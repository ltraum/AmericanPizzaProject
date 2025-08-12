from __future__ import annotations
from typing import Optional, Tuple
import pandas as pd

# Import LLooM Workbench
try:
    import text_lloom.workbench as wb
    _HAS_LLOOM = True
except Exception:
    _HAS_LLOOM = False


def _assert_lloom():
    if not _HAS_LLOOM:
        raise RuntimeError(
            "LLooM is not available. Install with `pip install text_lloom` and set OPENAI_API_KEY."
        )


def _build_export_from_long(
    score_df: pd.DataFrame,
    concepts_dict: dict,
    doc_id_col: str = "doc_id",
    threshold: float = 0.75,
) -> pd.DataFrame:
    """
    Build a summary (export_df) from LLooM's LONG form score_df without calling vis()/export_df().
    Columns returned:
      - concept (name)
      - criteria (prompt used for scoring)
      - summary (if present in concept dict)
      - prevalence (n_matches / total_docs in current slice)
      - n_matches (unique docs matching at threshold)
      - highlights (up to 3 strings from score_df['highlight'])
    """
    # Number of unique docs in this slice
    n_docs = score_df[doc_id_col].astype(str).nunique()

    rows = []
    for cid, c in concepts_dict.items():
        concept_name = c.get("name") or c.get("concept") or str(cid)
        prompt = c.get("prompt") or ""
        concept_summary = c.get("summary")

        sub = score_df.loc[score_df["concept_id"] == cid].copy()
        sub["is_match"] = pd.to_numeric(sub["score"], errors="coerce") >= threshold

        n_matches = sub.loc[sub["is_match"], doc_id_col].astype(str).nunique()
        prevalence = (n_matches / n_docs) if n_docs else 0.0

        # Up to 3 highlights from matching rows
        highs = (
            sub.loc[sub["is_match"], "highlight"]
               .dropna()
               .astype(str)
               .head(3)
               .tolist()
        )

        rows.append(
            {
                "concept": concept_name,
                "criteria": prompt,
                "summary": concept_summary,
                "prevalence": prevalence,
                "n_matches": int(n_matches),
                "highlights": highs,
            }
        )

    export_df = pd.DataFrame(rows).sort_values("n_matches", ascending=False)
    return export_df


async def run_lloom_induction_async(
    df_text: pd.DataFrame,
    seed: Optional[str] = None,
    max_concepts: int = 3,
    threshold: float = 0.75,
) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Run LLooM induction on a tidy dataframe with columns:
      - 'text' (string)
      - 'doc_id' (string; unique per row)
    Returns:
      - score_df: LONG table with columns like:
          ['doc_id','text','concept_id','concept_name','concept_prompt','score','rationale','highlight','concept_seed']
      - export_df: our safe summary built from score_df + concepts (no vis())
      - concepts_dict: {concept_id -> dict}
    """
    _assert_lloom()

    # IMPORTANT: use doc_id as id_col (you set df_text['doc_id'] in app.py)
    l = wb.lloom(df=df_text, text_col="text", id_col="doc_id")

    # Induce + score concepts (auto mode)
    score_df = await l.gen_auto(max_concepts=max_concepts, seed=seed, debug=False)

    # Concepts metadata
    concepts_dict = {cid: c.to_dict() for cid, c in l.concepts.items()}

    # Build export_df from long-form scores
    export_df = _build_export_from_long(
        score_df, concepts_dict, doc_id_col="doc_id", threshold=threshold
    )
    return score_df, export_df, concepts_dict


def run_lloom_induction(
    df_text: pd.DataFrame,
    seed: Optional[str] = None,
    max_concepts: int = 3,
    threshold: float = 0.75,
) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Sync wrapper for Streamlit.
    """
    import asyncio
    return asyncio.run(
        run_lloom_induction_async(
            df_text, seed=seed, max_concepts=max_concepts, threshold=threshold
        )
    )
