'''
Fully SQL-like Nested Filters Class
'''
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
        """Dict overload: nested AND/OR supported"""
        mask = self._build_condition(self.df, arg)
        filtered = self.df[mask]
        filtered.to_csv(output_file, sep=self.delimiter, index=False)

    @filter_and_save.register
    def _(self, arg: tuple, output_file: str):
        """Tuple overload → simple conditions"""
        if len(arg) == 2:
            col, value = arg
            filtered = self.df[self.df[col] == value]
        elif len(arg) == 4:
            col1, value1, col2, value2 = arg
            filtered = self.df[(self.df[col1] == value1) & (self.df[col2] == value2)]
        else:
            raise ValueError("Tuple must have 2 or 4 elements")
        filtered.to_csv(output_file, sep=self.delimiter, index=False)

    def _apply_simple_filter(self, df, col, value):
        """Apply a simple column filter and return mask"""
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
        """
        Recursively build boolean mask for nested conditions
        condition can be:
        - {"and": [sub1, sub2, ...]}
        - {"or": [sub1, sub2, ...]}
        - {"Column": value}
        """
        if "and" in condition:
            masks = [self._build_condition(df, sub) for sub in condition["and"]]
            return pd.concat(masks, axis=1).all(axis=1)
        elif "or" in condition:
            masks = [self._build_condition(df, sub) for sub in condition["or"]]
            return pd.concat(masks, axis=1).any(axis=1)
        else:
            # simple filters
            masks = []
            for col, value in condition.items():
                masks.append(self._apply_simple_filter(df, col, value))
            return pd.concat(masks, axis=1).all(axis=1)