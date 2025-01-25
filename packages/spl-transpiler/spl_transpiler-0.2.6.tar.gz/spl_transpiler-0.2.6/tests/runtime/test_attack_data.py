import logging
from pathlib import Path

import pytest
import yaml
from decorator import decorator
from pydantic import BaseModel, DirectoryPath
from pyspark.sql import SparkSession, DataFrame
from typing_extensions import Self

from spl_transpiler import convert_spl_to_pyspark
from spl_transpiler.macros import substitute_macros
from .utils import data_as_named_table, execute_transpiled_pyspark_code

log = logging.getLogger(__name__)


@decorator
def validate_suffix(path: Path, *, expected_suffix: str) -> callable:
    assert path.suffix == expected_suffix, (
        f"Expected {expected_suffix}, got {path.suffix}"
    )
    return path


class Cleanup(BaseModel):
    timestamps: list[str] = []
    sort_by: list[str] | None = None

    def apply(self, df: DataFrame) -> DataFrame:
        from pyspark.sql import functions as F

        df = df.withColumns(
            {col: F.to_timestamp(F.col(col)) for col in self.timestamps}
        )
        return df


class AttackDefinition(BaseModel):
    base_path: DirectoryPath
    input_file: Path
    output_file: Path
    query_file: Path

    cleanup: Cleanup = Cleanup()

    @classmethod
    def load_from_yaml(cls, path: Path) -> Self:
        with open(path, "r") as f:
            return cls(base_path=path.parent, **yaml.safe_load(f))

    def _load_data(self, path: Path) -> DataFrame:
        spark = SparkSession.builder.getOrCreate()
        spark.conf.set("spark.sql.caseSensitive", True)
        match path.suffix:
            case ".jsonl":
                df = spark.read.json(str(path.resolve()))
                df = df.select("result.*")
            case ".csv":
                df = (
                    spark.read.option("multiline", "true")
                    .option("quote", '"')
                    .option("header", "true")
                    .option("inferSchema", "true")
                    .option("escape", "\\")
                    .option("escape", '"')
                    .csv(str(path.resolve()))
                )
            case _:
                raise ValueError(f"Unknown extension: {path.suffix}")
        return df

    @property
    def input_data(self) -> DataFrame:
        return self._load_data(self.base_path / self.input_file)

    @property
    def output_data(self) -> DataFrame:
        return self._load_data(self.base_path / self.output_file)

    @property
    def query(self) -> str:
        return (self.base_path / self.query_file).read_text()


ATTACK_DATA_ROOT = Path(__file__).parent.parent / "sample_data" / "attack_data"
_sample_files = ATTACK_DATA_ROOT.glob("*.yaml")


# def _normalize_data(data):
#     match data:
#         case list():
#             return tuple(_normalize_data(item) for item in data)
#         case dict():
#             return tuple(sorted((k, _normalize_data(v)) for k, v in data.items()))
#         case _:
#             return data
#
#
# def _normalize_df(df: DataFrame):
#     return [_normalize_data(row.asDict(True)) for row in df.collect()]


def _normalize_df(df: DataFrame, cleanup: Cleanup):
    df = cleanup.apply(df)
    df = df.toPandas()

    df = df[list(sorted(df.columns))]
    df = df.sort_values(
        by=cleanup.sort_by if cleanup.sort_by is not None else list(df.columns)
    )
    df = df.reset_index(drop=True)

    return df


def _normalize_df_pair(actual, expected):
    for col, dtype in actual.dtypes.items():
        assert col in expected, (
            f"Column {col} found in actual output but missing from expected output"
        )
        try:
            expected[col] = expected[col].astype(dtype)
        except Exception as e:
            raise TypeError(
                f"Column {col} found in both actual and expected outputs, but values in expected output could not be type cast to match actual dtype {dtype}"
            ) from e

    return actual, expected


def _assert_df_equals(actual: DataFrame, expected: DataFrame, cleanup: Cleanup):
    from pandas.testing import assert_frame_equal

    actual = _normalize_df(actual, cleanup)
    expected = _normalize_df(expected, cleanup)

    actual, expected = _normalize_df_pair(actual, expected)

    assert_frame_equal(actual, expected, check_dtype=False)


# For each sample file, test that the transpiled query, when run against the input data, produces the output data
@pytest.mark.parametrize("attack_data_path", _sample_files, ids=lambda x: x.stem)
# @pytest.mark.parametrize("allow_runtime", [True, False], ids=lambda x: "runtime" if x else "standalone")
@pytest.mark.parametrize(
    "allow_runtime", [False], ids=lambda x: "runtime" if x else "standalone"
)
def test_transpiled_query(
    spark, macros, attack_data_path: Path, allow_runtime: bool
) -> None:
    attack_data = AttackDefinition.load_from_yaml(attack_data_path)
    query = substitute_macros(attack_data.query, macros)
    print(f"Query: {query}")
    transpiled_code = convert_spl_to_pyspark(query, allow_runtime=allow_runtime)
    # log.info(f"Transpiled code: {transpiled_code}")
    with data_as_named_table(spark, attack_data.input_data, "main"):
        query_results = execute_transpiled_pyspark_code(transpiled_code)
    _assert_df_equals(query_results, attack_data.output_data, attack_data.cleanup)
