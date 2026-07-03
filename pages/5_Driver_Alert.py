import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime

from utils.hotspot_engine import load_hotspots, build_hotspots, _load_ds1
from utils.risk_model import train_model, load_or_train
from utils.route_analyzer import geocode, get_road_route, find_hotspots_on_route
from utils.ai_description import get_live_weather, generate_alert_description
from utils.auto_retrain import start_scheduler, get_retrain_log
from utils.ui_components import GLOBAL_CSS
from config import WARN_RADIUS_M

st.set_page_config(
    page_title="SafeRoute — Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── init ──────────────────────────────────────────────────────────────────────
start_scheduler()

if "hotspots" not in st.session_state:
    with st.spinner("Indexing hotspot database..."):
        st.session_state["hotspots"] = load_hotspots()
if "clf" not in st.session_state:
    with st.spinner("Loading risk model..."):
        df = _load_ds1()
        st.session_state["clf"]      = load_or_train(df)
        st.session_state["train_df"] = df
if "satellite" not in st.session_state:
    st.session_state["satellite"] = False
if "_from_val" not in st.session_state:
    st.session_state["_from_val"] = ""
if "_to_val" not in st.session_state:
    st.session_state["_to_val"] = ""

hotspots = st.session_state["hotspots"]
high_hs  = len(hotspots[hotspots["risk_level"] == "HIGH"])
med_hs   = len(hotspots[hotspots["risk_level"] == "MEDIUM"])

# ── TOP NAV ───────────────────────────────────────────────────────────────────
components.html(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Space+Mono&display=swap" rel="stylesheet">
<div style="
  background:linear-gradient(180deg,#06060E 0%,rgba(6,6,14,.95) 100%);
  border-bottom:1px solid rgba(0,212,255,.12);
  padding:0 28px;height:62px;
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:100;
  backdrop-filter:blur(12px);
">
  <div style="display:flex;align-items:center;gap:14px">
    <div style="width:36px;height:36px;border-radius:50%;
      background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.3);
      display:flex;align-items:center;justify-content:center;
      box-shadow:0 0 16px rgba(0,212,255,.2)">
      <i class="fa-solid fa-shield-halved" style="color:#00D4FF;font-size:.9rem"></i>
    </div>
    <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;
                letter-spacing:2px;color:#F0F0F0">
      SAFE<span style="color:#00D4FF">ROUTE</span>
    </div>
    <div style="background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.2);
      border-radius:4px;padding:2px 8px;
      font-family:'Space Mono',monospace;font-size:.58rem;
      letter-spacing:1.5px;color:#00D4FF;">AI NAVIGATOR</div>
  </div>
  <div style="display:flex;gap:10px;align-items:center">
    <div style="display:inline-flex;align-items:center;gap:8px;
      background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.25);
      border-radius:8px;padding:6px 14px">
      <i class="fa-solid fa-database" style="color:#00D4FF;font-size:.72rem"></i>
      <div>
        <div style="font-family:'Orbitron',monospace;font-size:.78rem;font-weight:700;color:#00D4FF">{len(hotspots)}</div>
        <div style="font-family:'Space Mono',monospace;font-size:.58rem;color:rgba(0,212,255,.7)">HOTSPOTS</div>
      </div>
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;
      background:rgba(255,59,59,.08);border:1px solid rgba(255,59,59,.25);
      border-radius:8px;padding:6px 14px">
      <i class="fa-solid fa-circle-exclamation" style="color:#FF3B3B;font-size:.72rem"></i>
      <div>
        <div style="font-family:'Orbitron',monospace;font-size:.78rem;font-weight:700;color:#FF3B3B">{high_hs}</div>
        <div style="font-family:'Space Mono',monospace;font-size:.58rem;color:rgba(255,59,59,.7)">HIGH RISK</div>
      </div>
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;
      background:rgba(255,140,66,.08);border:1px solid rgba(255,140,66,.25);
      border-radius:8px;padding:6px 14px">
      <i class="fa-solid fa-city" style="color:#FF8C42;font-size:.72rem"></i>
      <div>
        <div style="font-family:'Orbitron',monospace;font-size:.78rem;font-weight:700;color:#FF8C42">8</div>
        <div style="font-family:'Space Mono',monospace;font-size:.58rem;color:rgba(255,140,66,.7)">CITIES</div>
      </div>
    </div>
  </div>
</div>
""", height=70)

# ── ROUTE INPUT ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  background:linear-gradient(180deg,#0D0D16,#0A0A0F);
  padding:28px 28px 20px;
  border-bottom:1px solid rgba(0,212,255,.08);
">
  <div style="font-family:'Space Mono',monospace;font-size:.6rem;
              letter-spacing:2.5px;color:#8A8A9A;margin-bottom:14px">
    <i class="fa-solid fa-route" style="color:#00D4FF;margin-right:6px"></i>
    ROUTE CONFIGURATION
  </div>
""", unsafe_allow_html=True)

ci1, ci2, ci3, ci4 = st.columns([5, 5, 2, 1])
with ci1:
    from_txt = st.text_input("from", placeholder="FROM — origin city or address",
                              label_visibility="collapsed", key="from_inp",
                              value=st.session_state["_from_val"])
with ci2:
    to_txt = st.text_input("to", placeholder="TO — destination city or address",
                            label_visibility="collapsed", key="to_inp",
                            value=st.session_state["_to_val"])
with ci3:
    go = st.button("SCAN ROUTE", use_container_width=True, type="primary")
with ci4:
    if st.button("SAT" if not st.session_state["satellite"] else "MAP",
                 use_container_width=True, key="sat_btn"):
        st.session_state["satellite"] = not st.session_state["satellite"]
        st.rerun()

# city quick-select pills
st.markdown("""
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;padding-bottom:4px">
  <span style="font-family:'Space Mono',monospace;font-size:.58rem;
               letter-spacing:1.5px;color:#8A8A9A;align-self:center">QUICK SELECT:</span>
""", unsafe_allow_html=True)

cities = ["Chennai","Mumbai","Delhi","Bangalore","Hyderabad","Pune","Kolkata","Chandigarh"]
pill_cols = st.columns(len(cities))
for i, city in enumerate(cities):
    with pill_cols[i]:
        if st.button(city, key=f"city_{i}", use_container_width=True):
            st.session_state["_from_val"] = city
            st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)

# ── ROUTE LOGIC ───────────────────────────────────────────────────────────────
if go:
    if not from_txt.strip() or not to_txt.strip():
        st.warning("Enter both From and To locations.")
    else:
        steps = [
            "Geocoding locations...",
            "Fetching road segments from OSRM...",
            "Scanning 1,126 accident hotspots...",
            "Fetching live weather data...",
            "Generating AI safety briefs...",
            "Route analysis complete.",
        ]
        prog = st.progress(0)
        status_box = st.empty()

        status_box.markdown(f"""
        <div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);
                    border-radius:10px;padding:12px 18px;
                    font-family:'Space Mono',monospace;font-size:.75rem;
                    color:#00D4FF;letter-spacing:.5px">
          <i class="fa-solid fa-circle-notch fa-spin" style="margin-right:8px"></i>
          {steps[0]}
        </div>""", unsafe_allow_html=True)

        start_c = geocode(from_txt.strip())
        prog.progress(15)
        end_c   = geocode(to_txt.strip())
        prog.progress(30)

        if not start_c:
            st.error(f"Cannot geocode: {from_txt}")
            prog.empty(); status_box.empty(); st.stop()
        if not end_c:
            st.error(f"Cannot geocode: {to_txt}")
            prog.empty(); status_box.empty(); st.stop()

        status_box.markdown(f"""
        <div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);
                    border-radius:10px;padding:12px 18px;
                    font-family:'Space Mono',monospace;font-size:.75rem;
                    color:#00D4FF;letter-spacing:.5px">
          <i class="fa-solid fa-circle-notch fa-spin" style="margin-right:8px"></i>
          {steps[1]}
        </div>""", unsafe_allow_html=True)

        route = get_road_route(start_c, end_c)
        prog.progress(55)

        status_box.markdown(f"""
        <div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);
                    border-radius:10px;padding:12px 18px;
                    font-family:'Space Mono',monospace;font-size:.75rem;
                    color:#00D4FF;letter-spacing:.5px">
          <i class="fa-solid fa-circle-notch fa-spin" style="margin-right:8px"></i>
          {steps[2]}
        </div>""", unsafe_allow_html=True)

        alerts = find_hotspots_on_route(route, hotspots, WARN_RADIUS_M)
        prog.progress(70)

        status_box.markdown(f"""
        <div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);
                    border-radius:10px;padding:12px 18px;
                    font-family:'Space Mono',monospace;font-size:.75rem;
                    color:#00D4FF;letter-spacing:.5px">
          <i class="fa-solid fa-circle-notch fa-spin" style="margin-right:8px"></i>
          {steps[3]}
        </div>""", unsafe_allow_html=True)

        mid_pt  = route[len(route) // 2]
        weather = get_live_weather(mid_pt[0], mid_pt[1])
        prog.progress(85)

        status_box.markdown(f"""
        <div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);
                    border-radius:10px;padding:12px 18px;
                    font-family:'Space Mono',monospace;font-size:.75rem;
                    color:#00D4FF;letter-spacing:.5px">
          <i class="fa-solid fa-circle-notch fa-spin" style="margin-right:8px"></i>
          {steps[4]}
        </div>""", unsafe_allow_html=True)

        enriched = []
        for a in alerts:
            desc = generate_alert_description(a, weather)
            enriched.append({**a, "weather": weather, "ai_desc": desc})
        prog.progress(100)

        status_box.markdown(f"""
        <div style="background:rgba(57,255,20,.05);border:1px solid rgba(57,255,20,.2);
                    border-radius:10px;padding:12px 18px;
                    font-family:'Space Mono',monospace;font-size:.75rem;
                    color:#39FF14;letter-spacing:.5px">
          <i class="fa-solid fa-circle-check" style="margin-right:8px"></i>
          {steps[5]}
        </div>""", unsafe_allow_html=True)

        st.session_state.update({
            "route": route, "alerts": enriched,
            "start": start_c, "end": end_c,
            "start_label": from_txt.strip(),
            "end_label":   to_txt.strip(),
            "weather":     weather,
            "_from_val":   "",
            "_to_val":     "",
        })

        import time; time.sleep(0.6)
        prog.empty(); status_box.empty()
        st.rerun()

# ── SUMMARY METRICS ───────────────────────────────────────────────────────────
if "alerts" in st.session_state:
    alerts = st.session_state["alerts"]
    high_n = sum(1 for a in alerts if a["risk_level"] == "HIGH")
    med_n  = sum(1 for a in alerts if a["risk_level"] == "MEDIUM")
    low_n  = sum(1 for a in alerts if a["risk_level"] == "LOW")
    w      = st.session_state.get("weather", {})

    st.markdown("""
    <div style="background:#0D0D16;padding:16px 28px;border-bottom:1px solid rgba(255,255,255,.06)">
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div style="background:rgba(255,59,59,.08);border:1px solid rgba(255,59,59,.2);
                    border-top:3px solid #FF3B3B;border-radius:12px;padding:16px 18px;text-align:center">
          <div style="font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;
                      color:#FF3B3B;text-shadow:0 0 20px rgba(255,59,59,.5)">{high_n}</div>
          <div style="font-family:'Space Mono',monospace;font-size:.6rem;
                      letter-spacing:1.5px;color:#8A8A9A;margin-top:4px">HIGH RISK ZONES</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div style="background:rgba(255,140,66,.08);border:1px solid rgba(255,140,66,.2);
                    border-top:3px solid #FF8C42;border-radius:12px;padding:16px 18px;text-align:center">
          <div style="font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;
                      color:#FF8C42;text-shadow:0 0 20px rgba(255,140,66,.5)">{med_n}</div>
          <div style="font-family:'Space Mono',monospace;font-size:.6rem;
                      letter-spacing:1.5px;color:#8A8A9A;margin-top:4px">MEDIUM RISK ZONES</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div style="background:rgba(57,255,20,.06);border:1px solid rgba(57,255,20,.15);
                    border-top:3px solid #39FF14;border-radius:12px;padding:16px 18px;text-align:center">
          <div style="font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;
                      color:#39FF14;text-shadow:0 0 20px rgba(57,255,20,.4)">{low_n}</div>
          <div style="font-family:'Space Mono',monospace;font-size:.6rem;
                      letter-spacing:1.5px;color:#8A8A9A;margin-top:4px">LOW RISK ZONES</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div style="background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.15);
                    border-top:3px solid #00D4FF;border-radius:12px;padding:16px 18px;text-align:center">
          <div style="font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:700;
                      color:#00D4FF;text-shadow:0 0 20px rgba(0,212,255,.4);line-height:1.3">
            {w.get('description','—')}<br>{w.get('temp',0):.0f}°C
          </div>
          <div style="font-family:'Space Mono',monospace;font-size:.6rem;
                      letter-spacing:1.5px;color:#8A8A9A;margin-top:4px">LIVE WEATHER</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── MAP ───────────────────────────────────────────────────────────────────────
def _add_tiles(m, satellite):
    if satellite:
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery", name="Satellite", max_zoom=19,
        ).add_to(m)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
            attr="Esri Labels", name="Labels", overlay=True, opacity=0.9,
        ).add_to(m)
    else:
        folium.TileLayer(tiles="CartoDB positron", name="Street").add_to(m)


def _build_map():
    sat = st.session_state.get("satellite", False)

    if "route" not in st.session_state:
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles=None)
        _add_tiles(m, sat)
        return m

    route  = st.session_state["route"]
    alerts = st.session_state["alerts"]
    start  = st.session_state["start"]
    end    = st.session_state["end"]
    s_lbl  = st.session_state["start_label"]
    e_lbl  = st.session_state["end_label"]

    mid = route[len(route) // 2]
    m   = folium.Map(location=mid, zoom_start=12, tiles=None, prefer_canvas=True)
    _add_tiles(m, sat)

    # Route glow — 3 layers
    folium.PolyLine(route, color="#00D4FF", weight=14, opacity=0.08).add_to(m)
    folium.PolyLine(route, color="#00AADD", weight=7,  opacity=0.5).add_to(m)
    folium.PolyLine(route, color="#00D4FF", weight=2,  opacity=0.95).add_to(m)

    # Risky segment overlays
    step = max(1, len(route) // 60)
    for a in alerts:
        clr = "#FF3B3B" if a["risk_level"] == "HIGH" else "#FF8C42"
        idx = a["route_idx"]
        seg = route[max(0, idx - step * 3): idx + step * 3 + 1]
        if len(seg) > 1:
            folium.PolyLine(seg, color=clr, weight=9, opacity=0.9).add_to(m)

    # Start
    folium.Marker(start, tooltip=f"START: {s_lbl}",
                  icon=folium.Icon(color="green", icon="circle", prefix="fa")).add_to(m)
    # End
    folium.Marker(end, tooltip=f"DESTINATION: {e_lbl}",
                  icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(m)

    # Pulsing hotspot markers via CSS injection
    for i, a in enumerate(alerts):
        clr   = "#FF3B3B" if a["risk_level"] == "HIGH" else "#FF8C42"
        label = "HIGH RISK" if a["risk_level"] == "HIGH" else "MEDIUM RISK"
        w_d   = a.get("weather", {})

        popup = folium.Popup(f"""
        <div style='font-family:system-ui;padding:14px;min-width:240px;
                    background:#0D0D16;color:#F0F0F0;border-radius:10px;
                    border:1px solid {clr}44'>
          <div style='color:{clr};font-weight:800;font-size:.9rem;
                      letter-spacing:.5px;margin-bottom:10px;
                      padding-bottom:8px;border-bottom:1px solid {clr}33'>
            HOTSPOT {i+1} — {label}
          </div>
          <table style='width:100%;font-size:.78rem;border-collapse:collapse'>
            <tr><td style='color:#8A8A9A;padding:3px 0'>Total Accidents</td>
                <td style='text-align:right;font-weight:700;color:#F0F0F0'>{a['total_accidents']}</td></tr>
            <tr><td style='color:#8A8A9A;padding:3px 0'>Fatal</td>
                <td style='text-align:right;font-weight:700;color:#FF3B3B'>{a['fatal']}</td></tr>
            <tr><td style='color:#8A8A9A;padding:3px 0'>Casualties</td>
                <td style='text-align:right;font-weight:700;color:#FF8C42'>{a['casualties']}</td></tr>
            <tr><td style='color:#8A8A9A;padding:3px 0'>Primary Cause</td>
                <td style='text-align:right;font-weight:600;color:#F0F0F0'>{a['top_cause'].title()}</td></tr>
            <tr><td style='color:#8A8A9A;padding:3px 0'>Peak Hour</td>
                <td style='text-align:right;font-weight:600;color:#F0F0F0'>{a['peak_hour']:02d}:00</td></tr>
            <tr><td style='color:#8A8A9A;padding:3px 0'>Weather Now</td>
                <td style='text-align:right;font-weight:600;color:#00D4FF'>{w_d.get('description','—')} {w_d.get('temp',0):.0f}°C</td></tr>
          </table>
          <div style='margin-top:10px;background:rgba(0,212,255,.08);border-radius:7px;
                      padding:9px 11px;font-size:.77rem;color:#A0A0C0;line-height:1.6;
                      border-left:3px solid #00D4FF'>
            {a['ai_desc']}
          </div>
        </div>""", max_width=320)

        # Pulsing outer ring (CSS animation via DivIcon)
        folium.Marker(
            [a["hotspot_lat"], a["hotspot_lon"]],
            icon=folium.DivIcon(html=f"""
            <div style="position:relative;width:40px;height:40px;
                        margin-left:-20px;margin-top:-20px">
              <div style="position:absolute;width:40px;height:40px;border-radius:50%;
                   border:2px solid {clr};opacity:.6;
                   animation:pulse-ring 2s ease-out infinite"></div>
              <div style="position:absolute;width:26px;height:26px;top:7px;left:7px;
                   border-radius:50%;border:2px solid {clr};opacity:.4;
                   animation:pulse-ring 2s ease-out infinite;animation-delay:.4s"></div>
            </div>
            <style>
            @keyframes pulse-ring {{
              0%   {{transform:scale(1);opacity:.8}}
              70%  {{transform:scale(2.2);opacity:0}}
              100% {{transform:scale(1);opacity:0}}
            }}
            </style>""", icon_size=(40, 40), icon_anchor=(20, 20))
        ).add_to(m)

        # Solid core dot with popup
        folium.CircleMarker(
            [a["hotspot_lat"], a["hotspot_lon"]],
            radius=8, color="#fff", fill=True,
            fill_color=clr, fill_opacity=1.0, weight=2,
            popup=popup,
            tooltip=f"HOTSPOT {i+1} — {a['total_accidents']} accidents | Click for details",
        ).add_to(m)

    return m


st.markdown('<div style="padding:0">', unsafe_allow_html=True)
st_folium(_build_map(), height=520, width=None, returned_objects=[],
          key=f"map_{st.session_state['satellite']}")
st.markdown('</div>', unsafe_allow_html=True)

# ── ALERT CARDS ───────────────────────────────────────────────────────────────
if "alerts" in st.session_state:
    alerts = st.session_state["alerts"]

    if not alerts:
        st.markdown("""
        <div style="margin:24px 28px;padding:36px;text-align:center;
                    background:rgba(57,255,20,.04);
                    border:1px solid rgba(57,255,20,.15);border-radius:16px">
          <i class="fa-solid fa-shield-halved" style="font-size:2.5rem;
             color:#39FF14;text-shadow:0 0 20px rgba(57,255,20,.5);
             display:block;margin-bottom:14px"></i>
          <div style="font-family:'Orbitron',monospace;font-size:.9rem;
                      font-weight:700;color:#39FF14;letter-spacing:1px;
                      margin-bottom:8px">ALL CLEAR</div>
          <div style="font-family:'Rajdhani',sans-serif;font-size:.95rem;
                      color:#8A8A9A;font-weight:500">
            No accident hotspots detected within 500m of your route.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding:24px 28px 8px">
          <div style="font-family:'Space Mono',monospace;font-size:.6rem;
                      letter-spacing:2.5px;color:#8A8A9A;margin-bottom:18px">
            <i class="fa-solid fa-location-crosshairs" style="color:#FF3B3B;margin-right:8px"></i>
            ACCIDENT HOTSPOT ALERTS — ALONG YOUR ROUTE
          </div>
        </div>""", unsafe_allow_html=True)

        for i, a in enumerate(alerts):
            is_high   = a["risk_level"] == "HIGH"
            clr       = "#FF3B3B" if is_high else "#FF8C42"
            bw        = "8px" if is_high else "4px"
            glow      = "rgba(255,59,59,.2)" if is_high else "rgba(255,140,66,.15)"
            badge_bg  = "rgba(255,59,59,.15)" if is_high else "rgba(255,140,66,.12)"
            badge_bd  = "rgba(255,59,59,.3)"  if is_high else "rgba(255,140,66,.25)"
            dm        = a["distance_m"]
            dist      = f"{dm}m from route" if dm < 1000 else f"{dm/1000:.1f}km from route"
            w         = a.get("weather", {})

            chips = "".join([
                f'<span style="display:inline-flex;align-items:center;gap:5px;'
                f'background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);'
                f'border-radius:20px;padding:4px 11px;font-size:.73rem;'
                f'font-family:Space Mono,monospace;color:#8A8A9A">'
                f'<i class="fa-solid fa-{ic}" style="color:{cc};font-size:.65rem"></i>{val}</span>'
                for ic, cc, val in [
                    ("chart-bar",         "#00D4FF", f"{a['total_accidents']} Accidents"),
                    ("skull-crossbones",  "#FF3B3B", f"{a['fatal']} Fatal"),
                    ("user-injured",      "#FF8C42", f"{a['casualties']} Casualties"),
                    ("clock",             "#8A8A9A", f"Peak {a['peak_hour']:02d}:00"),
                    ("bolt",              "#FF8C42", a['top_cause'].title()),
                    ("cloud-sun",         "#00D4FF", f"{w.get('description','—')} {w.get('temp',0):.0f}°C"),
                ]
            ])

            st.markdown(f"""
            <div style="
              margin:0 28px 14px;
              background:rgba(255,255,255,.03);
              border:1px solid rgba(255,255,255,.07);
              border-left:{bw} solid {clr};
              border-radius:14px;padding:20px 22px;
              box-shadow:0 4px 24px {glow};
              transition:transform .25s,box-shadow .25s;
              animation:fadeSlideUp .4s ease {i*0.08}s both;
            ">
              <div style="display:flex;justify-content:space-between;
                          align-items:flex-start;margin-bottom:14px">
                <div style="display:flex;align-items:center;gap:10px">
                  <div style="
                    background:{badge_bg};border:1px solid {badge_bd};
                    border-radius:6px;padding:4px 12px;
                    font-family:'Orbitron',monospace;font-size:.7rem;
                    font-weight:700;color:{clr};letter-spacing:1px
                  ">
                    <i class="fa-solid fa-{'circle-exclamation' if is_high else 'triangle-exclamation'}"
                       style="margin-right:6px"></i>
                    HOTSPOT {i+1} — {a['risk_level']} RISK
                  </div>
                </div>
                <div style="
                  font-family:'Space Mono',monospace;font-size:.65rem;
                  color:#8A8A9A;background:rgba(255,255,255,.04);
                  border:1px solid rgba(255,255,255,.08);border-radius:6px;
                  padding:4px 10px;white-space:nowrap
                ">
                  <i class="fa-solid fa-arrows-to-dot" style="margin-right:5px;color:#00D4FF"></i>
                  {dist}
                </div>
              </div>

              <div style="display:flex;flex-wrap:wrap;gap:7px;margin-bottom:16px">
                {chips}
              </div>

              <div style="
                background:rgba(0,212,255,.04);
                border:1px solid rgba(0,212,255,.1);
                border-left:3px solid #00D4FF;
                border-radius:10px;padding:13px 16px;
              ">
                <div style="font-family:'Space Mono',monospace;font-size:.58rem;
                            letter-spacing:2px;color:#00D4FF;margin-bottom:8px">
                  <i class="fa-solid fa-robot" style="margin-right:5px"></i>
                  AI SAFETY BRIEF
                </div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:.95rem;
                            font-weight:500;color:#A0A0C0;line-height:1.7;
                            font-style:italic">
                  {a['ai_desc']}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── TERMINAL RETRAIN LOG ──────────────────────────────────────────────────────
st.markdown('<div style="padding:8px 28px 24px">', unsafe_allow_html=True)
logs = get_retrain_log()
with st.expander("SYSTEM LOG — AUTO-RETRAIN HISTORY"):
    log_lines = ""
    if logs:
        for l in reversed(logs[-8:]):
            ts  = l['timestamp'][:16].replace('T', ' ')
            st_ = l['status'].upper()
            col = "#39FF14" if st_ == "SUCCESS" else ("#FF8C42" if st_ == "SKIPPED" else "#FF3B3B")
            log_lines += f"""
            <div style="padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04)">
              <span style="color:#555">[{ts}]</span>
              <span style="color:{col};margin-left:10px">{st_}</span>
              <span style="color:#8A8A9A;margin-left:10px">+{l['new_records']} records</span>
              <span style="color:#00D4FF;margin-left:10px">acc: {l['accuracy']}%</span>
              <span style="color:#555;margin-left:10px">// {l['note']}</span>
            </div>"""
    else:
        log_lines = '<div style="color:#555">No retrain events yet. Runs daily at 02:00.</div>'

    st.markdown(f"""
    <div style="
      background:#060608;border:1px solid rgba(57,255,20,.12);
      border-radius:12px;padding:18px 20px;
      font-family:'Space Mono',monospace;font-size:.72rem;
      line-height:1.8;max-height:240px;overflow-y:auto;
    ">
      <div style="color:#39FF14;margin-bottom:10px;font-size:.65rem;letter-spacing:1.5px">
        SAFEROUTE SYSTEM LOG v2.0 — AUTO-RETRAIN DAEMON
      </div>
      {log_lines}
    </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── REPORT FORM ───────────────────────────────────────────────────────────────
st.markdown('<div style="padding:0 28px 28px">', unsafe_allow_html=True)
with st.expander("REPORT NEW ACCIDENT — TRIGGERS MODEL RETRAIN"):
    with st.form("report_form"):
        c1, c2, c3 = st.columns(3)
        r_lat   = c1.number_input("Latitude",  value=13.0827, format="%.6f")
        r_lon   = c2.number_input("Longitude", value=80.2707, format="%.6f")
        r_sev   = c3.selectbox("Severity", ["minor", "major", "fatal"])
        c4, c5  = st.columns(2)
        r_weath = c4.selectbox("Weather", ["clear", "fog", "rain"])
        r_cause = c5.selectbox("Cause", ["weather","distraction",
                                          "overspeeding","drunk driving","poor road"])
        r_road  = st.selectbox("Road Type", ["urban","highway","rural"])
        submit  = st.form_submit_button("SUBMIT AND RETRAIN MODEL", type="primary")

    if submit:
        sev_num = {"minor": 1, "major": 2, "fatal": 3}[r_sev]
        new_row = {
            "latitude": r_lat, "longitude": r_lon,
            "severity": sev_num, "severity_raw": r_sev,
            "weather": r_weath, "road_type": r_road, "cause": r_cause,
            "casualties": 1 if sev_num >= 2 else 0, "vehicles_involved": 2,
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().strftime("%A"),
            "risk_score": round(sev_num / 3.0, 3),
            "traffic_density": "medium", "visibility": "medium",
            "is_peak_hour": 0, "alcohol": 0,
            "location_type": "Straight Road", "vehicle_type": "Car",
            "source": "reported",
        }
        base    = st.session_state.get("train_df", _load_ds1())
        updated = pd.concat([base, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state["train_df"] = updated
        with st.spinner("Retraining model and rebuilding hotspots..."):
            clf, acc = train_model(updated)
            st.session_state["clf"] = clf
            new_hs = build_hotspots()
            st.session_state["hotspots"] = new_hs
        st.success(f"Accident reported. Model accuracy: {acc*100:.1f}% | Hotspots: {len(new_hs)}")

st.markdown('</div>', unsafe_allow_html=True)
