from functools import cache

from pyspark.sql import DataFrame, functions as F, GroupedData


def groupByMaybeExploded(self: DataFrame, by: list) -> GroupedData:
    by_strings = [c for c in by if isinstance(c, str)]
    return self.withColumns(
        {
            c: F.explode(c)
            for c, tp in self.dtypes
            if c in by_strings and str(tp).lower().startswith("array<")
        }
    ).groupBy(by)


@cache
def install_monkeypatches():
    DataFrame._spltranspiler__groupByMaybeExploded = groupByMaybeExploded
