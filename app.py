import json
import os
import sys
import time

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from route import process_query

st.set_page_config(
    page_title="LKM Compute Savings — Medical PoC",
    layout="wide",
    page_icon="⚡",
)

# ─── Session state defaults ───────────────────────────────────────────────────
_DEFAULTS = {
    "queries": [],
    "results": [],
    "generation_done": False,
    "processing_done": False,
    "is_processing": False,
    "num_queries_saved": 10,
    "query_type_saved": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─── Helpers ──────────────────────────────────────────────────────────────────
def route_counts(results):
    c = {"EARLY_EXIT": 0, "CONTINUE_SLM": 0, "CONTINUE_TO_LLM": 0}
    for r in results:
        d = r.get("decision", "")
        if d in c:
            c[d] += 1
    return c


def compute_metrics(results):
    n = len(results)
    if n == 0:
        return 0.0, 0, 0.0
    avg_savings = sum(r["savings"] for r in results) / n * 100
    avg_certainty = sum(r["confidence"] for r in results) / n * 100
    return avg_savings, n, avg_certainty


def build_flowchart(n_total, counts, total_processed):
    early = counts.get("EARLY_EXIT", 0)
    slm = counts.get("CONTINUE_SLM", 0)
    llm = counts.get("CONTINUE_TO_LLM", 0)

    def bar(count, color):
        p = (count / total_processed * 100) if total_processed > 0 else 0
        return f"""
        <div style="margin-top:8px">
          <div style="background:#e5e7eb;border-radius:6px;height:16px;overflow:hidden">
            <div style="background:{color};width:{min(p, 100):.1f}%;height:100%;
                        border-radius:6px;transition:width .4s ease"></div>
          </div>
          <div style="font-size:12px;margin-top:3px;font-weight:600;color:#374151">
            {count} queries &nbsp;&bull;&nbsp; {p:.1f}%
          </div>
        </div>"""

    n_label = str(n_total) if n_total > 0 else "N"
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        background:transparent;padding:16px 8px}}
  .fc{{display:flex;flex-direction:column;align-items:center;gap:6px}}
  .node{{border-radius:10px;padding:10px 20px;text-align:center;font-weight:700;font-size:13px}}
  .n-input{{background:#dbeafe;border:2px solid #3b82f6;color:#1e3a8a;
            min-width:190px;font-size:15px;padding:12px 28px}}
  .n-router{{background:#fef3c7;border:2px solid #f59e0b;color:#78350f;
             min-width:230px;font-size:14px;padding:12px 24px}}
  .arrow{{font-size:22px;color:#9ca3af;line-height:1.1}}
  .branches{{display:flex;gap:14px;width:100%;justify-content:center;align-items:flex-start}}
  .branch{{display:flex;flex-direction:column;align-items:center;gap:3px;flex:1;max-width:175px}}
  .card{{border-radius:10px;padding:10px 14px;width:100%}}
  .c-early{{background:#dcfce7;border:2px solid #16a34a}}
  .c-slm  {{background:#dbeafe;border:2px solid #2563eb}}
  .c-llm  {{background:#ffedd5;border:2px solid #ea580c}}
  .card-title{{font-weight:700;font-size:13px;margin-bottom:2px}}
  .t-early{{color:#15803d}}.t-slm{{color:#1d4ed8}}.t-llm{{color:#c2410c}}
</style></head><body>
<div class="fc">
  <div class="node n-input">{n_label} queries input</div>
  <div class="arrow">↓</div>
  <div class="node n-router">⚡ Mechanistic LKM Router</div>
  <div class="branches">
    <div class="branch">
      <div class="arrow">↙</div>
      <div class="card c-early">
        <div class="card-title t-early">🟢 Early Exit</div>
        {bar(early, '#16a34a')}
      </div>
    </div>
    <div class="branch">
      <div class="arrow">↓</div>
      <div class="card c-slm">
        <div class="card-title t-slm">🔵 SLM</div>
        {bar(slm, '#2563eb')}
      </div>
    </div>
    <div class="branch">
      <div class="arrow">↘</div>
      <div class="card c-llm">
        <div class="card-title t-llm">🟡 LLM</div>
        {bar(llm, '#ea580c')}
      </div>
    </div>
  </div>
</div>
</body></html>"""


DECISION_BADGE = {
    "EARLY_EXIT":      ("🟢", "#dcfce7", "#15803d"),
    "CONTINUE_SLM":    ("🔵", "#dbeafe", "#1d4ed8"),
    "CONTINUE_TO_LLM": ("🟡", "#fef9c3", "#854d0e"),
}

def render_table_with_selection(results):
    import pandas as pd

    rows = [
        {
            "#": i + 1,
            "Query": r["query"],
            "Decision": r["decision"],
            "Savings": f"{r['savings']:.1%}",
            "Confidence": f"{r['confidence']:.1%}",
        }
        for i, r in enumerate(results)
    ]
    df = pd.DataFrame(rows)

    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="result_table",
    )

    selected_rows = event.selection.get("rows", []) if event and event.selection else []
    if selected_rows:
        idx = selected_rows[0]
        r = results[idx]
        decision = r.get("decision", "")
        emoji, bg, fg = DECISION_BADGE.get(decision, ("⚪", "#f3f4f6", "#374151"))

        st.markdown(
            f"""
<div style="margin-top:16px;border-radius:12px;border:1px solid #e5e7eb;
            padding:20px 24px;background:#fafafa">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
    <span style="font-weight:700;font-size:15px;color:#111">Query #{idx + 1}</span>
    <span style="background:{bg};color:{fg};border-radius:20px;padding:2px 12px;
                 font-size:12px;font-weight:700">{emoji} {decision}</span>
    <span style="margin-left:auto;font-size:12px;color:#6b7280">
      Savings&nbsp;<b>{r['savings']:.1%}</b>&nbsp;&nbsp;·&nbsp;&nbsp;Confidence&nbsp;<b>{r['confidence']:.1%}</b>
    </span>
  </div>
  <p style="font-size:14px;color:#374151;margin-bottom:14px;font-style:italic">
    {r['query']}
  </p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin-bottom:14px"/>
  <div style="font-size:14px;color:#111;line-height:1.7">
    <b>Answer</b>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(r["answer"] or "_No answer returned._")


def get_openai_key():
    return os.environ.get("OPENAI_API_KEY", "")


# ─── Top bar: Reset ───────────────────────────────────────────────────────────
top_left, top_right = st.columns([6, 1])
with top_right:
    if st.button("🔄 Reset Demo", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ─── Main layout ──────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

# Right column – placeholders created first so the processing loop can update them
with right_col:
    st.subheader("Routing Flow")
    chart_ph = st.empty()
    st.divider()
    mc1, mc2, mc3 = st.columns(3)

m1_ph = mc1.empty()
m2_ph = mc2.empty()
m3_ph = mc3.empty()

# Left column
with left_col:
    st.title("Medical Proof of Concept for LKM Compute Savings")
    st.markdown(
        "_Enter the number of questions and a description of the type of medical-related "
        "questions to generate in real-time and then watch the LKM evaluate and route to "
        "different buckets and observe the compute savings it generates._"
    )
    st.divider()

    locked = st.session_state.generation_done

    num_queries_val = st.number_input(
        "Number of queries to generate",
        min_value=1,
        max_value=500,
        step=1,
        value=st.session_state.num_queries_saved,
        disabled=locked,
    )
    query_type_val = st.text_input(
        "Types of questions to generate",
        placeholder="50% complex reasoning questions and 50% simple fact-based questions",
        value=st.session_state.query_type_saved,
        disabled=locked,
    )

    gen_clicked = False
    proc_clicked = False

    if not st.session_state.generation_done:
        gen_clicked = st.button(
            "Generate Questions",
            type="primary",
            disabled=not query_type_val.strip(),
        )
    else:
        st.success(f"✅ {len(st.session_state.queries)} questions generated")
        if not st.session_state.processing_done and not st.session_state.is_processing:
            proc_clicked = st.button("Process Questions", type="primary")

    status_ph = st.empty()
    table_ph = st.empty()


# ─── Initial chart + metrics render ───────────────────────────────────────────
_results = st.session_state.results
_counts = route_counts(_results)
_sv, _np, _cert = compute_metrics(_results)
_n_total = len(st.session_state.queries)

with chart_ph.container():
    components.html(build_flowchart(_n_total, _counts, _np), height=390, scrolling=False)

m1_ph.metric("% Compute Savings", f"{_sv:.1f}%", help="Average % of LLM compute avoided")
m2_ph.metric("Queries Processed", _np)
m3_ph.metric("Decision Certainty", f"{_cert:.1f}%")

# Render existing table if results are stored (e.g. after page rerun)
if _results:
    _label = (
        "✅ Query processing complete"
        if st.session_state.processing_done
        else f"📊 {len(_results)} of {_n_total} queries processed"
    )
    with table_ph.container():
        with st.expander(_label, expanded=True):
            render_table_with_selection(_results)


# ─── Handle Generate button ───────────────────────────────────────────────────
if gen_clicked:
    st.session_state.num_queries_saved = num_queries_val
    st.session_state.query_type_saved = query_type_val

    key = get_openai_key()
    if not key:
        with status_ph.container():
            st.error("No OpenAI API key found. Set OPENAI_API_KEY in your .env file.")
    else:
        with status_ph.container():
            with st.spinner("Generating questions…"):
                try:
                    from openai import OpenAI

                    client = OpenAI(api_key=key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": (
                                    f"You are testing a routing model for saving compute by predicting circuit traces and as a result saving compute by rerouting queries to a smaller language model or to an early exit, depending on the predicted circuits, exclusive to questions related to the medical / pharmaceutical domain. Your task is to generate exactly {num_queries_val} medical questions of types: {query_type_val} specified by the user."
                                    "Return ONLY a strict JSON object — no markdown, no explanation: "
                                    '{"queries": ["question 1", "question 2", ...]}'
                                ),
                            }
                        ],
                        response_format={"type": "json_object"},
                    )
                    data = json.loads(response.choices[0].message.content)
                    st.session_state.queries = data["queries"]
                    st.session_state.generation_done = True
                except Exception as exc:
                    with status_ph.container():
                        st.error(f"OpenAI error: {exc}")
        st.rerun()


# ─── Handle Process button ────────────────────────────────────────────────────
if proc_clicked:
    st.session_state.is_processing = True
    st.rerun()


# ─── Processing loop ──────────────────────────────────────────────────────────
if st.session_state.is_processing and not st.session_state.processing_done:
    queries = st.session_state.queries
    n = len(queries)

    for i in range(len(st.session_state.results), n):
        with status_ph.container():
            with st.spinner(f"Processing query {i + 1} of {n}…"):
                result = process_query(queries[i])
                st.session_state.results.append(result)

                counts = route_counts(st.session_state.results)
                sv, np_, cert = compute_metrics(st.session_state.results)

                with chart_ph.container():
                    components.html(
                        build_flowchart(n, counts, np_),
                        height=390,
                        scrolling=False,
                    )

                m1_ph.metric("% Compute Savings", f"{sv:.1f}%")
                m2_ph.metric("Queries Processed", np_)
                m3_ph.metric("Decision Certainty", f"{cert:.1f}%")

                with table_ph.container():
                    with st.expander(f"📊 {np_} of {n} queries processed", expanded=True):
                        render_table_with_selection(st.session_state.results)

                time.sleep(0.35)

    st.session_state.is_processing = False
    st.session_state.processing_done = True
    with status_ph.container():
        st.success("✅ Query processing complete")
    st.rerun()
