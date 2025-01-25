use crate::commands::cmd_rename::spl::RenameCommand;
use crate::pyspark::transpiler::{PipelineTransformState, PipelineTransformer};
use crate::spl::ast;
use anyhow::{bail, Result};

impl PipelineTransformer for RenameCommand {
    fn transform_standalone(
        &self,
        state: PipelineTransformState,
    ) -> anyhow::Result<PipelineTransformState> {
        let mut df = state.df.clone().unwrap_or_default();

        let renames = self
            .alias
            .iter()
            .cloned()
            .map(|alias| {
                let old_name = match *alias.expr {
                    ast::Expr::Leaf(ast::LeafExpr::Constant(ast::Constant::Field(ast::Field(
                        name,
                    )))) => name,
                    ast::Expr::Leaf(ast::LeafExpr::Constant(ast::Constant::Wildcard(
                        ast::Wildcard(_name),
                    ))) => bail!("UNIMPLEMENTED: Wildcard renaming is not supported yet"),
                    _ => bail!("Unsupported rename source: {:?}", alias),
                };
                Ok((old_name, alias.name.clone()))
            })
            .collect::<Result<Vec<_>>>()?;
        df = df.with_columns_renamed(renames);

        Ok(state.with_df(df))
    }
}

#[cfg(test)]
mod tests {
    use crate::pyspark::utils::test::generates;
    use rstest::rstest;

    #[rstest]
    fn test_rename_1() {
        let query = r#"index=main | rename foo as bar, x as y"#;

        generates(
            query,
            r#"
spark.table("main").withColumnsRenamed({"foo": "bar", "x": "y"})
            "#,
        )
    }
}
