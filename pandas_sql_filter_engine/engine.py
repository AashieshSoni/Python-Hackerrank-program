import pandas as pd
from .operators import PandasOperators, SQLOperators

class QueryEngine:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.pd_ops = PandasOperators(df)
        self.sql_ops = SQLOperators()

    def build_pd_mask(self, condition):
        if "and" in condition:
            masks = [self.build_pd_mask(c) for c in condition["and"]]
            return pd.concat(masks, axis=1).all(axis=1)

        if "or" in condition:
            masks = [self.build_pd_mask(c) for c in condition["or"]]
            return pd.concat(masks, axis=1).any(axis=1)

        masks = []
        for col, value in condition.items():
            masks.append(self.pd_ops.apply(col, value))

        return pd.concat(masks, axis=1).all(axis=1)

    def filter(self, condition):
        return self.df[self.build_pd_mask(condition)]

    def build_sql(self, condition):
        if "and" in condition:
            return "(" + " AND ".join([self.build_sql(c) for c in condition["and"]]) + ")"

        if "or" in condition:
            return "(" + " OR ".join([self.build_sql(c) for c in condition["or"]]) + ")"

        clauses = []
        for col, value in condition.items():
            clauses.append(self.sql_ops.apply(col, value))

        return " AND ".join(clauses)

    def build_select_query(self, table_name, condition=None, columns=None):
        col_part = "*" if columns is None else ", ".join(columns)
        query = f"SELECT {col_part} FROM {table_name}"

        if condition:
            query += f" WHERE {self.build_sql(condition)}"

        return query
