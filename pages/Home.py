import streamlit as st
import streamlit.components.v1 as components
from utils.ui_components import GLOBAL_CSS
from utils.auto_retrain import get_retrain_log

st.set_page_config(
    page_title="SafeRoute AI — Road Risk Navigator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── retrain log for ticker ────────────────────────────────────────────────────
logs      = get_retrain_log()
last_log  = logs[-1] if logs else None
acc_val   = f"{last_log['accuracy']}%" if last_log else "69.2%"
last_time = last_log['timestamp'][:16].replace('T', ' ') if last_log else "Pending"

# ── HERO ──────────────────────────────────────────────────────────────────────
pulse_dots = "".join([
    f'<div style="position:absolute;left:{x}%;top:{y}%;width:8px;height:8px;border-radius:50%;'
    f'background:{c};box-shadow:0 0 12px {c};'
    f'animation:pulse-ring {d}s ease-out infinite;animation-delay:{dl}s"></div>'
    for x,y,c,d,dl in [
        (15,35,"#FF3B3B",2.5,0),(72,28,"#FF3B3B",3,0.5),(55,60,"#FF8C42",2.8,1),
        (30,70,"#FF3B3B",2.2,0.3),(85,55,"#FF8C42",3.2,0.8),(42,20,"#FF3B3B",2.6,1.2),
        (65,75,"#FF8C42",2.9,0.6),(20,55,"#FF3B3B",2.4,0.9),(78,42,"#FF3B3B",3.1,0.2),
        (50,40,"#FF8C42",2.7,1.5),(35,45,"#FF3B3B",2.3,0.4),(60,30,"#FF8C42",3.0,1.1),
    ]
])

st.markdown(f"""
<div style="
  position:relative;min-height:100vh;
  background:radial-gradient(ellipse at 20% 50%,rgba(0,212,255,.06) 0%,transparent 60%),
             radial-gradient(ellipse at 80% 20%,rgba(255,59,59,.06) 0%,transparent 55%),
             #0A0A0F;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:80px 40px 120px;overflow:hidden;
">
  <div style="
    position:absolute;inset:0;
    background-image:
      linear-gradient(rgba(0,212,255,.04) 1px,transparent 1px),
      linear-gradient(90deg,rgba(0,212,255,.04) 1px,transparent 1px);
    background-size:60px 60px;
    mask-image:radial-gradient(ellipse at center,black 30%,transparent 80%);
  "></div>

  <div style="position:absolute;inset:0;overflow:hidden;pointer-events:none">
    {pulse_dots}
  </div>

  <div style="
    font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:3px;
    color:#00D4FF;text-transform:uppercase;margin-bottom:20px;
    border:1px solid rgba(0,212,255,.2);border-radius:20px;
    padding:5px 16px;background:rgba(0,212,255,.06);
    animation:fadeSlideUp .6s ease both;
  ">
    <i class="fa-solid fa-satellite-dish" style="margin-right:6px"></i>
    AI-POWERED ROAD RISK PREDICTION
  </div>

  <div style="
    font-family:'Orbitron',monospace;font-size:clamp(2rem,5vw,4rem);
    font-weight:900;text-align:center;line-height:1.1;
    letter-spacing:-1px;max-width:900px;
    animation:fadeSlideUp .7s ease .1s both;
  ">
    <span style="color:#F0F0F0">KNOW THE DANGER</span><br>
    <span style="
      background:linear-gradient(135deg,#FF3B3B,#FF8C42);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    ">BEFORE YOU DRIVE</span>
  </div>

  <div style="
    font-family:'Rajdhani',sans-serif;font-size:1.15rem;
    color:#8A8A9A;text-align:center;max-width:620px;
    margin:18px 0 40px;line-height:1.6;font-weight:500;
    animation:fadeSlideUp .7s ease .2s both;
  ">
    Real-time accident risk prediction across India's most dangerous road corridors
    — powered by machine learning, live weather, and AI safety intelligence.
  </div>

  <div style="animation:fadeSlideUp .7s ease .3s both">
    <a href="/Driver_Alert" target="_self" style="
      display:inline-flex;align-items:center;gap:10px;
      background:linear-gradient(135deg,rgba(0,212,255,.15),rgba(0,212,255,.05));
      border:1px solid rgba(0,212,255,.4);
      color:#00D4FF;text-decoration:none;
      font-family:'Orbitron',monospace;font-size:.82rem;font-weight:700;
      letter-spacing:2px;padding:14px 32px;border-radius:12px;
      box-shadow:0 0 30px rgba(0,212,255,.2);
      transition:all .3s;
    " onmouseover="this.style.boxShadow='0 0 50px rgba(0,212,255,.45)';this.style.transform='translateY(-2px)'"
       onmouseout="this.style.boxShadow='0 0 30px rgba(0,212,255,.2)';this.style.transform='none'">
      <i class="fa-solid fa-route"></i>
      ANALYZE MY ROUTE
      <i class="fa-solid fa-arrow-right"></i>
    </a>
  </div>

</div>
""", unsafe_allow_html=True)

# ── ANIMATED STAT COUNTERS ────────────────────────────────────────────────────
components.html("""
<div style="
  background:linear-gradient(180deg,#0A0A0F 0%,#0D0D14 100%);
  padding:50px 40px;
  border-top:1px solid rgba(0,212,255,.1);
  border-bottom:1px solid rgba(0,212,255,.1);
">
  <div style="
    max-width:1100px;margin:0 auto;
    display:grid;grid-template-columns:repeat(4,1fr);gap:20px;
  ">
    <div class="stat-card" data-target="20000" data-suffix="+" data-label="ACCIDENTS ANALYZED" data-color="#00D4FF"></div>
    <div class="stat-card" data-target="1126"  data-suffix=""  data-label="HOTSPOTS MAPPED"    data-color="#FF3B3B"></div>
    <div class="stat-card" data-target="8"     data-suffix=""  data-label="CITIES COVERED"     data-color="#FF8C42"></div>
    <div class="stat-card" data-target="100"   data-suffix="%" data-label="LIVE WEATHER"       data-color="#39FF14"></div>
  </div>
</div>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Space+Mono&display=swap');
  body { background:#0A0A0F; margin:0; }
  .stat-card {
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.08);
    border-radius:16px;padding:28px 20px;text-align:center;
    transition:transform .3s,box-shadow .3s;cursor:default;
  }
  .stat-card:hover { transform:translateY(-4px); }
  .stat-num {
    font-family:'Orbitron',monospace;font-size:2.2rem;font-weight:900;
    letter-spacing:-1px;line-height:1;margin-bottom:8px;
  }
  .stat-lbl {
    font-family:'Space Mono',monospace;font-size:.58rem;
    letter-spacing:2px;color:#8A8A9A;text-transform:uppercase;
  }
</style>

<script>
  function easeOut(t) { return 1 - Math.pow(1-t, 3); }
  document.querySelectorAll('.stat-card').forEach(card => {
    const target = parseInt(card.dataset.target);
    const suffix = card.dataset.suffix;
    const label  = card.dataset.label;
    const color  = card.dataset.color;
    card.style.borderColor = color + '22';
    card.style.boxShadow   = '0 0 30px ' + color + '15';
    const numEl = document.createElement('div');
    numEl.className = 'stat-num';
    numEl.style.color = color;
    numEl.style.textShadow = '0 0 20px ' + color + '60';
    const lblEl = document.createElement('div');
    lblEl.className = 'stat-lbl';
    lblEl.textContent = label;
    card.appendChild(numEl);
    card.appendChild(lblEl);
    let start = null;
    const dur = target > 1000 ? 2200 : 1400;
    function animate(ts) {
      if (!start) start = ts;
      const prog = Math.min((ts - start) / dur, 1);
      const val  = Math.floor(easeOut(prog) * target);
      numEl.textContent = (val >= 1000 ? val.toLocaleString() : val) + suffix;
      if (prog < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  });
</script>
""", height=230)

# ── HOW IT WORKS ──────────────────────────────────────────────────────────────
components.html("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@500;600;700&family=Space+Mono&display=swap" rel="stylesheet">

<div style="padding:60px 40px;background:#0A0A0F">
  <div style="text-align:center;margin-bottom:48px">
    <div style="font-family:'Space Mono',monospace;font-size:.65rem;
                letter-spacing:3px;color:#00D4FF;margin-bottom:12px">HOW IT WORKS</div>
    <div style="font-family:'Orbitron',monospace;font-size:1.6rem;
                font-weight:700;color:#F0F0F0">THREE STEPS TO SAFER DRIVING</div>
  </div>

  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;max-width:1000px;margin:0 auto">

    <div class="how-card" style="--c:#00D4FF">
      <div class="how-num">01</div>
      <div class="how-icon"><i class="fa-solid fa-map-location-dot"></i></div>
      <div class="how-title">ENTER YOUR ROUTE</div>
      <div class="how-desc">Type any From and To location in India. Our geocoder resolves the address to GPS coordinates in real time.</div>
    </div>

    <div class="how-card" style="--c:#FF8C42">
      <div class="how-num">02</div>
      <div class="how-icon"><i class="fa-solid fa-brain"></i></div>
      <div class="how-title">AI SCANS 1,126 HOTSPOTS</div>
      <div class="how-desc">OSRM plots your exact road path. Our vectorized engine checks every hotspot against your route in milliseconds.</div>
    </div>

    <div class="how-card" style="--c:#FF3B3B">
      <div class="how-num">03</div>
      <div class="how-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>
      <div class="how-title">GET REAL-TIME ALERTS</div>
      <div class="how-desc">Gemini AI writes a contextual safety brief per hotspot combining accident history, live weather, and primary causes.</div>
    </div>

  </div>
</div>

<style>
body { background:#0A0A0F; margin:0; }
.how-card {
  background:rgba(255,255,255,.03);
  border:1px solid rgba(255,255,255,.07);
  border-top:3px solid var(--c);
  border-radius:16px;padding:30px 24px;
  text-align:center;position:relative;overflow:hidden;
  transition:transform .3s,box-shadow .3s;
}
.how-card:hover {
  transform:translateY(-6px);
  box-shadow:0 12px 40px rgba(0,0,0,.4);
}
.how-num {
  font-family:'Orbitron',monospace;font-size:3rem;font-weight:900;
  color:var(--c);opacity:.15;line-height:1;margin-bottom:16px;
}
.how-icon {
  font-size:1.8rem;color:var(--c);margin-bottom:14px;
}
.how-title {
  font-family:'Orbitron',monospace;font-size:.72rem;font-weight:700;
  letter-spacing:1.5px;color:#F0F0F0;margin-bottom:12px;
}
.how-desc {
  font-family:'Rajdhani',sans-serif;font-size:.92rem;
  color:#8A8A9A;line-height:1.6;font-weight:500;
}
</style>
""", height=420)

# ── COMPARISON TABLE ──────────────────────────────────────────────────────────
rows_html = "".join([f"""
    <div class="cmp-row" style="display:grid;grid-template-columns:2fr 1.5fr 1.5fr;
                border-bottom:1px solid rgba(255,255,255,.04)">
      <div style="padding:14px 24px;font-family:'Rajdhani',sans-serif;
                  font-size:.9rem;font-weight:600;color:#8A8A9A">{feat}</div>
      <div style="padding:14px 24px;text-align:center;font-family:'Space Mono',monospace;
                  font-size:.78rem;color:#444">{gmap}</div>
      <div style="padding:14px 24px;text-align:center;font-family:'Space Mono',monospace;
                  font-size:.78rem;color:#00D4FF">{safe}</div>
    </div>"""
    for feat, gmap, safe in [
        ("Data Source",     "Govt black-spot DB",    "20,000 ML records"),
        ("Weather Factor",  "None",                  "Live OpenWeatherMap"),
        ("Alert Type",      "Fixed zone warning",    "AI-generated brief"),
        ("Model Updates",   "Manual by Google",      "Auto every 24hrs"),
        ("Hotspot Accuracy","On/off flag",            "Prob. score + cause"),
        ("Route Checking",  "Nearest fixed zone",    "Closest road point"),
    ]
])

components.html(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@500;600;700&family=Space+Mono&display=swap" rel="stylesheet">

<div style="padding:60px 40px;background:linear-gradient(180deg,#0A0A0F,#0D0D16,#0A0A0F)">
  <div style="text-align:center;margin-bottom:48px">
    <div style="font-family:'Space Mono',monospace;font-size:.65rem;
                letter-spacing:3px;color:#FF3B3B;margin-bottom:12px">WHY SAFEROUTE</div>
    <div style="font-family:'Orbitron',monospace;font-size:1.6rem;
                font-weight:700;color:#F0F0F0">BEYOND GOOGLE MAPS</div>
  </div>

  <div style="max-width:820px;margin:0 auto;border-radius:16px;overflow:hidden;
              border:1px solid rgba(255,255,255,.07)">

    <div style="display:grid;grid-template-columns:2fr 1.5fr 1.5fr;
                background:rgba(255,255,255,.05);border-bottom:1px solid rgba(255,255,255,.07)">
      <div style="padding:16px 24px;font-family:'Space Mono',monospace;
                  font-size:.65rem;letter-spacing:2px;color:#8A8A9A">FEATURE</div>
      <div style="padding:16px 24px;text-align:center;font-family:'Space Mono',monospace;
                  font-size:.65rem;letter-spacing:2px;color:#555">GOOGLE MAPS</div>
      <div style="padding:16px 24px;text-align:center;font-family:'Orbitron',monospace;
                  font-size:.65rem;letter-spacing:2px;color:#00D4FF">SAFEROUTE AI</div>
    </div>

    {rows_html}
  </div>
</div>

<style>
body {{ background:#0A0A0F; margin:0; }}
.cmp-row {{ transition:background .2s; }}
.cmp-row:hover {{ background:rgba(0,212,255,.03); }}
</style>
""", height=560)

# ── LIVE TICKER ───────────────────────────────────────────────────────────────
ticker_items = " &nbsp;&nbsp;|&nbsp;&nbsp; ".join([
    f'<span style="color:#FF3B3B"><i class="fa-solid fa-circle" style="font-size:.4rem;vertical-align:middle;margin-right:6px"></i>LAST RETRAIN: {last_time}</span>',
    f'<span style="color:#00D4FF"><i class="fa-solid fa-microchip" style="margin-right:6px"></i>MODEL ACCURACY: {acc_val}</span>',
    '<span style="color:#39FF14"><i class="fa-solid fa-cloud-sun-rain" style="margin-right:6px"></i>WEATHER: LIVE INTEGRATION</span>',
    '<span style="color:#FF8C42"><i class="fa-solid fa-city" style="margin-right:6px"></i>CITIES: 8 ACTIVE</span>',
    '<span style="color:#00D4FF"><i class="fa-solid fa-database" style="margin-right:6px"></i>HOTSPOTS: 1,126 INDEXED</span>',
    '<span style="color:#FF3B3B"><i class="fa-solid fa-triangle-exclamation" style="margin-right:6px"></i>HIGH RISK ZONES: 55</span>',
    '<span style="color:#39FF14"><i class="fa-solid fa-bolt" style="margin-right:6px"></i>RETRAIN: DAILY AT 02:00</span>',
] * 2)

st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<div style="
  background:#06060A;
  border-top:1px solid rgba(0,212,255,.12);
  border-bottom:1px solid rgba(0,212,255,.12);
  padding:12px 0;overflow:hidden;position:relative;
">
  <div style="
    display:inline-flex;gap:60px;white-space:nowrap;
    animation:ticker-scroll 30s linear infinite;
    font-family:'Space Mono',monospace;font-size:.72rem;
    letter-spacing:1px;
  ">
    {ticker_items}
  </div>
</div>
""", unsafe_allow_html=True)

# ── BOTTOM CTA ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  padding:80px 40px;text-align:center;
  background:radial-gradient(ellipse at center,rgba(0,212,255,.05) 0%,transparent 70%),#0A0A0F;
">
  <div style="font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:700;
              color:#F0F0F0;margin-bottom:12px">READY TO CHECK YOUR ROUTE?</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;
              color:#8A8A9A;margin-bottom:32px">
    Enter your origin and destination — get AI risk analysis in seconds.
  </div>
  <a href="/Driver_Alert" target="_self" style="
    display:inline-flex;align-items:center;gap:10px;
    background:linear-gradient(135deg,#FF3B3B,#FF6B3B);
    color:#fff;text-decoration:none;
    font-family:'Orbitron',monospace;font-size:.8rem;font-weight:700;
    letter-spacing:2px;padding:15px 36px;border-radius:12px;
    box-shadow:0 0 40px rgba(255,59,59,.35);
    transition:all .3s;
  " onmouseover="this.style.boxShadow='0 0 60px rgba(255,59,59,.6)';this.style.transform='translateY(-3px)'"
     onmouseout="this.style.boxShadow='0 0 40px rgba(255,59,59,.35)';this.style.transform='none'">
    <i class="fa-solid fa-shield-halved"></i>
    START ROUTE ANALYSIS
    <i class="fa-solid fa-arrow-right"></i>
  </a>
</div>
""", unsafe_allow_html=True)
