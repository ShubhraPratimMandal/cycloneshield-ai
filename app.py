import math
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="CycloneShield AI", page_icon="🌪️", layout="wide")

st.markdown("""
<style>
.main { background: #f6f8fb; }
.block-container { padding-top: 1.2rem; }
.hero { padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(135deg,#0b1f33 0%,#123f5a 55%,#167d9a 100%); color:white; margin-bottom:1rem; }
.hero h1 { margin:0; font-size:2.25rem; }
.hero p { margin:.45rem 0 0; color:#d9edf4; }
.metric-card { background:white; border:1px solid #e5eaf0; border-radius:15px; padding:1rem; box-shadow:0 4px 18px rgba(10,30,50,.05); }
.risk-pill { display:inline-block; padding:.35rem .75rem; border-radius:999px; font-weight:700; color:white; }
.small { color:#607080; font-size:.86rem; }
</style>
""", unsafe_allow_html=True)

LOCATIONS = {
    "Kolkata, West Bengal": {"lat":22.5726,"lon":88.3639,"elev":9,"pop":4.5,"infra":82,"coast":42},
    "Digha, West Bengal": {"lat":21.6289,"lon":87.5074,"elev":6,"pop":0.2,"infra":64,"coast":92},
    "Haldia, West Bengal": {"lat":22.0667,"lon":88.0698,"elev":7,"pop":0.2,"infra":78,"coast":76},
    "Paradip, Odisha": {"lat":20.3167,"lon":86.6167,"elev":4,"pop":0.15,"infra":84,"coast":97},
    "Puri, Odisha": {"lat":19.8135,"lon":85.8312,"elev":7,"pop":0.2,"infra":72,"coast":90},
    "Visakhapatnam, Andhra Pradesh": {"lat":17.6868,"lon":83.2185,"elev":15,"pop":2.0,"infra":86,"coast":84},
    "Chennai, Tamil Nadu": {"lat":13.0827,"lon":80.2707,"elev":6,"pop":7.1,"infra":89,"coast":76},
    "Port Blair, Andaman & Nicobar": {"lat":11.6234,"lon":92.7265,"elev":16,"pop":0.1,"infra":61,"coast":98},
}

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def risk_model(wind, rainfall, surge, duration, density, infra, elevation, coastal, preparedness):
    wind_r = clamp((wind - 60) / 130 * 100)
    rain_r = clamp(rainfall / 600 * 100)
    surge_r = clamp(surge / 7 * 100)
    duration_r = clamp((duration - 3) / 30 * 100)
    pop_r = clamp(density / 10000 * 100)
    infra_r = clamp(infra)
    elev_r = clamp(100 - elevation * 7)
    coast_r = clamp(coastal)
    prep_reduction = clamp(preparedness) * 0.30
    score = clamp(0.27*wind_r + 0.18*rain_r + 0.18*surge_r + 0.08*duration_r + 0.10*pop_r + 0.10*infra_r + 0.05*elev_r + 0.04*coast_r - prep_reduction)
    if score < 25:
        level, action = "LOW", "Routine monitoring. Keep emergency communication channels active."
    elif score < 50:
        level, action = "MODERATE", "Prepare shelters, inspect drainage and secure exposed equipment."
    elif score < 75:
        level, action = "HIGH", "Activate preparedness plans and prioritize vulnerable infrastructure."
    else:
        level, action = "CRITICAL", "Immediate response readiness. Consider evacuation of high-exposure zones."
    components = {"Wind intensity":wind_r,"Rainfall":rain_r,"Storm surge":surge_r,"Population exposure":pop_r,"Infrastructure vulnerability":infra_r,"Low elevation":elev_r,"Coastal exposure":coast_r,"Duration":duration_r}
    return score, level, action, components

st.sidebar.title("🌪️ CycloneShield AI")
st.sidebar.caption("Cyclone Impact & Infrastructure Vulnerability Forecaster")
scenario = st.sidebar.selectbox("Scenario", ["Custom assessment","Severe Bay of Bengal cyclone","Extreme landfall scenario","Moderate coastal storm"])
location = st.sidebar.selectbox("Assessment location", list(LOCATIONS.keys()))
loc = LOCATIONS[location]
defaults = {
    "Custom assessment": (120,350,3.0,14,4500,loc["infra"],3,loc["coast"],45),
    "Severe Bay of Bengal cyclone": (145,480,4.2,18,6000,loc["infra"],3,loc["coast"],35),
    "Extreme landfall scenario": (185,620,6.0,26,8000,min(100,loc["infra"]+8),2,min(100,loc["coast"]+5),20),
    "Moderate coastal storm": (95,220,1.5,9,3000,max(0,loc["infra"]-8),5,max(0,loc["coast"]-10),65),
}
d = defaults[scenario]
st.sidebar.subheader("Hazard parameters")
wind = st.sidebar.slider("Maximum sustained wind (km/h)", 60,220,d[0],5)
rainfall = st.sidebar.slider("24h rainfall (mm)", 0,800,d[1],10)
surge = st.sidebar.slider("Storm surge (m)", 0.0,8.0,float(d[2]),0.1)
duration = st.sidebar.slider("Expected impact duration (hours)", 3,48,d[3])
st.sidebar.subheader("Exposure & vulnerability")
population_density = st.sidebar.slider("Population density (people/km²)",100,15000,d[4],100)
infra = st.sidebar.slider("Infrastructure vulnerability index",0,100,d[5])
elevation = st.sidebar.slider("Average elevation (m)",0,20,d[6])
coastal = st.sidebar.slider("Coastal exposure index",0,100,d[7])
preparedness = st.sidebar.slider("Preparedness level",0,100,d[8])

score, level, action, components = risk_model(wind,rainfall,surge,duration,population_density,infra,elevation,coastal,preparedness)

st.markdown('<div class="hero"><h1>🌪️ CycloneShield AI</h1><p>AI-assisted cyclone impact forecasting and infrastructure vulnerability intelligence</p></div>', unsafe_allow_html=True)
c1,c2,c3,c4 = st.columns(4)
c1.metric("Overall Risk Score", f"{score:.0f}/100")
c2.metric("Risk Level", level)
c3.metric("Wind Hazard", f"{wind} km/h")
c4.metric("Storm Surge", f"{surge:.1f} m")
pill_color = {"LOW":"#2e7d32","MODERATE":"#ef9b20","HIGH":"#e85d04","CRITICAL":"#c62828"}[level]
st.markdown(f'<div style="margin:.6rem 0 1rem"><span class="risk-pill" style="background:{pill_color}">{level} RISK</span> <span style="margin-left:.6rem;color:#526170">{location}</span></div>', unsafe_allow_html=True)

left,right = st.columns([1.25,1])
with left:
    st.subheader("📊 Vulnerability drivers")
    comp_df = pd.DataFrame({"Factor":list(components.keys()),"Risk contribution":list(components.values())}).sort_values("Risk contribution",ascending=True)
    fig = px.bar(comp_df,x="Risk contribution",y="Factor",orientation="h",range_x=[0,100],text="Risk contribution",labels={"Risk contribution":"Normalized hazard / exposure score"})
    fig.update_traces(texttemplate="%{text:.0f}",textposition="outside")
    fig.update_layout(height=390,margin=dict(l=5,r=20,t=10,b=10))
    st.plotly_chart(fig,use_container_width=True)
with right:
    st.subheader("🧠 AI assessment")
    st.markdown(f'<div class="metric-card"><h3 style="margin-top:0">{level} vulnerability detected</h3><p><b>Primary assessment:</b> Combined hazard and exposure profile produces a <b>{score:.0f}/100</b> risk score.</p><p><b>Recommended action:</b> {action}</p><p class="small">This prototype uses a transparent weighted model so the score can be explained to reviewers and emergency planners.</p></div>', unsafe_allow_html=True)
    st.write("**Top three risk drivers**")
    for name,value in sorted(components.items(), key=lambda x:x[1], reverse=True)[:3]:
        st.progress(int(value), text=f"{name}: {value:.0f}/100")

st.subheader("🗺️ Interactive infrastructure risk map")
st.caption("Base map: OpenStreetMap. Forecast markers are synthetic demonstration points for the selected assessment.")
np.random.seed(42)
m = folium.Map(location=[loc["lat"],loc["lon"]],zoom_start=9,tiles="OpenStreetMap",control_scale=True)
folium.Marker([loc["lat"],loc["lon"]],tooltip=f"{location}: {score:.0f}/100 {level}",popup=f"<b>{location}</b><br>Risk score: {score:.0f}/100<br>Risk level: {level}",icon=folium.Icon(color="red" if score>=50 else "orange",icon="warning-sign")).add_to(m)
for _ in range(55):
    lat,lon = loc["lat"]+np.random.normal(0,.18), loc["lon"]+np.random.normal(0,.20)
    rs = clamp(score*np.random.uniform(.72,1.25))
    lc = "Critical" if rs>=75 else "High" if rs>=50 else "Moderate" if rs>=25 else "Low"
    color = "#c62828" if rs>=75 else "#e85d04" if rs>=50 else "#ef9b20" if rs>=25 else "#2e7d32"
    folium.CircleMarker([lat,lon],radius=5,color=color,fill=True,fill_color=color,fill_opacity=.55,weight=1,tooltip=f"{lc} risk • {rs:.0f}/100").add_to(m)
st_folium(m,height=470,use_container_width=True)

st.subheader("🏗️ Critical infrastructure exposure")
infra_data = pd.DataFrame([
    ["Hospitals & health facilities", clamp(infra+4), "Medical continuity / access"],
    ["Power infrastructure", clamp(infra+9), "Grid failure / outage"],
    ["Road & bridge network", clamp(infra+2), "Flooding / debris / access"],
    ["Water & drainage", clamp(infra+7), "Urban flooding / contamination"],
    ["Telecommunications", clamp(infra-3), "Connectivity disruption"],
    ["Schools & shelters", clamp(infra-5), "Evacuation capacity"],
],columns=["Infrastructure","Vulnerability","Main concern"])
infra_data["Risk"] = infra_data["Vulnerability"].apply(lambda v: "Critical" if v>=75 else "High" if v>=50 else "Moderate" if v>=25 else "Low")
st.dataframe(infra_data,use_container_width=True,hide_index=True)

st.subheader("🚨 Recommended preparedness priorities")
recs=[]
if wind>=140: recs.append("Inspect roofs, transmission lines, towers and other wind-sensitive assets.")
if rainfall>=350: recs.append("Pre-position drainage pumps and inspect flood-prone transport corridors.")
if surge>=3: recs.append("Prioritize coastal evacuation routes and low-elevation critical facilities.")
if population_density>=5000: recs.append("Increase shelter, public-warning and evacuation capacity in dense zones.")
if infra>=75: recs.append("Prioritize high-vulnerability infrastructure for pre-landfall inspection.")
if preparedness<50: recs.append("Raise preparedness level through emergency drills, supplies and communications.")
if not recs: recs.append("Continue routine monitoring and maintain emergency communication readiness.")
for i,r in enumerate(recs,1): st.markdown(f"**{i}.** {r}")

with st.expander("🔬 Model methodology"):
    st.write("CycloneShield AI normalizes hazard and exposure indicators to a 0–100 scale and combines them using transparent weights. Preparedness reduces the resulting score. This is a hackathon decision-support prototype, not an official warning system.")
    st.code("""Risk Score =
27% Wind + 18% Rainfall + 18% Storm surge + 8% Duration
+ 10% Population + 10% Infrastructure + 5% Low elevation
+ 4% Coastal exposure - Preparedness reduction
Final score is bounded to 0–100.""")
st.caption("CycloneShield AI • Track 5 prototype • Not an official emergency warning system.")
