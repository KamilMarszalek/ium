import ast
import json

import pandas as pd


def parse_amenities_cell(x):
    if pd.isna(x):
        return []
    if isinstance(x, list):
        return [str(a).strip() for a in x]
    s = str(x).strip()
    if not s:
        return []
    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return [str(a).strip() for a in obj]
    except Exception:
        pass
    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, list):
            return [str(a).strip() for a in obj]
    except Exception:
        pass
    s = s.strip("{}[]")
    return [t.strip().strip('"').strip("'") for t in s.split(",") if t.strip()]
