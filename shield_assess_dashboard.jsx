import { useState } from "react";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const COLORS = {
  bg: "#0a0e17",
  surface: "#111827",
  surfaceHover: "#1a2235",
  border: "#1e2a3a",
  text: "#e2e8f0",
  textMuted: "#64748b",
  textDim: "#475569",
  accent: "#3b82f6",
  accentGlow: "rgba(59, 130, 246, 0.15)",
  danger: "#ef4444",
  dangerGlow: "rgba(239, 68, 68, 0.12)",
  warning: "#f59e0b",
  warningGlow: "rgba(245, 158, 11, 0.12)",
  success: "#10b981",
  successGlow: "rgba(16, 185, 129, 0.12)",
  purple: "#8b5cf6",
  cyan: "#06b6d4",
};

const DUMMY = {
  overview: {
    totalQueries: 142847,
    sensitiveQueries: 55710,
    sensitivePercent: 39.0,
    highRiskResponses: 20856,
    highRiskPercent: 14.6,
    criticalRisk: 891,
    actualSpend: 472000,
    optimalSpend: 158000,
    savings: 314000,
    savingsPercent: 66.5,
    credentialLeaks: 47,
    avgCostPerQuery: 0.0033,
    optimalCostPerQuery: 0.0011,
  },
  dailyTrend: Array.from({ length: 30 }, (_, i) => ({
    day: `${i + 1} Mar`,
    queries: 4200 + Math.floor(Math.random() * 1800),
    sensitive: 1600 + Math.floor(Math.random() * 800),
    highRisk: 580 + Math.floor(Math.random() * 300),
  })),
  sensitivityByCategory: [
    { name: "PII — Direct", count: 18420, pct: 33.1 },
    { name: "Financial Data", count: 14280, pct: 25.6 },
    { name: "Proprietary", count: 11140, pct: 20.0 },
    { name: "Regulated (HIPAA)", count: 6680, pct: 12.0 },
    { name: "Credentials", count: 2780, pct: 5.0 },
    { name: "Custom", count: 2410, pct: 4.3 },
  ],
  sensitiveByModel: [
    { model: "GPT-4 Turbo", count: 28940, pct: 52.0, risk: "high" },
    { model: "Claude 3.5 Sonnet", count: 12250, pct: 22.0, risk: "high" },
    { model: "Mistral Large", count: 8350, pct: 15.0, risk: "medium" },
    { model: "On-Prem Llama 3", count: 4280, pct: 7.7, risk: "low" },
    { model: "Cohere Command", count: 1890, pct: 3.3, risk: "high" },
  ],
  sensitiveByApp: [
    { app: "Compliance Copilot", queries: 18900, sensitive: 12400, leakRate: 65.6 },
    { app: "Customer Service Bot", queries: 42100, sensitive: 14200, leakRate: 33.7 },
    { app: "Legal Research Agent", queries: 8400, sensitive: 7800, leakRate: 92.9 },
    { app: "HR Assistant", queries: 31200, sensitive: 9100, leakRate: 29.2 },
    { app: "Developer Copilot", queries: 28400, sensitive: 8300, leakRate: 29.2 },
    { app: "Finance Analyst", queries: 13847, sensitive: 3910, leakRate: 28.2 },
  ],
  correctnessDistribution: [
    { level: "Low Risk", count: 95240, pct: 66.7, color: COLORS.success },
    { level: "Medium Risk", count: 26750, pct: 18.7, color: COLORS.warning },
    { level: "High Risk", count: 19966, pct: 14.0, color: COLORS.danger },
    { level: "Critical", count: 891, pct: 0.6, color: "#dc2626" },
  ],
  hallucinationTypes: [
    { type: "Fabricated Citations", count: 8420, pct: 40.4 },
    { type: "Invented Statistics", count: 5890, pct: 28.3 },
    { type: "Confident Unhedged Claims", count: 3210, pct: 15.4 },
    { type: "Fabricated Attributions", count: 2100, pct: 10.1 },
    { type: "Internal Inconsistency", count: 1236, pct: 5.8 },
  ],
  flaggedResponses: [
    { id: "q-88291", app: "Legal Research Agent", risk: "critical", type: "Fabricated Citation", detail: "Referenced non-existent case: 'Morrison v. Digital Finance Corp [2024] EWHC 1847'", time: "14:32" },
    { id: "q-91042", app: "Compliance Copilot", risk: "critical", type: "Invented Statistic", detail: "Claimed '2024 FCA report states 94% compliance rate' — no such report exists", time: "15:01" },
    { id: "q-87103", app: "Finance Analyst", risk: "critical", type: "Fabricated Attribution", detail: "Attributed revenue projection to 'Goldman Sachs Q4 2025 Outlook' — document not found", time: "11:22" },
    { id: "q-92847", app: "HR Assistant", risk: "high", type: "Confident Unhedged Claim", detail: "Stated UK notice period requirements as fact without citing Employment Rights Act", time: "16:45" },
    { id: "q-93102", app: "Customer Service Bot", risk: "high", type: "Invented Statistic", detail: "Claimed product has '99.7% uptime SLA' — actual SLA is 99.5%", time: "17:12" },
  ],
  computeByTier: [
    { tier: "Could route to SLM", queries: 88565, pct: 62.0, actualCost: 292000, optimalCost: 21000 },
    { tier: "Correctly at LLM", queries: 39997, pct: 28.0, actualCost: 132000, optimalCost: 132000 },
    { tier: "Multi-pass waste", queries: 10000, pct: 7.0, actualCost: 33000, optimalCost: 0 },
    { tier: "Tail explosions", queries: 4285, pct: 3.0, actualCost: 15000, optimalCost: 5000 },
  ],
  costTrend: Array.from({ length: 30 }, (_, i) => ({
    day: `${i + 1} Mar`,
    actual: 14000 + Math.floor(Math.random() * 4000),
    optimal: 4500 + Math.floor(Math.random() * 1500),
  })),
  topWasteQueries: [
    { id: "q-71029", app: "Developer Copilot", tokens: 142800, cost: "£4.28", complexity: 0.12, optimalCost: "£0.02", saving: "99.5%" },
    { id: "q-83471", app: "Legal Research Agent", tokens: 98400, cost: "£2.95", complexity: 0.31, optimalCost: "£0.08", saving: "97.3%" },
    { id: "q-67283", app: "Customer Service Bot", tokens: 87200, cost: "£2.62", complexity: 0.08, optimalCost: "£0.01", saving: "99.6%" },
    { id: "q-90128", app: "Finance Analyst", tokens: 76100, cost: "£2.28", complexity: 0.44, optimalCost: "£0.19", saving: "91.7%" },
  ],
};

const fmt = (n) => n.toLocaleString("en-GB");
const fmtK = (n) => n >= 1000 ? `${(n / 1000).toFixed(1)}k` : n;
const fmtMoney = (n) => `£${(n / 1000).toFixed(0)}k`;

function StatCard({ label, value, sub, color, glow, icon }) {
  return (
    <div style={{
      background: COLORS.surface,
      border: `1px solid ${COLORS.border}`,
      borderRadius: 10,
      padding: "18px 20px",
      position: "relative",
      overflow: "hidden",
    }}>
      {glow && <div style={{
        position: "absolute", top: -30, right: -30, width: 80, height: 80,
        background: glow, borderRadius: "50%", filter: "blur(30px)",
      }} />}
      <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.08em", color: COLORS.textMuted, textTransform: "uppercase", marginBottom: 8 }}>
        {icon && <span style={{ marginRight: 6 }}>{icon}</span>}{label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: color || COLORS.text, lineHeight: 1.1 }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: COLORS.textMuted, marginTop: 6 }}>{sub}</div>}
    </div>
  );
}

function SectionHeader({ title, subtitle }) {
  return (
    <div style={{ marginBottom: 16, marginTop: 8 }}>
      <h3 style={{ fontSize: 15, fontWeight: 700, color: COLORS.text, margin: 0, letterSpacing: "-0.01em" }}>{title}</h3>
      {subtitle && <p style={{ fontSize: 12, color: COLORS.textMuted, margin: "4px 0 0" }}>{subtitle}</p>}
    </div>
  );
}

function ShieldBadge({ text, color }) {
  return (
    <span style={{
      display: "inline-block",
      padding: "2px 8px",
      borderRadius: 4,
      fontSize: 10,
      fontWeight: 700,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      background: color === "danger" ? COLORS.dangerGlow : color === "warning" ? COLORS.warningGlow : color === "success" ? COLORS.successGlow : COLORS.accentGlow,
      color: color === "danger" ? COLORS.danger : color === "warning" ? COLORS.warning : color === "success" ? COLORS.success : COLORS.accent,
      border: `1px solid ${color === "danger" ? "rgba(239,68,68,0.3)" : color === "warning" ? "rgba(245,158,11,0.3)" : color === "success" ? "rgba(16,185,129,0.3)" : "rgba(59,130,246,0.3)"}`,
    }}>{text}</span>
  );
}

function ProtectAnnotation({ children }) {
  return (
    <div style={{
      background: "rgba(59, 130, 246, 0.06)",
      border: `1px solid rgba(59, 130, 246, 0.2)`,
      borderRadius: 8,
      padding: "10px 14px",
      marginTop: 12,
      display: "flex",
      alignItems: "flex-start",
      gap: 10,
    }}>
      <div style={{ fontSize: 14, marginTop: 1 }}>🛡️</div>
      <div style={{ fontSize: 11.5, color: COLORS.accent, lineHeight: 1.5, fontWeight: 500 }}>{children}</div>
    </div>
  );
}

const tabs = ["Overview", "Sovereignty", "Correctness", "Compute"];

function OverviewPanel() {
  const o = DUMMY.overview;
  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 24 }}>
        <StatCard label="Queries Analysed" value={fmt(o.totalQueries)} sub="Last 30 days" icon="📊" />
        <StatCard label="Containing Sensitive Data" value={`${o.sensitivePercent}%`} sub={`${fmt(o.sensitiveQueries)} queries sent to external LLMs`} color={COLORS.danger} glow={COLORS.dangerGlow} icon="🔓" />
        <StatCard label="High Hallucination Risk" value={`${o.highRiskPercent}%`} sub={`${fmt(o.criticalRisk)} critical risk responses`} color={COLORS.warning} glow={COLORS.warningGlow} icon="⚠️" />
        <StatCard label="Recoverable Compute Waste" value={fmtMoney(o.savings)} sub={`${o.savingsPercent}% of total spend (${fmtMoney(o.actualSpend)})`} color={COLORS.success} glow={COLORS.successGlow} icon="💰" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, marginBottom: 24 }}>
        <StatCard label="Credential Leaks Detected" value={o.credentialLeaks} sub="API keys, tokens, passwords sent to external LLMs" color={COLORS.danger} icon="🔑" />
        <StatCard label="Cost Per Useful Answer" value={`£${o.avgCostPerQuery.toFixed(4)}`} sub={`Optimal: £${o.optimalCostPerQuery.toFixed(4)} (${Math.round((1 - o.optimalCostPerQuery / o.avgCostPerQuery) * 100)}% reduction possible)`} icon="📉" />
        <StatCard label="Annualised Savings" value={fmtMoney(o.savings * 12)} sub="Projected at current query volume with Shield Protect" color={COLORS.accent} glow={COLORS.accentGlow} icon="📈" />
      </div>

      <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
        <SectionHeader title="30-Day Query Trend" subtitle="Total queries, sensitive data exposure, and high-risk responses" />
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={DUMMY.dailyTrend} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="gQueries" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS.accent} stopOpacity={0.2} />
                <stop offset="95%" stopColor={COLORS.accent} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gSensitive" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS.danger} stopOpacity={0.2} />
                <stop offset="95%" stopColor={COLORS.danger} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
            <XAxis dataKey="day" tick={{ fontSize: 10, fill: COLORS.textDim }} interval={4} />
            <YAxis tick={{ fontSize: 10, fill: COLORS.textDim }} />
            <Tooltip contentStyle={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 12, color: COLORS.text }} />
            <Area type="monotone" dataKey="queries" stroke={COLORS.accent} fill="url(#gQueries)" strokeWidth={2} name="Total Queries" />
            <Area type="monotone" dataKey="sensitive" stroke={COLORS.danger} fill="url(#gSensitive)" strokeWidth={2} name="Sensitive" />
            <Area type="monotone" dataKey="highRisk" stroke={COLORS.warning} fill="transparent" strokeWidth={1.5} strokeDasharray="4 3" name="High Risk" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <ProtectAnnotation>
        <strong>Shield Protect would have intercepted {fmt(DUMMY.overview.sensitiveQueries)} sensitive queries</strong> before they reached external LLMs — rerouting them to sovereign SLMs or resolving them via early exit. {DUMMY.overview.credentialLeaks} credential leaks would have been stripped automatically. Projected annual savings: <strong>{fmtMoney(DUMMY.overview.savings * 12)}</strong> in compute waste alone.
      </ProtectAnnotation>
    </div>
  );
}

function SovereigntyPanel() {
  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 20 }}>
        <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
          <SectionHeader title="Sensitive Data by Category" subtitle="Classification of sensitive content found in queries" />
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {DUMMY.sensitivityByCategory.map((c, i) => (
              <div key={i}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontSize: 12, color: COLORS.text, fontWeight: 500 }}>{c.name}</span>
                  <span style={{ fontSize: 12, color: COLORS.textMuted }}>{fmt(c.count)} ({c.pct}%)</span>
                </div>
                <div style={{ height: 6, background: COLORS.bg, borderRadius: 3, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${c.pct}%`, background: `linear-gradient(90deg, ${COLORS.danger}, ${COLORS.warning})`, borderRadius: 3 }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
          <SectionHeader title="Sensitive Queries by Destination Model" subtitle="Which LLMs are receiving your sensitive data?" />
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {DUMMY.sensitiveByModel.map((m, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 12px", background: COLORS.bg, borderRadius: 8 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.text }}>{m.model}</div>
                  <div style={{ fontSize: 11, color: COLORS.textMuted }}>{fmt(m.count)} sensitive queries ({m.pct}%)</div>
                </div>
                <ShieldBadge text={m.risk === "high" ? "External" : m.risk === "medium" ? "EU Cloud" : "On-Prem"} color={m.risk === "high" ? "danger" : m.risk === "medium" ? "warning" : "success"} />
              </div>
            ))}
          </div>
          <ProtectAnnotation>
            <strong>87.1% of sensitive queries</strong> are being sent to external (non-sovereign) LLMs. Shield Protect would reroute these to your on-premise or sovereign cloud models.
          </ProtectAnnotation>
        </div>
      </div>

      <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
        <SectionHeader title="Data Leakage Rate by Application" subtitle="Which applications are sending the most sensitive data to external LLMs?" />
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${COLORS.border}` }}>
                {["Application", "Total Queries", "Sensitive Queries", "Leak Rate", "Risk", "Shield Protect Action"].map(h => (
                  <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: COLORS.textMuted, fontWeight: 600, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.06em" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DUMMY.sensitiveByApp.map((a, i) => (
                <tr key={i} style={{ borderBottom: `1px solid ${COLORS.border}` }}>
                  <td style={{ padding: "10px 12px", color: COLORS.text, fontWeight: 600 }}>{a.app}</td>
                  <td style={{ padding: "10px 12px", color: COLORS.textMuted }}>{fmt(a.queries)}</td>
                  <td style={{ padding: "10px 12px", color: COLORS.danger, fontWeight: 600 }}>{fmt(a.sensitive)}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ width: 60, height: 5, background: COLORS.bg, borderRadius: 3, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${a.leakRate}%`, background: a.leakRate > 60 ? COLORS.danger : a.leakRate > 30 ? COLORS.warning : COLORS.success, borderRadius: 3 }} />
                      </div>
                      <span style={{ color: a.leakRate > 60 ? COLORS.danger : a.leakRate > 30 ? COLORS.warning : COLORS.text, fontWeight: 600, fontSize: 12 }}>{a.leakRate}%</span>
                    </div>
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    <ShieldBadge text={a.leakRate > 60 ? "Critical" : a.leakRate > 30 ? "High" : "Medium"} color={a.leakRate > 60 ? "danger" : a.leakRate > 30 ? "warning" : "default"} />
                  </td>
                  <td style={{ padding: "10px 12px", color: COLORS.accent, fontSize: 11 }}>
                    {a.leakRate > 60 ? "Reroute all to sovereign SLM" : a.leakRate > 30 ? "Classify & selectively reroute" : "Monitor + redact PII"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function CorrectnessPanel() {
  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 20 }}>
        <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
          <SectionHeader title="Response Risk Distribution" subtitle="Correctness scoring across all analysed responses" />
          <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie data={DUMMY.correctnessDistribution} dataKey="count" cx="50%" cy="50%" innerRadius={45} outerRadius={72} strokeWidth={0}>
                  {DUMMY.correctnessDistribution.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
              {DUMMY.correctnessDistribution.map((d, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 10, height: 10, borderRadius: 2, background: d.color, flexShrink: 0 }} />
                  <span style={{ fontSize: 12, color: COLORS.text, flex: 1 }}>{d.level}</span>
                  <span style={{ fontSize: 12, color: COLORS.textMuted, fontVariantNumeric: "tabular-nums" }}>{fmt(d.count)}</span>
                  <span style={{ fontSize: 11, color: d.color, fontWeight: 700, width: 40, textAlign: "right" }}>{d.pct}%</span>
                </div>
              ))}
            </div>
          </div>
          <ProtectAnnotation>
            <strong>{fmt(DUMMY.overview.highRiskResponses)} high-risk responses</strong> would have been blocked by deterministic abstention. Shield Protect refuses to generate outputs it cannot verify.
          </ProtectAnnotation>
        </div>

        <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
          <SectionHeader title="Hallucination Types Detected" subtitle="Most common categories of unverifiable or fabricated content" />
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {DUMMY.hallucinationTypes.map((h, i) => (
              <div key={i}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontSize: 12, color: COLORS.text, fontWeight: 500 }}>{h.type}</span>
                  <span style={{ fontSize: 12, color: COLORS.textMuted }}>{fmt(h.count)} ({h.pct}%)</span>
                </div>
                <div style={{ height: 6, background: COLORS.bg, borderRadius: 3, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${h.pct}%`, background: i === 0 ? COLORS.danger : i === 1 ? COLORS.warning : COLORS.purple, borderRadius: 3, transition: "width 0.5s" }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
        <SectionHeader title="Flagged Responses — Critical & High Risk" subtitle="Most recent responses requiring immediate attention" />
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {DUMMY.flaggedResponses.map((f, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "flex-start", gap: 12, padding: "12px 14px",
              background: f.risk === "critical" ? COLORS.dangerGlow : COLORS.bg,
              borderRadius: 8,
              border: `1px solid ${f.risk === "critical" ? "rgba(239,68,68,0.2)" : COLORS.border}`,
            }}>
              <div style={{ flexShrink: 0, marginTop: 2 }}>
                <ShieldBadge text={f.risk} color={f.risk === "critical" ? "danger" : "warning"} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.text }}>{f.app}</span>
                  <span style={{ fontSize: 10, color: COLORS.textDim }}>•</span>
                  <span style={{ fontSize: 10, color: COLORS.textDim }}>{f.type}</span>
                  <span style={{ fontSize: 10, color: COLORS.textDim }}>•</span>
                  <span style={{ fontSize: 10, color: COLORS.textDim }}>{f.id}</span>
                </div>
                <div style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.5 }}>{f.detail}</div>
              </div>
              <div style={{ fontSize: 11, color: COLORS.textDim, flexShrink: 0 }}>{f.time}</div>
            </div>
          ))}
        </div>
        <ProtectAnnotation>
          Under Shield Protect, all 5 of these responses would have been <strong>intercepted before reaching the user</strong>. The fabricated citation (Morrison v. Digital Finance Corp) and invented FCA report would trigger deterministic abstention. The system would offer to locate verified alternatives instead.
        </ProtectAnnotation>
      </div>
    </div>
  );
}

function ComputePanel() {
  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 20 }}>
        <StatCard label="Actual Monthly Spend" value={fmtMoney(DUMMY.overview.actualSpend)} color={COLORS.danger} icon="💸" />
        <StatCard label="Optimal Monthly Spend" value={fmtMoney(DUMMY.overview.optimalSpend)} color={COLORS.success} icon="✅" />
        <StatCard label="Monthly Waste" value={fmtMoney(DUMMY.overview.savings)} sub={`${DUMMY.overview.savingsPercent}% of total spend`} color={COLORS.warning} glow={COLORS.warningGlow} icon="🗑️" />
        <StatCard label="Queries Routable to SLM" value="62%" sub="88,565 queries at £0.0002 instead of £0.0033" color={COLORS.accent} icon="🔀" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 20 }}>
        <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
          <SectionHeader title="Daily Spend: Actual vs. Optimal" subtitle="What you're spending vs. what you'd spend with Shield Protect" />
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={DUMMY.costTrend} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
              <defs>
                <linearGradient id="gActual" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.danger} stopOpacity={0.15} />
                  <stop offset="95%" stopColor={COLORS.danger} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gOptimal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.15} />
                  <stop offset="95%" stopColor={COLORS.success} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
              <XAxis dataKey="day" tick={{ fontSize: 10, fill: COLORS.textDim }} interval={4} />
              <YAxis tick={{ fontSize: 10, fill: COLORS.textDim }} tickFormatter={(v) => `£${(v/1000).toFixed(0)}k`} />
              <Tooltip contentStyle={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 12, color: COLORS.text }} formatter={(v) => `£${v.toLocaleString()}`} />
              <Area type="monotone" dataKey="actual" stroke={COLORS.danger} fill="url(#gActual)" strokeWidth={2} name="Actual Spend" />
              <Area type="monotone" dataKey="optimal" stroke={COLORS.success} fill="url(#gOptimal)" strokeWidth={2} name="With Shield Protect" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
          <SectionHeader title="Waste Decomposition" subtitle="Where your compute budget is going" />
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={DUMMY.computeByTier} margin={{ top: 5, right: 5, left: -15, bottom: 0 }} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: COLORS.textDim }} tickFormatter={(v) => `£${(v/1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="tier" tick={{ fontSize: 10, fill: COLORS.textMuted }} width={130} />
              <Tooltip contentStyle={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontSize: 12, color: COLORS.text }} formatter={(v) => `£${v.toLocaleString()}`} />
              <Bar dataKey="actualCost" fill={COLORS.danger} radius={[0, 4, 4, 0]} name="Current Cost" barSize={14} />
              <Bar dataKey="optimalCost" fill={COLORS.success} radius={[0, 4, 4, 0]} name="With Shield" barSize={14} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: 10, padding: 20 }}>
        <SectionHeader title="Top Waste Queries — Tail Explosions" subtitle="Individual queries that consumed disproportionate compute relative to their complexity" />
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ borderBottom: `1px solid ${COLORS.border}` }}>
                {["Query ID", "Application", "Tokens", "Actual Cost", "Complexity", "Optimal Cost", "Waste"].map(h => (
                  <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: COLORS.textMuted, fontWeight: 600, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.06em" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DUMMY.topWasteQueries.map((q, i) => (
                <tr key={i} style={{ borderBottom: `1px solid ${COLORS.border}` }}>
                  <td style={{ padding: "10px 12px", color: COLORS.accent, fontFamily: "monospace", fontSize: 11 }}>{q.id}</td>
                  <td style={{ padding: "10px 12px", color: COLORS.text }}>{q.app}</td>
                  <td style={{ padding: "10px 12px", color: COLORS.warning, fontWeight: 600, fontVariantNumeric: "tabular-nums" }}>{fmt(q.tokens)}</td>
                  <td style={{ padding: "10px 12px", color: COLORS.danger, fontWeight: 600 }}>{q.cost}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <div style={{ width: 40, height: 5, background: COLORS.bg, borderRadius: 3, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${q.complexity * 100}%`, background: COLORS.accent, borderRadius: 3 }} />
                      </div>
                      <span style={{ fontSize: 11, color: COLORS.textMuted }}>{q.complexity}</span>
                    </div>
                  </td>
                  <td style={{ padding: "10px 12px", color: COLORS.success, fontWeight: 600 }}>{q.optimalCost}</td>
                  <td style={{ padding: "10px 12px", color: COLORS.danger, fontWeight: 700 }}>{q.saving}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ProtectAnnotation>
          These 4 queries alone cost <strong>£12.13</strong> and could have been resolved for <strong>£0.30</strong>. Shield Protect's tail suppression would have terminated runaway token generation and rerouted to appropriate model tiers based on actual query complexity.
        </ProtectAnnotation>
      </div>
    </div>
  );
}

const panels = { Overview: OverviewPanel, Sovereignty: SovereigntyPanel, Correctness: CorrectnessPanel, Compute: ComputePanel };

export default function ShieldAssessDashboard() {
  const [activeTab, setActiveTab] = useState("Overview");
  const Panel = panels[activeTab];

  return (
    <div style={{ background: COLORS.bg, minHeight: "100vh", color: COLORS.text, fontFamily: "'DM Sans', 'Segoe UI', system-ui, sans-serif" }}>
      <div style={{ padding: "16px 24px", borderBottom: `1px solid ${COLORS.border}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 28, height: 28, borderRadius: 6, background: `linear-gradient(135deg, ${COLORS.accent}, #60a5fa)`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 800, color: "#fff" }}>C</div>
            <span style={{ fontSize: 16, fontWeight: 800, letterSpacing: "-0.02em" }}>Clee<span style={{ color: COLORS.accent }}>AI</span></span>
          </div>
          <div style={{ width: 1, height: 20, background: COLORS.border }} />
          <span style={{ fontSize: 14, fontWeight: 600, color: COLORS.textMuted }}>Shield Assess</span>
          <ShieldBadge text="Diagnostic Mode" color="default" />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontSize: 11, color: COLORS.textMuted }}>Acme Financial Services Ltd</span>
          <span style={{ fontSize: 11, color: COLORS.textDim }}>•</span>
          <span style={{ fontSize: 11, color: COLORS.textMuted }}>1 Mar – 30 Mar 2026</span>
          <div style={{ padding: "5px 12px", borderRadius: 6, background: COLORS.success, color: "#fff", fontSize: 11, fontWeight: 700 }}>● Live</div>
        </div>
      </div>

      <div style={{ padding: "0 24px" }}>
        <div style={{ display: "flex", gap: 0, borderBottom: `1px solid ${COLORS.border}`, marginBottom: 20 }}>
          {tabs.map(t => (
            <button key={t} onClick={() => setActiveTab(t)} style={{
              padding: "14px 20px",
              background: "none",
              border: "none",
              borderBottom: activeTab === t ? `2px solid ${COLORS.accent}` : "2px solid transparent",
              color: activeTab === t ? COLORS.text : COLORS.textMuted,
              fontSize: 13,
              fontWeight: activeTab === t ? 700 : 500,
              cursor: "pointer",
              transition: "all 0.15s",
              fontFamily: "inherit",
            }}>{t}</button>
          ))}
        </div>
        <Panel />
        <div style={{ height: 40 }} />
      </div>
    </div>
  );
}
