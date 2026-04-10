import random
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(
    page_title="Shield Assess — CreeAI",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="collapsed",
)

# ─── Colours ─────────────────────────────────────────────────────────────────
C = dict(
    bg="#0a0e17", surface="#111827", border="#1e2a3a",
    text="#e2e8f0", muted="#64748b", dim="#475569",
    accent="#3b82f6", danger="#ef4444", warning="#f59e0b",
    success="#10b981", purple="#8b5cf6", cyan="#06b6d4",
)

# ─── Dummy data ──────────────────────────────────────────────────────────────
random.seed(42)

OV = dict(
    totalQueries=142847, sensitiveQueries=55710, sensitivePercent=39.0,
    highRiskResponses=20856, highRiskPercent=14.6, criticalRisk=891,
    actualSpend=472000, optimalSpend=158000, savings=314000, savingsPercent=66.5,
    credentialLeaks=47, avgCostPerQuery=0.0033, optimalCostPerQuery=0.0011,
)

DAILY_TREND = [
    {"day": f"{i+1} Mar",
     "queries": 4200 + random.randint(0, 1800),
     "sensitive": 1600 + random.randint(0, 800),
     "highRisk": 580 + random.randint(0, 300)}
    for i in range(30)
]

SENSITIVITY_BY_CAT = [
    ("PII — Direct", 18420, 33.1), ("Financial Data", 14280, 25.6),
    ("Proprietary", 11140, 20.0), ("Regulated (HIPAA)", 6680, 12.0),
    ("Credentials", 2780, 5.0), ("Custom", 2410, 4.3),
]

SENSITIVE_BY_MODEL = [
    ("GPT-4 Turbo", 28940, 52.0, "high"), ("Claude 3.5 Sonnet", 12250, 22.0, "high"),
    ("Mistral Large", 8350, 15.0, "medium"), ("On-Prem Llama 3", 4280, 7.7, "low"),
    ("Cohere Command", 1890, 3.3, "high"),
]

SENSITIVE_BY_APP = [
    ("Compliance Copilot", 18900, 12400, 65.6),
    ("Customer Service Bot", 42100, 14200, 33.7),
    ("Legal Research Agent", 8400, 7800, 92.9),
    ("HR Assistant", 31200, 9100, 29.2),
    ("Developer Copilot", 28400, 8300, 29.2),
    ("Finance Analyst", 13847, 3910, 28.2),
]

CORRECTNESS_DIST = [
    ("Low Risk", 95240, 66.7, C["success"]),
    ("Medium Risk", 26750, 18.7, C["warning"]),
    ("High Risk", 19966, 14.0, C["danger"]),
    ("Critical", 891, 0.6, "#dc2626"),
]

HALLUCINATION_TYPES = [
    ("Fabricated Citations", 8420, 40.4),
    ("Invented Statistics", 5890, 28.3),
    ("Confident Unhedged Claims", 3210, 15.4),
    ("Fabricated Attributions", 2100, 10.1),
    ("Internal Inconsistency", 1236, 5.8),
]

FLAGGED = [
    ("q-88291", "Legal Research Agent", "critical", "Fabricated Citation",
     "Referenced non-existent case: 'Morrison v. Digital Finance Corp [2024] EWHC 1847'", "14:32"),
    ("q-91042", "Compliance Copilot", "critical", "Invented Statistic",
     "Claimed '2024 FCA report states 94% compliance rate' — no such report exists", "15:01"),
    ("q-87103", "Finance Analyst", "critical", "Fabricated Attribution",
     "Attributed revenue projection to 'Goldman Sachs Q4 2025 Outlook' — document not found", "11:22"),
    ("q-92847", "HR Assistant", "high", "Confident Unhedged Claim",
     "Stated UK notice period requirements as fact without citing Employment Rights Act", "16:45"),
    ("q-93102", "Customer Service Bot", "high", "Invented Statistic",
     "Claimed product has '99.7% uptime SLA' — actual SLA is 99.5%", "17:12"),
]

COMPUTE_BY_TIER = [
    ("Could route to SLM", 88565, 62.0, 292000, 21000),
    ("Correctly at LLM", 39997, 28.0, 132000, 132000),
    ("Multi-pass waste", 10000, 7.0, 33000, 0),
    ("Tail explosions", 4285, 3.0, 15000, 5000),
]

COST_TREND = [
    {"day": f"{i+1} Mar",
     "actual": 14000 + random.randint(0, 4000),
     "optimal": 4500 + random.randint(0, 1500)}
    for i in range(30)
]

TOP_WASTE = [
    ("q-71029", "Developer Copilot", 142800, "£4.28", 0.12, "£0.02", "99.5%"),
    ("q-83471", "Legal Research Agent", 98400, "£2.95", 0.31, "£0.08", "97.3%"),
    ("q-67283", "Customer Service Bot", 87200, "£2.62", 0.08, "£0.01", "99.6%"),
    ("q-90128", "Finance Analyst", 76100, "£2.28", 0.44, "£0.19", "91.7%"),
]


# ─── Helpers ─────────────────────────────────────────────────────────────────
def fmt(n):
    return f"{n:,}"

def fmt_money(n):
    return f"£{n // 1000}k"

def shield_annotation(text):
    st.markdown(
        f"""<div style="background:rgba(59,130,246,0.06);border:1px solid rgba(59,130,246,0.2);
        border-radius:8px;padding:10px 14px;margin-top:12px;display:flex;align-items:flex-start;gap:10px">
        <div style="font-size:14px;margin-top:1px">🛡️</div>
        <div style="font-size:11.5px;color:{C['accent']};line-height:1.5;font-weight:500">{text}</div>
        </div>""",
        unsafe_allow_html=True,
    )

def badge_html(text, color):
    color_map = {
        "danger": (C["danger"], "rgba(239,68,68,0.12)", "rgba(239,68,68,0.3)"),
        "warning": (C["warning"], "rgba(245,158,11,0.12)", "rgba(245,158,11,0.3)"),
        "success": (C["success"], "rgba(16,185,129,0.12)", "rgba(16,185,129,0.3)"),
    }
    fg, bg, bd = color_map.get(color, (C["accent"], "rgba(59,130,246,0.15)", "rgba(59,130,246,0.3)"))
    return (f'<span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;'
            f'font-weight:700;letter-spacing:0.05em;text-transform:uppercase;'
            f'background:{bg};color:{fg};border:1px solid {bd}">{text}</span>')

def progress_bar_html(pct, color, height=6):
    return (f'<div style="height:{height}px;background:{C["bg"]};border-radius:3px;overflow:hidden">'
            f'<div style="height:100%;width:{min(pct,100):.1f}%;background:{color};border-radius:3px"></div></div>')

def stat_card(label, value, sub="", color=None, icon=""):
    c = color or C["text"]
    st.markdown(
        f"""<div style="background:{C['surface']};border:1px solid {C['border']};border-radius:10px;
        padding:18px 20px;height:100%">
        <div style="font-size:11px;font-weight:600;letter-spacing:0.08em;color:{C['muted']};
        text-transform:uppercase;margin-bottom:8px">{icon} {label}</div>
        <div style="font-size:28px;font-weight:700;color:{c};line-height:1.1">{value}</div>
        {"<div style='font-size:12px;color:" + C['muted'] + ";margin-top:6px'>" + sub + "</div>" if sub else ""}
        </div>""",
        unsafe_allow_html=True,
    )


# ─── Global dark style injection ────────────────────────────────────────────
st.markdown(f"""<style>
    .stApp {{ background-color: {C['bg']}; color: {C['text']}; }}
    .stTabs [data-baseweb="tab-list"] {{ background: transparent; border-bottom: 1px solid {C['border']}; }}
    .stTabs [data-baseweb="tab"] {{ color: {C['muted']}; font-weight: 500; }}
    .stTabs [aria-selected="true"] {{ color: {C['text']} !important; font-weight: 700; border-bottom-color: {C['accent']} !important; }}
    section[data-testid="stSidebar"] {{ display: none; }}
    div[data-testid="stMetric"] {{ background: {C['surface']}; border: 1px solid {C['border']}; border-radius: 10px; padding: 18px 20px; }}
    div[data-testid="stMetricValue"] {{ color: {C['text']}; }}
    div[data-testid="stMetricLabel"] {{ color: {C['muted']}; }}
</style>""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    f"""<div style="display:flex;align-items:center;justify-content:space-between;
    padding:10px 0 14px;border-bottom:1px solid {C['border']};margin-bottom:20px">
    <div style="display:flex;align-items:center;gap:14px">
        <div style="display:flex;align-items:center;gap:6px">
            <div style="width:28px;height:28px;border-radius:6px;
            background:linear-gradient(135deg,{C['accent']},#60a5fa);display:flex;
            align-items:center;justify-content:center;font-size:14px;font-weight:800;color:#fff">C</div>
            <span style="font-size:16px;font-weight:800;letter-spacing:-0.02em;color:{C['text']}">
            Clee<span style="color:{C['accent']}">AI</span></span>
        </div>
        <div style="width:1px;height:20px;background:{C['border']}"></div>
        <span style="font-size:14px;font-weight:600;color:{C['muted']}">Shield Assess</span>
        {badge_html("Diagnostic Mode", "default")}
    </div>
    <div style="display:flex;align-items:center;gap:16px">
        <span style="font-size:11px;color:{C['muted']}">Acme Financial Services Ltd</span>
        <span style="font-size:11px;color:{C['dim']}">•</span>
        <span style="font-size:11px;color:{C['muted']}">1 Mar – 30 Mar 2026</span>
        <div style="padding:5px 12px;border-radius:6px;background:{C['success']};
        color:#fff;font-size:11px;font-weight:700">● Live</div>
    </div>
    </div>""",
    unsafe_allow_html=True,
)


# ─── Tabs ────────────────────────────────────────────────────────────────────
tab_overview, tab_sovereignty, tab_correctness, tab_compute = st.tabs(
    ["Overview", "Sovereignty", "Correctness", "Compute"]
)

# ════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab_overview:
    r1 = st.columns(4)
    with r1[0]:
        stat_card("Queries Analysed", fmt(OV["totalQueries"]), "Last 30 days", icon="📊")
    with r1[1]:
        stat_card("Containing Sensitive Data", f"{OV['sensitivePercent']}%",
                  f"{fmt(OV['sensitiveQueries'])} queries sent to external LLMs",
                  color=C["danger"], icon="🔓")
    with r1[2]:
        stat_card("High Hallucination Risk", f"{OV['highRiskPercent']}%",
                  f"{fmt(OV['criticalRisk'])} critical risk responses",
                  color=C["warning"], icon="⚠️")
    with r1[3]:
        stat_card("Recoverable Compute Waste", fmt_money(OV["savings"]),
                  f"{OV['savingsPercent']}% of total spend ({fmt_money(OV['actualSpend'])})",
                  color=C["success"], icon="💰")

    st.write("")
    r2 = st.columns(3)
    with r2[0]:
        stat_card("Credential Leaks Detected", str(OV["credentialLeaks"]),
                  "API keys, tokens, passwords sent to external LLMs", color=C["danger"], icon="🔑")
    with r2[1]:
        reduction = round((1 - OV["optimalCostPerQuery"] / OV["avgCostPerQuery"]) * 100)
        stat_card("Cost Per Useful Answer", f"£{OV['avgCostPerQuery']:.4f}",
                  f"Optimal: £{OV['optimalCostPerQuery']:.4f} ({reduction}% reduction possible)", icon="📉")
    with r2[2]:
        stat_card("Annualised Savings", fmt_money(OV["savings"] * 12),
                  "Projected at current query volume with Shield Protect",
                  color=C["accent"], icon="📈")

    st.write("")
    st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
    border-radius:10px;padding:20px">
    <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">30-Day Query Trend</h4>
    <p style="font-size:12px;color:{C['muted']};margin:0 0 12px">Total queries, sensitive data exposure, and high-risk responses</p>
    </div>""", unsafe_allow_html=True)

    df_trend = pd.DataFrame(DAILY_TREND)
    st.area_chart(df_trend, x="day", y=["queries", "sensitive", "highRisk"],
                  color=[C["accent"], C["danger"], C["warning"]], height=250)

    shield_annotation(
        f"<strong>Shield Protect would have intercepted {fmt(OV['sensitiveQueries'])} sensitive queries</strong> "
        f"before they reached external LLMs — rerouting them to sovereign SLMs or resolving them via early exit. "
        f"{OV['credentialLeaks']} credential leaks would have been stripped automatically. "
        f"Projected annual savings: <strong>{fmt_money(OV['savings'] * 12)}</strong> in compute waste alone."
    )


# ════════════════════════════════════════════════════════════════════════════
# SOVEREIGNTY
# ════════════════════════════════════════════════════════════════════════════
with tab_sovereignty:
    col_cat, col_model = st.columns(2)

    with col_cat:
        st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
        border-radius:10px;padding:20px">
        <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Sensitive Data by Category</h4>
        <p style="font-size:12px;color:{C['muted']};margin:0 0 16px">Classification of sensitive content found in queries</p>
        {"".join(
            f'''<div style="margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-size:12px;color:{C['text']};font-weight:500">{name}</span>
            <span style="font-size:12px;color:{C['muted']}">{fmt(count)} ({pct}%)</span>
            </div>{progress_bar_html(pct, f"linear-gradient(90deg,{C['danger']},{C['warning']})")}</div>'''
            for name, count, pct in SENSITIVITY_BY_CAT
        )}
        </div>""", unsafe_allow_html=True)

    with col_model:
        risk_badge = lambda risk: badge_html(
            "External" if risk == "high" else "EU Cloud" if risk == "medium" else "On-Prem",
            "danger" if risk == "high" else "warning" if risk == "medium" else "success"
        )
        st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
        border-radius:10px;padding:20px">
        <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Sensitive Queries by Destination Model</h4>
        <p style="font-size:12px;color:{C['muted']};margin:0 0 16px">Which LLMs are receiving your sensitive data?</p>
        {"".join(
            f'''<div style="display:flex;align-items:center;gap:12px;padding:8px 12px;
            background:{C['bg']};border-radius:8px;margin-bottom:8px">
            <div style="flex:1">
            <div style="font-size:13px;font-weight:600;color:{C['text']}">{model}</div>
            <div style="font-size:11px;color:{C['muted']}">{fmt(count)} sensitive queries ({pct}%)</div>
            </div>{risk_badge(risk)}</div>'''
            for model, count, pct, risk in SENSITIVE_BY_MODEL
        )}
        </div>""", unsafe_allow_html=True)

        shield_annotation(
            "<strong>87.1% of sensitive queries</strong> are being sent to external (non-sovereign) LLMs. "
            "Shield Protect would reroute these to your on-premise or sovereign cloud models."
        )

    st.write("")
    # Leakage table
    st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
    border-radius:10px;padding:20px">
    <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Data Leakage Rate by Application</h4>
    <p style="font-size:12px;color:{C['muted']};margin:0 0 16px">Which applications are sending the most sensitive data to external LLMs?</p>
    <table style="width:100%;border-collapse:collapse;font-size:12px">
    <thead><tr style="border-bottom:1px solid {C['border']}">
    {"".join(f'<th style="padding:8px 12px;text-align:left;color:{C["muted"]};font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:0.06em">{h}</th>' for h in ["Application","Total Queries","Sensitive Queries","Leak Rate","Risk","Shield Protect Action"])}
    </tr></thead><tbody>
    {"".join(
        f'''<tr style="border-bottom:1px solid {C['border']}">
        <td style="padding:10px 12px;color:{C['text']};font-weight:600">{app}</td>
        <td style="padding:10px 12px;color:{C['muted']}">{fmt(total)}</td>
        <td style="padding:10px 12px;color:{C['danger']};font-weight:600">{fmt(sens)}</td>
        <td style="padding:10px 12px"><div style="display:flex;align-items:center;gap:8px">
        <div style="width:60px;height:5px;background:{C['bg']};border-radius:3px;overflow:hidden">
        <div style="height:100%;width:{leak}%;background:{C['danger'] if leak > 60 else C['warning'] if leak > 30 else C['success']};border-radius:3px"></div></div>
        <span style="color:{C['danger'] if leak > 60 else C['warning'] if leak > 30 else C['text']};font-weight:600;font-size:12px">{leak}%</span></div></td>
        <td style="padding:10px 12px">{badge_html("Critical" if leak > 60 else "High" if leak > 30 else "Medium", "danger" if leak > 60 else "warning" if leak > 30 else "default")}</td>
        <td style="padding:10px 12px;color:{C['accent']};font-size:11px">{"Reroute all to sovereign SLM" if leak > 60 else "Classify & selectively reroute" if leak > 30 else "Monitor + redact PII"}</td>
        </tr>'''
        for app, total, sens, leak in SENSITIVE_BY_APP
    )}
    </tbody></table></div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CORRECTNESS
# ════════════════════════════════════════════════════════════════════════════
with tab_correctness:
    col_risk, col_hall = st.columns(2)

    with col_risk:
        st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
        border-radius:10px;padding:20px">
        <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Response Risk Distribution</h4>
        <p style="font-size:12px;color:{C['muted']};margin:0 0 16px">Correctness scoring across all analysed responses</p>
        {"".join(
            f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
            <div style="width:10px;height:10px;border-radius:2px;background:{color};flex-shrink:0"></div>
            <span style="font-size:12px;color:{C['text']};flex:1">{level}</span>
            <span style="font-size:12px;color:{C['muted']};font-variant-numeric:tabular-nums">{fmt(count)}</span>
            <span style="font-size:11px;color:{color};font-weight:700;width:40px;text-align:right">{pct}%</span>
            </div>'''
            for level, count, pct, color in CORRECTNESS_DIST
        )}
        </div>""", unsafe_allow_html=True)

        shield_annotation(
            f"<strong>{fmt(OV['highRiskResponses'])} high-risk responses</strong> would have been blocked by "
            "deterministic abstention. Shield Protect refuses to generate outputs it cannot verify."
        )

    with col_hall:
        bar_colors = [C["danger"], C["warning"], C["purple"], C["purple"], C["purple"]]
        st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
        border-radius:10px;padding:20px">
        <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Hallucination Types Detected</h4>
        <p style="font-size:12px;color:{C['muted']};margin:0 0 16px">Most common categories of unverifiable or fabricated content</p>
        {"".join(
            f'''<div style="margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-size:12px;color:{C['text']};font-weight:500">{htype}</span>
            <span style="font-size:12px;color:{C['muted']}">{fmt(count)} ({pct}%)</span>
            </div>{progress_bar_html(pct, bar_colors[i])}</div>'''
            for i, (htype, count, pct) in enumerate(HALLUCINATION_TYPES)
        )}
        </div>""", unsafe_allow_html=True)

    st.write("")
    # Flagged responses
    st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
    border-radius:10px;padding:20px">
    <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Flagged Responses — Critical & High Risk</h4>
    <p style="font-size:12px;color:{C['muted']};margin:0 0 16px">Most recent responses requiring immediate attention</p>
    {"".join(
        f'''<div style="display:flex;align-items:flex-start;gap:12px;padding:12px 14px;
        background:{'rgba(239,68,68,0.12)' if risk == 'critical' else C['bg']};border-radius:8px;
        border:1px solid {'rgba(239,68,68,0.2)' if risk == 'critical' else C['border']};margin-bottom:6px">
        <div style="flex-shrink:0;margin-top:2px">{badge_html(risk, "danger" if risk == "critical" else "warning")}</div>
        <div style="flex:1;min-width:0">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span style="font-size:12px;font-weight:700;color:{C['text']}">{app}</span>
        <span style="font-size:10px;color:{C['dim']}">•</span>
        <span style="font-size:10px;color:{C['dim']}">{ftype}</span>
        <span style="font-size:10px;color:{C['dim']}">•</span>
        <span style="font-size:10px;color:{C['dim']}">{qid}</span>
        </div>
        <div style="font-size:12px;color:{C['muted']};line-height:1.5">{detail}</div>
        </div>
        <div style="font-size:11px;color:{C['dim']};flex-shrink:0">{time}</div>
        </div>'''
        for qid, app, risk, ftype, detail, time in FLAGGED
    )}
    </div>""", unsafe_allow_html=True)

    shield_annotation(
        "Under Shield Protect, all 5 of these responses would have been <strong>intercepted before reaching the user</strong>. "
        "The fabricated citation (Morrison v. Digital Finance Corp) and invented FCA report would trigger deterministic abstention. "
        "The system would offer to locate verified alternatives instead."
    )


# ════════════════════════════════════════════════════════════════════════════
# COMPUTE
# ════════════════════════════════════════════════════════════════════════════
with tab_compute:
    r1 = st.columns(4)
    with r1[0]:
        stat_card("Actual Monthly Spend", fmt_money(OV["actualSpend"]), color=C["danger"], icon="💸")
    with r1[1]:
        stat_card("Optimal Monthly Spend", fmt_money(OV["optimalSpend"]), color=C["success"], icon="✅")
    with r1[2]:
        stat_card("Monthly Waste", fmt_money(OV["savings"]),
                  f"{OV['savingsPercent']}% of total spend", color=C["warning"], icon="🗑️")
    with r1[3]:
        stat_card("Queries Routable to SLM", "62%",
                  "88,565 queries at £0.0002 instead of £0.0033", color=C["accent"], icon="🔀")

    st.write("")
    col_spend, col_waste = st.columns(2)

    with col_spend:
        st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
        border-radius:10px;padding:20px">
        <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Daily Spend: Actual vs. Optimal</h4>
        <p style="font-size:12px;color:{C['muted']};margin:0 0 4px">What you're spending vs. what you'd spend with Shield Protect</p>
        </div>""", unsafe_allow_html=True)
        df_cost = pd.DataFrame(COST_TREND)
        st.area_chart(df_cost, x="day", y=["actual", "optimal"],
                      color=[C["danger"], C["success"]], height=220)

    with col_waste:
        df_tier = pd.DataFrame(COMPUTE_BY_TIER, columns=["tier", "queries", "pct", "actualCost", "optimalCost"])
        st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
        border-radius:10px;padding:20px">
        <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Waste Decomposition</h4>
        <p style="font-size:12px;color:{C['muted']};margin:0 0 4px">Where your compute budget is going</p>
        </div>""", unsafe_allow_html=True)
        st.bar_chart(df_tier, x="tier", y=["actualCost", "optimalCost"],
                     color=[C["danger"], C["success"]], height=220)

    st.write("")
    # Top waste queries table
    st.markdown(f"""<div style="background:{C['surface']};border:1px solid {C['border']};
    border-radius:10px;padding:20px">
    <h4 style="font-size:15px;font-weight:700;color:{C['text']};margin:0 0 4px">Top Waste Queries — Tail Explosions</h4>
    <p style="font-size:12px;color:{C['muted']};margin:0 0 16px">Individual queries that consumed disproportionate compute relative to their complexity</p>
    <table style="width:100%;border-collapse:collapse;font-size:12px">
    <thead><tr style="border-bottom:1px solid {C['border']}">
    {"".join(f'<th style="padding:8px 12px;text-align:left;color:{C["muted"]};font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:0.06em">{h}</th>' for h in ["Query ID","Application","Tokens","Actual Cost","Complexity","Optimal Cost","Waste"])}
    </tr></thead><tbody>
    {"".join(
        f'''<tr style="border-bottom:1px solid {C['border']}">
        <td style="padding:10px 12px;color:{C['accent']};font-family:monospace;font-size:11px">{qid}</td>
        <td style="padding:10px 12px;color:{C['text']}">{app}</td>
        <td style="padding:10px 12px;color:{C['warning']};font-weight:600;font-variant-numeric:tabular-nums">{fmt(tokens)}</td>
        <td style="padding:10px 12px;color:{C['danger']};font-weight:600">{cost}</td>
        <td style="padding:10px 12px"><div style="display:flex;align-items:center;gap:6px">
        <div style="width:40px;height:5px;background:{C['bg']};border-radius:3px;overflow:hidden">
        <div style="height:100%;width:{complexity*100}%;background:{C['accent']};border-radius:3px"></div></div>
        <span style="font-size:11px;color:{C['muted']}">{complexity}</span></div></td>
        <td style="padding:10px 12px;color:{C['success']};font-weight:600">{opt_cost}</td>
        <td style="padding:10px 12px;color:{C['danger']};font-weight:700">{waste}</td>
        </tr>'''
        for qid, app, tokens, cost, complexity, opt_cost, waste in TOP_WASTE
    )}
    </tbody></table></div>""", unsafe_allow_html=True)

    shield_annotation(
        "These 4 queries alone cost <strong>£12.13</strong> and could have been resolved for <strong>£0.30</strong>. "
        "Shield Protect's tail suppression would have terminated runaway token generation and rerouted to "
        "appropriate model tiers based on actual query complexity."
    )
