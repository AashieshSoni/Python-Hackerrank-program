import pandas as pd
from functools import singledispatchmethod

class CSVFilter:
    def __init__(self, input_file: str, delimiter: str = ","):
        self.input_file = input_file
        self.delimiter = delimiter
        self.df = pd.read_csv(input_file, delimiter=delimiter)

    @singledispatchmethod
    def filter_and_save(self, args, output_file: str):
        """Default method (unsupported types)."""
        raise NotImplementedError("Unsupported filter type")

    @filter_and_save.register
    def _(self, arg: tuple, output_file: str):
        """
        Single or two arguments:
        - (col, value)
        - (col1, value1, col2, value2)
        """
        if len(arg) == 2:
            col, value = arg
            filtered = self.df[self.df[col] == value]
        elif len(arg) == 4:
            col1, value1, col2, value2 = arg
            filtered = self.df[(self.df[col1] == value1) & (self.df[col2] == value2)]
        else:
            raise ValueError("Tuple must have 2 or 4 elements")
        
        filtered.to_csv(output_file, sep=self.delimiter, index=False)

    @filter_and_save.register
    def _(self, arg: dict, output_file: str):
        """
        Multiple arguments:
        - {col: value, col2: value2, ...}
        - value can be:
            scalar → equality
            list → IN filter
            tuple("operator", value) → condition
        """
        filtered = self.df.copy()

        for col, value in arg.items():
            if isinstance(value, list):  
                # IN filter
                filtered = filtered[filtered[col].isin(value)]

            elif isinstance(value, tuple) and len(value) == 2:
                # Conditional operators
                op, val = value

                # Numeric comparisons
                if op == ">":
                    filtered = filtered[filtered[col] > val]
                elif op == "<":
                    filtered = filtered[filtered[col] < val]
                elif op == ">=":
                    filtered = filtered[filtered[col] >= val]
                elif op == "<=":
                    filtered = filtered[filtered[col] <= val]
                elif op == "!=":
                    filtered = filtered[filtered[col] != val]
                elif op.lower() == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                    filtered = filtered[(filtered[col] >= val[0]) & (filtered[col] <= val[1])]

                # String pattern matching
                elif op.lower() == "like":
                    filtered = filtered[filtered[col].astype(str).str.contains(val, case=False, na=False)]
                elif op.lower() == "notlike":
                    filtered = filtered[~filtered[col].astype(str).str.contains(val, case=False, na=False)]
                elif op.lower() == "startswith":
                    filtered = filtered[filtered[col].astype(str).str.startswith(val, na=False)]
                elif op.lower() == "endswith":
                    filtered = filtered[filtered[col].astype(str).str.endswith(val, na=False)]

                else:
                    raise ValueError(f"Unsupported operator/value: {op}, {val}")

            else:
                # Equality filter
                filtered = filtered[filtered[col] == value]
        
        filtered.to_csv(output_file, sep=self.delimiter, index=False)


# ---------------- USAGE EXAMPLES ----------------

csv_obj = CSVFilter("input.csv", delimiter="|")

# Case 1: LIKE filter on Name
csv_obj.filter_and_save({"Name": ("like", "Ro")}, "output_like.csv")

# Case 2: Name starts with 'A' and Year = 2025
csv_obj.filter_and_save({"Name": ("startswith", "A"), "Year": 2025}, "output_start.csv")

# Case 3: Country in [India, USA], Status != Inactive, Name not containing 'a'
csv_obj.filter_and_save(
    {"Country": ["India", "USA"], "Status": ("!=", "Inactive"), "Name": ("notlike", "a")},
    "output_complex.csv"
)
