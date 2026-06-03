class PandasOperators:
    def __init__(self, df):
        self.df = df

    def apply(self, col, value):
        if isinstance(value, list):
            return self.df[col].isin(value)

        if isinstance(value, tuple):
            op, val = value
            op = op.lower()

            if op == "=": return self.df[col] == val
            if op == "!=": return self.df[col] != val
            if op == ">": return self.df[col] > val
            if op == "<": return self.df[col] < val
            if op == ">=": return self.df[col] >= val
            if op == "<=": return self.df[col] <= val
            if op == "in": return self.df[col].isin(val)
            if op == "notin": return ~self.df[col].isin(val)
            if op == "between": return (self.df[col] >= val[0]) & (self.df[col] <= val[1])
            if op == "like": return self.df[col].astype(str).str.contains(val, case=False, na=False)
            if op == "notlike": return ~self.df[col].astype(str).str.contains(val, case=False, na=False)
            if op == "startswith": return self.df[col].astype(str).str.startswith(val, na=False)
            if op == "endswith": return self.df[col].astype(str).str.endswith(val, na=False)
            if op == "isnull": return self.df[col].isnull()
            if op == "isempty": return self.df[col].astype(str).str.strip() == ""

        return self.df[col] == value


class SQLOperators:

    def apply(self, col, value):
        if isinstance(value, list):
            vals = ", ".join([f"'{v}'" for v in value])
            return f"{col} IN ({vals})"

        if isinstance(value, tuple):
            op, val = value
            op = op.lower()

            if op == "=": return f"{col} = '{val}'"
            if op == "!=": return f"{col} != '{val}'"
            if op == ">": return f"{col} > {val}"
            if op == "<": return f"{col} < {val}"
            if op == ">=": return f"{col} >= {val}"
            if op == "<=": return f"{col} <= {val}"
            if op == "in": return f"{col} IN ({','.join(map(str,val))})"
            if op == "notin": return f"{col} NOT IN ({','.join(map(str,val))})"
            if op == "between": return f"{col} BETWEEN {val[0]} AND {val[1]}"
            if op == "like": return f"{col} LIKE '%{val}%'"
            if op == "notlike": return f"{col} NOT LIKE '%{val}%'"
            if op == "startswith": return f"{col} LIKE '{val}%'"
            if op == "endswith": return f"{col} LIKE '%{val}'"
            if op == "isnull": return f"{col} IS NULL"
            if op == "isempty": return f"({col} = '' OR {col} IS NULL)"

        return f"{col} = '{value}'"
