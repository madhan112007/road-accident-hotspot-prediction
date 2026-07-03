GLOBAL_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@400;500;600;700&family=Space+Mono:wght@400;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<style>
:root {
  --bg:        #0A0A0F;
  --bg-card:   rgba(255,255,255,0.04);
  --bg-card2:  rgba(255,255,255,0.07);
  --blue:      #00D4FF;
  --red:       #FF3B3B;
  --orange:    #FF8C42;
  --green:     #39FF14;
  --text:      #F0F0F0;
  --muted:     #8A8A9A;
  --border:    rgba(255,255,255,0.08);
  --glow-red:  0 0 24px rgba(255,59,59,0.45);
  --glow-blue: 0 0 24px rgba(0,212,255,0.35);
  --glow-grn:  0 0 24px rgba(57,255,20,0.3);
}

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: var(--bg) !important; color: var(--text) !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 0 !important; max-width: 100% !important; background: var(--bg) !important; }
[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stVerticalBlock"]    { gap: 0 !important; }
section[data-testid="stSidebar"]   { background: #06060A !important; border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] * { color: var(--muted) !important; font-family: 'Space Mono', monospace !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0A0A0F; }
::-webkit-scrollbar-thumb { background: var(--blue); border-radius: 10px; }

/* ── INPUTS ── */
.stTextInput > label { display: none !important; }
.stTextInput > div > div > input {
  background: #ffffff !important;
  border: 1px solid rgba(0,212,255,0.4) !important;
  border-radius: 10px !important;
  color: #111111 !important;
  font-family: 'Rajdhani', sans-serif !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  height: 50px !important;
  padding: 0 16px !important;
  transition: all .25s !important;
  letter-spacing: .5px !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(0,212,255,0.12), var(--glow-blue) !important;
  background: #ffffff !important;
  color: #111111 !important;
}
.stTextInput > div > div > input::placeholder { color: #888888 !important; }

/* ── BUTTONS ── */
div[data-testid="stButton"] > button {
  background: transparent !important;
  border: 1px solid rgba(0,212,255,0.3) !important;
  color: var(--blue) !important;
  border-radius: 10px !important;
  font-family: 'Orbitron', monospace !important;
  font-size: .78rem !important;
  font-weight: 700 !important;
  letter-spacing: 1.5px !important;
  height: 50px !important;
  transition: all .25s !important;
}
div[data-testid="stButton"] > button:hover {
  background: rgba(0,212,255,0.1) !important;
  border-color: var(--blue) !important;
  box-shadow: var(--glow-blue) !important;
  transform: translateY(-2px) !important;
}

/* ── SELECTBOX ── */
.stSelectbox > label { display: none !important; }
.stSelectbox > div > div {
  background: rgba(0,212,255,0.04) !important;
  border: 1px solid rgba(0,212,255,0.2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Rajdhani', sans-serif !important;
}

/* ── EXPANDER ── */
div[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
div[data-testid="stExpander"] summary {
  color: var(--muted) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: .78rem !important;
}

/* ── METRIC ── */
[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 14px !important;
}
[data-testid="stMetricValue"] {
  color: var(--blue) !important;
  font-family: 'Orbitron', monospace !important;
}
[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: .7rem !important;
}

/* ── PROGRESS ── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--blue), #0088aa) !important;
  border-radius: 4px !important;
}
.stProgress > div > div {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 4px !important;
}

/* ── FORM ── */
[data-testid="stForm"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 20px !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--blue) !important; }

/* ── NUMBER INPUT ── */
.stNumberInput > label { color: #F0F0F0 !important; font-family: 'Space Mono',monospace !important; font-size:.72rem !important; }
.stNumberInput input { background: #ffffff !important; border: 1px solid rgba(0,212,255,0.3) !important; color: #111111 !important; border-radius: 8px !important; font-family: 'Space Mono',monospace !important; font-weight:600 !important; }

/* ── TICKER ANIMATION ── */
@keyframes ticker-scroll {
  0%   { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}
@keyframes pulse-ring {
  0%   { transform: scale(1);   opacity: .8; }
  70%  { transform: scale(2.4); opacity: 0;  }
  100% { transform: scale(1);   opacity: 0;  }
}
@keyframes count-up { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:none; } }
@keyframes glow-pulse { 0%,100% { box-shadow: var(--glow-red); } 50% { box-shadow: 0 0 40px rgba(255,59,59,.7); } }
@keyframes scan-line { 0% { top:0; } 100% { top:100%; } }
@keyframes fadeSlideUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:none; } }
@keyframes border-glow { 0%,100% { border-color: rgba(0,212,255,.2); } 50% { border-color: rgba(0,212,255,.6); } }
</style>
"""


TOPNAV_HTML = """
<div style="
  background: linear-gradient(180deg,#06060E 0%,rgba(6,6,14,.95) 100%);
  border-bottom: 1px solid rgba(0,212,255,.12);
  padding: 0 28px;
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky; top:0; z-index:100;
  backdrop-filter: blur(12px);
">
  <div style="display:flex;align-items:center;gap:14px">
    <div style="
      width:36px;height:36px;border-radius:50%;
      background:rgba(0,212,255,.1);
      border:1px solid rgba(0,212,255,.3);
      display:flex;align-items:center;justify-content:center;
      box-shadow:0 0 16px rgba(0,212,255,.2)
    ">
      <i class="fa-solid fa-shield-halved" style="color:#00D4FF;font-size:.9rem"></i>
    </div>
    <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;
                letter-spacing:2px;color:#F0F0F0">
      SAFE<span style="color:#00D4FF">ROUTE</span>
    </div>
    <div style="
      background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.2);
      border-radius:4px;padding:2px 8px;
      font-family:'Space Mono',monospace;font-size:.58rem;
      letter-spacing:1.5px;color:#00D4FF;
    ">AI NAVIGATOR</div>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    {badges}
  </div>
</div>
"""


def nav_badge(icon, value, label, color):
    return f"""
    <div style="
      display:inline-flex;align-items:center;gap:8px;
      background:rgba({color},.08);
      border:1px solid rgba({color},.25);
      border-radius:8px;padding:6px 14px;
    ">
      <i class="fa-solid fa-{icon}" style="color:rgb({color});font-size:.72rem"></i>
      <div>
        <div style="font-family:'Orbitron',monospace;font-size:.78rem;
                    font-weight:700;color:rgb({color});letter-spacing:.5px">{value}</div>
        <div style="font-family:'Space Mono',monospace;font-size:.58rem;
                    color:rgba({color},.7);letter-spacing:.8px">{label}</div>
      </div>
    </div>"""


def section_divider(label: str, icon: str = "circle-dot") -> str:
    return f"""
    <div style="display:flex;align-items:center;gap:12px;padding:24px 28px 14px">
      <i class="fa-solid fa-{icon}" style="color:#00D4FF;font-size:.75rem"></i>
      <div style="font-family:'Space Mono',monospace;font-size:.65rem;
                  letter-spacing:2px;text-transform:uppercase;color:#8A8A9A">{label}</div>
      <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(0,212,255,.2),transparent)"></div>
    </div>"""
