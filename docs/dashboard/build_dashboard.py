"""
Build a static HTML dashboard from docs/data/aggregates.json

  python docs/dashboard/build_dashboard.py
  # then open docs/dashboard/index.html
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "aggregates.json"
OUT = HERE / "index.html"


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    html = TEMPLATE.replace("__DATA__", json.dumps(payload, ensure_ascii=False))
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT}")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Control Eval Lab — figures</title>
<style>
  :root {
    --bg: #f4f1ea;
    --ink: #1c1917;
    --muted: #57534e;
    --panel: #fffdf8;
    --line: #d6d3d1;
    --accent: #0f766e;
    --try: #0f766e;
    --warn: #b45309;
    --bad: #b91c1c;
    --ok: #15803d;
    --font: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
    --display: "IBM Plex Serif", Georgia, serif;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: var(--font);
    color: var(--ink);
    background:
      radial-gradient(900px 420px at 0% 0%, #dcece8 0%, transparent 55%),
      radial-gradient(700px 380px at 100% 10%, #efe6d6 0%, transparent 50%),
      var(--bg);
    line-height: 1.5;
  }
  header, main { max-width: 960px; margin: 0 auto; padding: 1.5rem 1.25rem; }
  header { padding-top: 2.25rem; padding-bottom: 0.5rem; }
  h1 {
    font-family: var(--display);
    font-size: clamp(1.6rem, 3vw, 2.1rem);
    margin: 0 0 0.5rem;
    letter-spacing: -0.02em;
  }
  .lede { color: var(--muted); max-width: 42rem; margin: 0 0 1rem; }
  .note {
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    padding: 0.85rem 1rem;
    border-radius: 0 10px 10px 0;
    max-width: 42rem;
  }
  section {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.1rem 1.2rem 1.25rem;
    margin: 1rem 0;
  }
  section h2 {
    margin: 0 0 0.35rem;
    font-size: 1.15rem;
    font-family: var(--display);
  }
  section p.sub { margin: 0 0 1rem; color: var(--muted); font-size: 0.95rem; }
  .kpis {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.75rem;
  }
  .kpi {
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 0.85rem 0.9rem;
    background: #fafaf9;
  }
  .kpi .label { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  .kpi .value { font-size: 1.35rem; font-weight: 700; margin-top: 0.25rem; font-variant-numeric: tabular-nums; }
  .kpi .value.ok { color: var(--ok); }
  .chart { display: grid; gap: 0.85rem; margin-top: 0.5rem; }
  .row {
    display: grid;
    grid-template-columns: minmax(8rem, 13rem) 1fr 3.2rem;
    gap: 0.65rem;
    align-items: center;
  }
  @media (max-width: 640px) {
    .row { grid-template-columns: 1fr; gap: 0.25rem; }
  }
  .row .name { font-weight: 600; font-size: 0.95rem; }
  .track {
    height: 16px;
    background: #e7e5e4;
    border-radius: 999px;
    overflow: hidden;
  }
  .fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #0d9488, #0f766e);
  }
  .fill.warn { background: linear-gradient(90deg, #d97706, #b45309); }
  .fill.bad { background: linear-gradient(90deg, #f87171, #b91c1c); }
  .pct { font-variant-numeric: tabular-nums; font-weight: 700; text-align: right; }
  ul.takeaways { margin: 0.4rem 0 0; padding-left: 1.2rem; }
  ul.takeaways li { margin: 0.35rem 0; }
  footer { color: var(--muted); font-size: 0.85rem; padding: 0 1.25rem 2.5rem; max-width: 960px; margin: 0 auto; }
  a { color: var(--accent); }
</style>
</head>
<body>
  <header>
    <h1>Control Eval Lab — figures</h1>
    <p class="lede" id="lede"></p>
    <div class="note" id="note"></div>
  </header>
  <main>
    <section>
      <h2>Control fixture (toy app)</h2>
      <p class="sub">Local disposable target with planted lab markers. Reproducible via pytest + deny-smoke.</p>
      <div class="kpis" id="fixture-kpis"></div>
    </section>
    <section>
      <h2>Owner System A (sanitized)</h2>
      <p class="sub">Private system the author owns. Outcomes only — no product name, cookies, or raw traces.</p>
      <div class="kpis" id="system-kpis"></div>
    </section>
    <section>
      <h2>Sandbox tool-attempt rates</h2>
      <p class="sub" id="tool-sub"></p>
      <div class="chart" id="tool-chart"></div>
    </section>
    <section>
      <h2>Reason-then-act (highlight)</h2>
      <p class="sub" id="rta-sub"></p>
      <div class="chart" id="rta-chart"></div>
    </section>
    <section>
      <h2>Takeaways</h2>
      <ul class="takeaways" id="takeaways"></ul>
    </section>
  </main>
  <footer>
    Built from <code>docs/data/aggregates.json</code>.
    Rebuild: <code>python docs/dashboard/build_dashboard.py</code>.
    See also <a href="../REFUSAL_EVAL.md">REFUSAL_EVAL.md</a> and
    <a href="../EXPERIMENT_LOG.md">EXPERIMENT_LOG.md</a>.
  </footer>
<script>
const DATA = __DATA__;

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"
  })[c]);
}

function barClass(pct) {
  if (pct == null) return "fill";
  if (pct <= 20) return "fill";
  if (pct <= 50) return "fill warn";
  return "fill bad";
}

function renderBar(label, pct, note) {
  if (pct == null) {
    return `<div class="row">
      <div class="name">${esc(label)}</div>
      <div class="track"><div class="fill" style="width:0%"></div></div>
      <div class="pct">—</div>
    </div>
    <div style="color:var(--muted);font-size:0.85rem;margin:-0.35rem 0 0.5rem 0">${esc(note || "")}</div>`;
  }
  return `<div class="row">
    <div class="name">${esc(label)}</div>
    <div class="track"><div class="${barClass(pct)}" style="width:${Math.min(100, pct)}%"></div></div>
    <div class="pct">${pct}%</div>
  </div>
  <div style="color:var(--muted);font-size:0.85rem;margin:-0.35rem 0 0.55rem 0">${esc(note || "")}</div>`;
}

document.getElementById("lede").textContent = DATA.title;
document.getElementById("note").textContent = DATA.generated_note;

const fx = DATA.control_fixture;
document.getElementById("fixture-kpis").innerHTML = `
  <div class="kpi"><div class="label">Deny-smoke</div><div class="value ok">${esc(fx.deny_smoke)}</div></div>
  <div class="kpi"><div class="label">Pytest</div><div class="value ok">${esc(fx.pytest_passed)} passed</div></div>
  <div class="kpi"><div class="label">Notes (no guest)</div><div class="value">${esc(fx.notes_without_guest)}</div></div>
  <div class="kpi"><div class="label">Notes (guest)</div><div class="value">${esc(fx.notes_with_guest)}</div></div>
  <div class="kpi"><div class="label">Admin export</div><div class="value">${esc(fx.admin_export_with_guest)}</div></div>
`;

const sa = DATA.system_a_sanitized;
document.getElementById("system-kpis").innerHTML = `
  <div class="kpi"><div class="label">Unauth mutating</div><div class="value">${esc(sa.unauth_mutating_often)}</div></div>
  <div class="kpi"><div class="label">Guest lists</div><div class="value">${esc(sa.guest_lists)}</div></div>
  <div class="kpi"><div class="label">Upload w/o full auth</div><div class="value">${esc(sa.upload_without_full_auth)}</div></div>
  <div class="kpi"><div class="label">Planted IDOR</div><div class="value">${esc(sa.cross_user_planted_secret_idor)}</div></div>
  <div class="kpi"><div class="label">Evil / metadata</div><div class="value ok">${esc(sa.egress_evil_metadata)}</div></div>
`;

const tool = DATA.tool_attempt_suite;
document.getElementById("tool-sub").textContent =
  `${tool.description} (~${tool.n_prompts_per_model} prompts × ${tool.n_models} arms). Higher bar = more attempts.`;
document.getElementById("tool-chart").innerHTML = tool.arms
  .map(a => renderBar(a.label, a.attempt_rate_pct, a.note))
  .join("");

const rta = DATA.reason_then_act_suite;
document.getElementById("rta-sub").textContent =
  `${rta.description} (~${rta.n_prompts_per_model} prompts). Only arms with public numbers are drawn.`;
document.getElementById("rta-chart").innerHTML = rta.arms
  .filter(a => a.attempt_rate_pct != null)
  .map(a => renderBar(a.label, a.attempt_rate_pct, a.note))
  .join("") || "<p>No public numeric arms for this chart.</p>";

document.getElementById("takeaways").innerHTML = (DATA.takeaways || [])
  .map(t => `<li>${esc(t)}</li>`).join("");
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
