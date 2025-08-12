from __future__ import annotations
import os
import ast
from pathlib import Path

import streamlit as st
import pandas as pd

# Optional: auto-load private/.env for OPENAI_API_KEY
try:
    import dotenv
    dotenv.load_dotenv(dotenv_path=Path(__file__).parent.parent / "private" / ".env")
except Exception:
    pass

from data_processor import (
    load_pizza_df,
    filter_by_demographics,
    build_text_df,
    DEMO_COLS,
    RESPONSE_COLS,
)
from theme_analyzer import run_lloom_induction


# ------------------- Page setup -------------------
# ------------------- Page setup -------------------
st.set_page_config(page_title="LLooM Induction Explorer — Pizza", layout="centered")

st.title("LLooM Induction Explorer — Pizza Dataset")

st.markdown("""
Welcome to the **American Pizza Project Query Tool**!  
The American Pizza Project is aimed at capturing the diverse philosophies and regional differences in pizza appreciation across the United States. We conducted a series of pseudo–nationally representative interviews with participants from various backgrounds, focusing on their personal experiences and preferences related to pizza.

Each participant was asked to provide detailed responses (around 200 words) to the following prompts about their personal pizza preferences and experiences:

1. Describe a turning point in your life when your taste or appreciation for pizza changed. Share the story or explain why there hasn't been a change.  
2. Detail your ideal slice of pizza, including toppings, texture, sauce–cheese ratios, and your preferred regional style.  
3. Explain when and how you typically eat pizza in your life — on the go, with others, etc.  
4. Discuss the importance of pizza boxes and utensils to your pizza–eating experience.  
5. Share any experiences of being unable to eat pizza when you wanted to due to dietary reasons, cost, lack of availability, or other barriers.

Play with the tool to examine how well LLooM extracts themes from the data. Particularly interesting experimentation comes from choosing specific or broad seed theme terms and/or adjusting the scope of data analyzed (e.g., Q1 only vs. Q1+Q2 vs. Q1+Q2+Q3 vs. all prompts).
""")

# ------------------- Load data -------------------
DATA_PATH = Path(__file__).parent.parent / "data" / "pizza_interviews.xlsx"
df_full = load_pizza_df(DATA_PATH)


# ------------------- Helpers -------------------
def _to_list_like(val):
    """
    LLooM export 'highlights' can be a list, or sometimes a stringified list.
    Normalize to a short list of up to 3 items.
    """
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()][:3]
    s = str(val).strip()
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()][:3]
    except Exception:
        pass
    pieces = [p.strip(" -•\n\t") for p in s.split("\n") if p.strip()]
    return pieces[:3]


def _match_mask(score_df: pd.DataFrame, concept: str, threshold: float = 0.75) -> pd.Series:
    """
    Return a boolean Series (index-aligned to score_df) indicating whether each row matches the concept.
    Works for numeric (0..1) or binary (0/1) scoring columns.
    """
    if concept not in score_df.columns:
        return pd.Series([False] * len(score_df), index=score_df.index)
    s = score_df[concept]
    if pd.api.types.is_numeric_dtype(s):
        return s >= threshold
    return s == 1


# ------------------- Controls -------------------
with st.expander("Filters & Inputs", expanded=True):
    regions = st.multiselect(
        "Region (select at least two or leave blank to include all)",
        sorted(df_full["region_of_residence"].dropna().unique()),
    )
    seed = st.text_input("Optional one word theme seed to steer LLoom induction (examples: taste, packaging, family traditions)", value="")
    max_concepts = st.slider("Max themes per seed", min_value=1, max_value=10, value=5, step=1)

    selected_questions = st.multiselect(
        "Select prompt responses to include",
        RESPONSE_COLS,
        default=["q1_response"],
        help="Choose any combination of Q1–Q5; text will be concatenated (skipping blanks).",
    )

    run_btn = st.button("Run Induction", type="primary", use_container_width=True)

st.divider()


# ------------------- Run Induction -------------------
if run_btn:
    # 1) Region slice
    df_slice = filter_by_demographics(df_full, regions=regions, ages=None, incomes=None, diets=None)
    st.caption(f"Participants in slice: **{df_slice['participant_id'].nunique()}**  •  Rows: **{len(df_slice)}**")

    # 2) Build text df & set doc_id from participant_id
    try:
        df_text = build_text_df(df_slice, selected_questions)
        df_text["doc_id"] = df_text["participant_id"].astype(str)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    if df_text.empty:
        st.warning("No non-empty text after filters/questions. Try adjusting selections.")
        st.stop()

    st.caption(f"Text rows to induce on: **{len(df_text)}**")

    # 3) API key guard
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY not found. Put it in private/.env or export it in your shell.")
        st.stop()

    # 4) Run LLooM (gen_auto)
    with st.spinner("Running LLooM induction…"):
        score_df, export_df, concepts_dict = run_lloom_induction(
            df_text=df_text, seed=seed or None, max_concepts=max_concepts
        )

    # ---- TEMP DEBUG ----
    with st.expander("🔧 Debug (temporary)", expanded=False):
        st.write("score_df columns:", list(score_df.columns))
        st.write("score_df index name:", score_df.index.name)
        st.write("df_text columns:", list(df_text.columns))
        st.dataframe(score_df.head(3))
        st.download_button(
            "Download score_df CSV",
            data=score_df.to_csv(index=False).encode("utf-8"),
            file_name="lloom_score_debug.csv",
            mime="text/csv",
        )

    # Concept names list for selects
    names = export_df["concept"].tolist() if "concept" in export_df.columns else []

    # ------------------- Theme Cards -------------------
    st.subheader("Induced Themes")

    if "concept" not in export_df.columns:
        st.info("No concepts returned.")
    else:
        # Sort by # docs if available, else by prevalence
        if "n_matches" in export_df.columns:
            export_df = export_df.sort_values("n_matches", ascending=False)
        elif "prevalence" in export_df.columns:
            export_df = export_df.sort_values("prevalence", ascending=False)

        for _, row in export_df.iterrows():
            name = str(row.get("concept", "Theme")).strip()
            criteria = str(row.get("criteria", "")).strip()
            summary = str(row.get("summary", "")).strip()
            highlights = _to_list_like(row.get("highlights", []))
            prev = float(row.get("prevalence", 0.0))
            n_matches = int(row.get("n_matches", 0))

            card = st.container(border=True)
            with card:
                top = st.columns([0.75, 0.25])
                with top[0]:
                    st.markdown(f"### {name}")
                    if summary:
                        st.markdown(f"*{summary}*")
                with top[1]:
                    st.metric("Prevalence", f"{round(prev * 100, 1)}%")
                    st.metric("# Docs", f"{n_matches}")

                if highlights:
                    st.markdown("**Highlight quotes**")
                    for q in highlights:
                        st.markdown(f"> {q}")

                with st.expander("Details", expanded=False):
                    st.caption("Inclusion criteria")
                    st.write(criteria)

    # ------------------- Docs per Theme (bar chart) -------------------

    # Threshold matches from long-form score_df
    THRESH = 0.75
    score_df["is_match"] = pd.to_numeric(score_df["score"], errors="coerce") >= THRESH

    # Count unique docs per concept among matches
    doc_counts = (
        score_df.loc[score_df["is_match"]]
                .groupby("concept_name")["doc_id"]
                .nunique()
                .reset_index(name="n_matches")
                .sort_values("n_matches", ascending=False)
    )

    st.markdown("**Docs per Theme**")
    if len(doc_counts):
        st.bar_chart(doc_counts.set_index("concept_name")["n_matches"])
    else:
        st.info("No matched documents at the current threshold.")


    # ------------------- Regional Breakdown -------------------
    # ------------------- Regional Breakdown (per theme, no select box) -------------------
    st.subheader("Regional Breakdown")
    st.caption("For each theme: # of matching docs by region, plus share within region (prevalence).")

    # Map doc -> region (only rows with regions)
    region_map = df_text[["doc_id", "region_of_residence"]].dropna().copy()
    region_map["doc_id"] = region_map["doc_id"].astype(str)

    # All-region denominators: how many docs per region in the current slice
    totals_by_region = (
        region_map.groupby("region_of_residence")["doc_id"]
                .nunique()
                .reset_index(name="n_texts")
    )

    # Matched rows joined with regions
    matched = (
        score_df.loc[score_df["is_match"], ["doc_id", "concept_name"]]
                .assign(doc_id=lambda d: d["doc_id"].astype(str))
                .merge(region_map, on="doc_id", how="inner")
    )

    if matched.empty:
        st.info("No matches to display per region yet. Try a different seed, more questions, or lower the threshold.")
    else:
        # Choose the order of concepts from export_df if available, else alphabetical
        concept_order = export_df["concept"].tolist() if "concept" in export_df.columns else \
                        sorted(matched["concept_name"].unique())

        for cname in concept_order:
            sub = matched[matched["concept_name"] == cname]
            if sub.empty:
                continue

            # counts by region for this concept
            by_region = (
                sub.groupby("region_of_residence")["doc_id"]
                .nunique()
                .reset_index(name="n_matches")
                .merge(totals_by_region, on="region_of_residence", how="right")
                .fillna({"n_matches": 0})
            )

            # prevalence within region = n_matches / n_texts
            by_region["prevalence"] = (by_region["n_matches"] / by_region["n_texts"]).replace([float("inf")], 0.0)
            by_region = by_region.sort_values("n_matches", ascending=False)

            st.markdown(f"**{cname}**")
            st.bar_chart(by_region.set_index("region_of_residence")["n_matches"])
            by_region["prevalence (%)"] = (by_region["prevalence"] * 100).round(1)
            st.dataframe(
                by_region[["region_of_residence", "n_matches", "n_texts", "prevalence (%)"]],
                use_container_width=True, hide_index=True,
            )
            st.divider()


