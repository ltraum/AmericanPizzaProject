from __future__ import annotations
from pathlib import Path
from typing import List, Optional
import pandas as pd

# Always resolve the Excel from the repo's /data folder
DEFAULT_DATA_PATH = Path(__file__).parent.parent / "data" / "pizza_interviews.xlsx"

# Expose these so the app can import them
DEMO_COLS = [
    "participant_id",
    "age",
    "city_of_residence",
    "state_of_residence",
    "region_of_residence",
    "income",
    "pizza_consumption",
    "food_restrictions",
]

RESPONSE_COLS = ["q1_response", "q2_response", "q3_response", "q4_response", "q5_response"]

def load_pizza_df(data_path: Path | str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the dataset once (Excel). Does not mutate columns beyond basic cleanup.
    """
    df = pd.read_excel(data_path)
    # Quick sanity: ensure required columns exist
    missing = [c for c in DEMO_COLS + RESPONSE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in data file: {missing}")
    return df

def filter_by_demographics(
    df: pd.DataFrame,
    regions: Optional[List[str]] = None,
    ages: Optional[List[int]] = None,
    incomes: Optional[List[str]] = None,
    diets: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Filter by demographics. participant_id is preserved.
    """
    sub = df.copy()
    if regions:
        sub = sub[sub["region_of_residence"].isin(regions)]
    if ages:
        sub = sub[sub["age"].isin(ages)]
    if incomes:
        sub = sub[sub["income"].isin(incomes)]
    if diets:
        sub = sub[sub["food_restrictions"].isin(diets)]
    return sub

def build_text_df(df: pd.DataFrame, questions: List[str]) -> pd.DataFrame:
    """
    Concatenate any subset of response columns into a single 'text' field.
    Keeps all DEMO_COLS for traceability. Drops empty text rows.
    """
    valid_qs = [q for q in questions if q in RESPONSE_COLS]
    if not valid_qs:
        raise ValueError("No valid question columns selected.")

    text = (
        df[valid_qs]
        .apply(lambda row: " ".join([str(r) for r in row if pd.notnull(r) and str(r).strip() != ""]), axis=1)
        .str.strip()
    )

    out = df[DEMO_COLS].copy()
    out["text"] = text
    out = out[out["text"] != ""]
    return out

if __name__ == "__main__":
    # Mini sanity check if run directly
    d = load_pizza_df()
    print("Rows:", len(d), "Participants:", d["participant_id"].nunique())
    print("Demo preview:\n", d[DEMO_COLS].head(3))
