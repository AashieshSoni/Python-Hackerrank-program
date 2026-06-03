import pandas as pd
from functools import singledispatchmethod

class CSVFilter:
    def __init__(self, input_file: str, delimiter: str = ","):
        self.input_file = input_file
        self.delimiter = delimiter
        self.df = pd.read_csv(input_file, delimiter=delimiter)

    @singledispatchmethod
    def filter_and_save(self, args, output_file: str):
        raise NotImplementedError("Unsupported filter type")

    @filter_and_save.register
    def _(self, arg: dict, output_file: str):
        mask = self._build_condition(self.df, arg)
        filtered = self.df[mask]
        filtered.to_csv(output_file, sep=self.delimiter, index=False)

    @filter_and_save.register
    def _(self, arg: tuple, output_file: str):
        if len(arg) == 2:
            col, value = arg
            filtered = self.df[self.df[col] == value]
        elif len(arg) == 4:
            col1, value1, col2, value2 = arg
            filtered = self.df[(self.df[col1] == value1) & (self.df[col2] == value2)]
        else:
            raise ValueError("Tuple must have 2 or 4 elements")
        filtered.to_csv(output_file, sep=self.delimiter, index=False)

    # ---------- Pandas Filter ----------
    def _apply_simple_filter(self, df, col, value):
        if isinstance(value, list):
            return df[col].isin(value)

        elif isinstance(value, tuple) and len(value) == 2:
            op, val = value
            if op == ">": return df[col] > val
            if op == "<": return df[col] < val
            if op == ">=": return df[col] >= val
            if op == "<=": return df[col] <= val
            if op == "!=": return df[col] != val
            if op.lower() == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                return (df[col] >= val[0]) & (df[col] <= val[1])
            if op.lower() == "like":
                return df[col].astype(str).str.contains(val, case=False, na=False)
            if op.lower() == "notlike":
                return ~df[col].astype(str).str.contains(val, case=False, na=False)
            if op.lower() == "startswith":
                return df[col].astype(str).str.startswith(val, na=False)
            if op.lower() == "endswith":
                return df[col].astype(str).str.endswith(val, na=False)
            raise ValueError(f"Unsupported operator: {op}")

        else:
            return df[col] == value

    def _build_condition(self, df, condition):
        if "and" in condition:
            masks = [self._build_condition(df, sub) for sub in condition["and"]]
            return pd.concat(masks, axis=1).all(axis=1)
        elif "or" in condition:
            masks = [self._build_condition(df, sub) for sub in condition["or"]]
            return pd.concat(masks, axis=1).any(axis=1)
        else:
            masks = []
            for col, value in condition.items():
                masks.append(self._apply_simple_filter(df, col, value))
            return pd.concat(masks, axis=1).all(axis=1)

    # ---------- SQL WHERE Builders ----------
    def _sql_equal(self, col, val):
        return f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"

    def _sql_in(self, col, values):
        vals = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values])
        return f"{col} IN ({vals})"

    def _sql_between(self, col, val):
        low, high = val
        low = f"'{low}'" if isinstance(low, str) else low
        high = f"'{high}'" if isinstance(high, str) else high
        return f"{col} BETWEEN {low} AND {high}"

    def _sql_like(self, col, val):
        return f"{col} LIKE '%{val}%'"

    def _sql_notlike(self, col, val):
        return f"{col} NOT LIKE '%{val}%'"

    def _sql_startswith(self, col, val):
        return f"{col} LIKE '{val}%'"

    def _sql_endswith(self, col, val):
        return f"{col} LIKE '%{val}'"

    def _sql_comparison(self, col, op, val):
        val = f"'{val}'" if isinstance(val, str) else val
        return f"{col} {op} {val}"

    def to_sql_where(self, condition):
        """Convert nested condition dict to SQL WHERE clause string"""
        if "and" in condition:
            return "(" + " AND ".join([self.to_sql_where(sub) for sub in condition["and"]]) + ")"
        elif "or" in condition:
            return "(" + " OR ".join([self.to_sql_where(sub) for sub in condition["or"]]) + ")"
        else:
            clauses = []
            for col, value in condition.items():
                if isinstance(value, list):
                    clauses.append(self._sql_in(col, value))

                elif isinstance(value, tuple) and len(value) == 2:
                    op, val = value
                    if op.lower() == "between":
                        clauses.append(self._sql_between(col, val))
                    elif op.lower() == "like":
                        clauses.append(self._sql_like(col, val))
                    elif op.lower() == "notlike":
                        clauses.append(self._sql_notlike(col, val))
                    elif op.lower() == "startswith":
                        clauses.append(self._sql_startswith(col, val))
                    elif op.lower() == "endswith":
                        clauses.append(self._sql_endswith(col, val))
                    else:
                        clauses.append(self._sql_comparison(col, op, val))

                else:
                    clauses.append(self._sql_equal(col, value))

            return " AND ".join(clauses)