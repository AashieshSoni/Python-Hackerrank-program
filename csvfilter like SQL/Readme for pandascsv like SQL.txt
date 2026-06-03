 a Python class using pandas that:  
Takes a CSV (with a custom delimiter) as input.

Generates a filtered CSV (with delimiter) as output.

Uses function overloading (via @singledispatchmethod or default args) to filter rows based on:

Single argument (one condition on one column).

Two arguments (two conditions).

Multiple arguments (flexible number of conditions).

Here’s a clean implementation 👇

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
        Multiple arguments: pass as dictionary {col: value, col2: value2, ...}
        """
        filtered = self.df.copy()
        for col, value in arg.items():
            filtered = filtered[filtered[col] == value]
        
        filtered.to_csv(output_file, sep=self.delimiter, index=False)


# ---------------- USAGE EXAMPLES ----------------

# Initialize
csv_obj = CSVFilter("input.csv", delimiter="|")

# 1. Single argument filter
csv_obj.filter_and_save(("Country", "India"), "output_single.csv")

# 2. Two arguments filter
csv_obj.filter_and_save(("Country", "India", "Year", 2025), "output_two.csv")

# 3. Multiple arguments filter
csv_obj.filter_and_save({"Country": "India", "Year": 2025, "Status": "Active"}, "output_multi.csv")
✅ Supports function overloading with @singledispatchmethod.
✅ Handles single, double, or multiple column-value filters.
✅ Works with any delimiter (e.g., "|", ";", "\t").
✅ Writes filtered CSV to output file.

Would you like me to also add LIKE (partial match) support for string columns (e.g., "Name" contains 'sh')?

You said:
share "input.csv" sample
ChatGPT said:
Here’s a small sample input.csv file with | (pipe) as delimiter so you can test the class code I shared earlier:

ID|Name|Country|Year|Status
1|Aashiesh|India|2025|Active
2|Rohan|India|2024|Inactive
3|Emma|USA|2025|Active
4|Liu|China|2025|Inactive
5|Maria|India|2025|Active
6|John|USA|2023|Active
7|Sofia|Spain|2025|Inactive
8|Raj|India|2025|Inactive
Example filtering using this file:
Single argument

csv_obj.filter_and_save(("Country", "India"), "output_single.csv")
➡️ Keeps only rows where Country = India.

Two arguments

csv_obj.filter_and_save(("Country", "India", "Year", 2025), "output_two.csv")
➡️ Keeps rows where Country = India AND Year = 2025.

Multiple arguments

csv_obj.filter_and_save({"Country": "India", "Year": 2025, "Status": "Active"}, "output_multi.csv")
➡️ Keeps rows where Country = India AND Year = 2025 AND Status = Active.

Do you also want me to show you the resulting output CSVs for these three cases with this sample data?

You said:
few columns like Country may wanted to pass multiple values in agrument , include other argument like Year as 2025 and name is Rohan
ChatGPT said:
Perfect point 👌 — you want to extend the filtering logic so that:

Some columns can accept multiple values (e.g., Country can be ["India", "USA"]).

Other filters can still be exact matches (e.g., Year=2025, Name="Rohan").

I’ll enhance the multiple-arguments (dict) filter to handle list values as "IN filter".

Here’s the updated class code:

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
        Multiple arguments: pass as dictionary 
        - {col: value, col2: value2, ...}
        - if value is list, it will apply 'IN' filter
        """
        filtered = self.df.copy()
        for col, value in arg.items():
            if isinstance(value, list):  # multiple values
                filtered = filtered[filtered[col].isin(value)]
            else:  # single value
                filtered = filtered[filtered[col] == value]
        
        filtered.to_csv(output_file, sep=self.delimiter, index=False)


# ---------------- USAGE EXAMPLES ----------------

# Initialize
csv_obj = CSVFilter("input.csv", delimiter="|")

# Case 1: Multiple Countries, Year = 2025, Name = Rohan
csv_obj.filter_and_save(
    {"Country": ["India", "USA"], "Year": 2025, "Name": "Rohan"},
    "output_multi_country.csv"
)
With the earlier input.csv:
ID|Name|Country|Year|Status
1|Aashiesh|India|2025|Active
2|Rohan|India|2024|Inactive
3|Emma|USA|2025|Active
4|Liu|China|2025|Inactive
5|Maria|India|2025|Active
6|John|USA|2023|Active
7|Sofia|Spain|2025|Inactive
8|Raj|India|2025|Inactive
👉 The above filter (Country in ["India","USA"] AND Year=2025 AND Name=Rohan)
will return NO rows, because Rohan is from India but in 2024.

If you change it to:

{"Country": ["India", "USA"], "Name": "Rohan"}
➡️ It will pick row 2 (Rohan | India | 2024 | Inactive).

Would you like me to also extend this so you can pass ranges (e.g., Year >= 2024) instead of just equality?

You said:
yes
ChatGPT said:
Great 👍 — let’s extend the class so it can handle:

Equality filters (same as before).

Multiple values (IN filter) via lists.

Range/condition filters via tuples like:

(">= ", 2024) → Year ≥ 2024

("<", 2025) → Year < 2025

("between", (2023, 2025)) → Year between 2023 and 2025

Updated Code
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
                else:
                    raise ValueError(f"Unsupported operator/value: {op}, {val}")

            else:
                # Equality filter
                filtered = filtered[filtered[col] == value]
        
        filtered.to_csv(output_file, sep=self.delimiter, index=False)


# ---------------- USAGE EXAMPLES ----------------

# Initialize with pipe-delimited CSV
csv_obj = CSVFilter("input.csv", delimiter="|")

# Case 1: Country in multiple values, Year >= 2024, Name is Rohan
csv_obj.filter_and_save(
    {"Country": ["India", "USA"], "Year": (">=", 2024), "Name": "Rohan"},
    "output_complex.csv"
)

# Case 2: Year between 2023 and 2025, Status != Inactive
csv_obj.filter_and_save(
    {"Year": ("between", (2023, 2025)), "Status": ("!=", "Inactive")},
    "output_between.csv"
)
Example with your input.csv
ID|Name|Country|Year|Status
1|Aashiesh|India|2025|Active
2|Rohan|India|2024|Inactive
3|Emma|USA|2025|Active
4|Liu|China|2025|Inactive
5|Maria|India|2025|Active
6|John|USA|2023|Active
7|Sofia|Spain|2025|Inactive
8|Raj|India|2025|Inactive
Query:

{"Country": ["India", "USA"], "Year": (">=", 2024), "Name": "Rohan"}
→ Returns Row 2 (Rohan | India | 2024 | Inactive) ✅

Query:

{"Year": ("between", (2023, 2025)), "Status": ("!=", "Inactive")}
→ Returns rows where Year is 2023–2025 and Status is Active (Rows 1, 3, 5, 6).

Do you also want me to extend this so filters can use partial string matching (like SQL LIKE '%text%')?

You said:
yes
ChatGPT said:
Perfect 👍 now we’ll add string pattern matching support like SQL LIKE.
That means in filters, you’ll be able to pass conditions like:

("like", "Ro") → contains "Ro"

("startswith", "A") → starts with "A"

("endswith", "sh") → ends with "sh"

("notlike", "an") → does not contain "an"

Final Enhanced Class
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
Example Results with input.csv
ID|Name|Country|Year|Status
1|Aashiesh|India|2025|Active
2|Rohan|India|2024|Inactive
3|Emma|USA|2025|Active
4|Liu|China|2025|Inactive
5|Maria|India|2025|Active
6|John|USA|2023|Active
7|Sofia|Spain|2025|Inactive
8|Raj|India|2025|Inactive
{"Name": ("like", "Ro")} → Row 2 (Rohan).

{"Name": ("startswith", "A"), "Year": 2025} → Row 1 (Aashiesh).

{"Country": ["India","USA"], "Status": ("!=", "Inactive"), "Name": ("notlike", "a")}
→ Row 6 (John | USA | 2023 | Active).

Do you want me to also add support for OR conditions (e.g., Name contains 'Ro' OR Status=Active), or should we keep it strictly AND logic between filters?

You said:
yes
ChatGPT said:
Got it ✅ — currently all filters are applied with AND logic (all conditions must be true).
Now we’ll extend the design so you can also specify OR conditions like SQL:

filters_and={...} → all conditions must match (default).

filters_or=[{...}, {...}] → at least one condition group must match.

This way, we can mix AND within a group, and combine groups with OR.

Final Enhanced Class (AND + OR support)
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
    def _(self, arg: tuple, output_file: str):
        """Tuple overload → single or two conditions"""
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
        """Dict overload → AND logic across filters"""
        filtered = self._apply_filters(self.df, arg)
        filtered.to_csv(output_file, sep=self.delimiter, index=False)

    @filter_and_save.register
    def _(self, arg: list, output_file: str):
        """
        List of dicts → OR logic
        Example:
            [
              {"Country": "India", "Year": 2025},
              {"Name": ("like", "Ro")}
            ]
        """
        frames = []
        for condition_group in arg:
            frames.append(self._apply_filters(self.df, condition_group))
        # Union of all matches
        filtered = pd.concat(frames).drop_duplicates()
        filtered.to_csv(output_file, sep=self.delimiter, index=False)

    def _apply_filters(self, df, filters: dict):
        """Apply AND filters to DataFrame based on rules"""
        filtered = df.copy()
        for col, value in filters.items():
            if isinstance(value, list):
                filtered = filtered[filtered[col].isin(value)]

            elif isinstance(value, tuple) and len(value) == 2:
                op, val = value
                if op == ">":   filtered = filtered[filtered[col] > val]
                elif op == "<": filtered = filtered[filtered[col] < val]
                elif op == ">=": filtered = filtered[filtered[col] >= val]
                elif op == "<=": filtered = filtered[filtered[col] <= val]
                elif op == "!=": filtered = filtered[filtered[col] != val]
                elif op.lower() == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                    filtered = filtered[(filtered[col] >= val[0]) & (filtered[col] <= val[1])]
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
                filtered = filtered[filtered[col] == value]
        return filtered
Example Usage with input.csv
csv_obj = CSVFilter("input.csv", delimiter="|")

# 1) AND Example: Country = India AND Year = 2025
csv_obj.filter_and_save({"Country": "India", "Year": 2025}, "output_and.csv")

# 2) OR Example: (Country = India AND Year = 2025) OR (Name LIKE 'Ro')
csv_obj.filter_and_save(
    [
        {"Country": "India", "Year": 2025},
        {"Name": ("like", "Ro")}
    ],
    "output_or.csv"
)

# 3) Mixed: OR groups with advanced conditions
csv_obj.filter_and_save(
    [
        {"Country": ["India", "USA"], "Status": ("!=", "Inactive")},
        {"Year": ("between", (2023, 2024)), "Name": ("startswith", "R")}
    ],
    "output_or_complex.csv"
)
With your sample input.csv:
ID|Name|Country|Year|Status
1|Aashiesh|India|2025|Active
2|Rohan|India|2024|Inactive
3|Emma|USA|2025|Active
4|Liu|China|2025|Inactive
5|Maria|India|2025|Active
6|John|USA|2023|Active
7|Sofia|Spain|2025|Inactive
8|Raj|India|2025|Inactive
AND Example ({"Country":"India","Year":2025}) → Rows 1, 5, 8

OR Example:

Group1 → Country=India & Year=2025 → Rows 1, 5, 8

Group2 → Name LIKE "Ro" → Row 2

Combined → Rows 1,2,5,8

👉 Now you can choose strict AND filtering or OR filtering across groups.

Would you like me to also support nested OR/AND combinations (like ((A AND B) OR (C AND D)) AND E) — i.e. fully SQL-like logic — or keep it at top-level OR groups with AND inside?

You said:
yes
ChatGPT said:
Perfect 🚀 You want nested AND/OR logic — like SQL conditions with parentheses:

👉 Example:

((Country = "India" AND Year = 2025) OR (Name LIKE "Ro")) AND Status = "Active"
To support this, we can represent filters as a tree of conditions using dictionaries:

"and": [ ... ] → all must be true.

"or": [ ... ] → at least one must be true.

Direct dict → simple column filters.

🔥 Fully SQL-like Nested Filters Class
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
✅ Example Usage with input.csv
csv_obj = CSVFilter("input.csv", delimiter="|")

# Example 1: Simple nested AND/OR
condition = {
    "and": [
        {
            "or": [
                {"Country": "India", "Year": 2025},
                {"Name": ("like", "Ro")}
            ]
        },
        {"Status": "Active"}
    ]
}

csv_obj.filter_and_save(condition, "output_nested.csv")
Example Walkthrough
Using your input.csv:

ID|Name|Country|Year|Status
1|Aashiesh|India|2025|Active
2|Rohan|India|2024|Inactive
3|Emma|USA|2025|Active
4|Liu|China|2025|Inactive
5|Maria|India|2025|Active
6|John|USA|2023|Active
7|Sofia|Spain|2025|Inactive
8|Raj|India|2025|Inactive
Condition:

((Country="India" AND Year=2025) OR (Name LIKE "Ro")) AND Status="Active"
Group1: (Country=India AND Year=2025) → Rows 1, 5, 8

Group2: (Name LIKE "Ro") → Row 2

OR of Group1 + Group2 → Rows 1,2,5,8

AND Status=Active → Rows 1,5 ✅

👉 Final Output →

1|Aashiesh|India|2025|Active
5|Maria|India|2025|Active
Would you like me to also add an option to export the generated filter condition as SQL WHERE clause (so you can reuse the same filters in a database query)?

You said:
yes
ChatGPT said:
🔥 Awesome — let’s add the ability to export the same nested filter condition into a SQL WHERE clause.
That way, you can reuse the same condition in Pandas and in SQL queries.

Enhanced Class with to_sql_where()
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

    # ---------- FILTER BUILDERS ----------
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

    # ---------- SQL WHERE BUILDER ----------
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
                    vals = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                    clauses.append(f"{col} IN ({vals})")

                elif isinstance(value, tuple) and len(value) == 2:
                    op, val = value
                    if op.lower() == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                        low, high = val
                        low = f"'{low}'" if isinstance(low, str) else low
                        high = f"'{high}'" if isinstance(high, str) else high
                        clauses.append(f"{col} BETWEEN {low} AND {high}")
                    elif op.lower() == "like":
                        clauses.append(f"{col} LIKE '%{val}%'")
                    elif op.lower() == "notlike":
                        clauses.append(f"{col} NOT LIKE '%{val}%'")
                    elif op.lower() == "startswith":
                        clauses.append(f"{col} LIKE '{val}%'")
                    elif op.lower() == "endswith":
                        clauses.append(f"{col} LIKE '%{val}'")
                    else:
                        val = f"'{val}'" if isinstance(val, str) else val
                        clauses.append(f"{col} {op} {val}")

                else:
                    val = f"'{value}'" if isinstance(value, str) else value
                    clauses.append(f"{col} = {val}")
            return " AND ".join(clauses)
✅ Example Usage
csv_obj = CSVFilter("input.csv", delimiter="|")

# Complex nested condition
condition = {
    "and": [
        {
            "or": [
                {"Country": "India", "Year": 2025},
                {"Name": ("like", "Ro")}
            ]
        },
        {"Status": "Active"}
    ]
}

# Apply in Pandas and export CSV
csv_obj.filter_and_save(condition, "output_nested.csv")

# Convert to SQL WHERE clause
sql_where = csv_obj.to_sql_where(condition)
print("SQL WHERE clause:")
print(sql_where)
🔎 Output SQL WHERE clause
((Country = 'India' AND Year = 2025) OR (Name LIKE '%Ro%')) AND (Status = 'Active')
👉 Now you can:

Use the same condition dict for both Pandas filtering and SQL queries.

Automatically generate valid WHERE clauses, including IN, BETWEEN, LIKE, etc.

Do you want me to also add an option so that the class can generate the full SQL SELECT query (like SELECT * FROM table WHERE ...) if you provide the table name?

You said:
create separate function for each clauses
ChatGPT said:
Perfect 👍 — you want to modularize the SQL generation by creating a separate function for each clause type (=, IN, BETWEEN, LIKE, etc.) so it’s cleaner and extendable.

Here’s the refactored version:

🐍 Python Code

class supports:

=, !=, >, <, >=, <=
IN, NOT IN
BETWEEN
LIKE, NOT LIKE, STARTSWITH, ENDSWITH
IS NULL, IS EMPTY