import streamlit as st
import pandas as pd
import joblib
import requests
import pydeck as pdk
import plotly.graph_objects as go
import os, time, random
from openai import OpenAI
from streamlit_folium import st_folium
import folium
from utils.pdf_report import generate_pdf

st.set_page_config(layout="wide")

# ================= 🎛 BACKGROUND SELECT =================
bg_mode = st.sidebar.selectbox(
    "🌤 Select Background",
    ["Clear ☀", "Cloudy ☁", "Rainy 🌧", "Night 🌙"]
)

# ================= 🌧 RAIN =================
rain_html = ""
if bg_mode == "Rainy 🌧":
    rain_html = "".join([
        f'<div class="rain" style="left:{random.randint(0,100)}%; animation-duration:{random.uniform(0.4,0.8)}s;"></div>'
        for _ in range(120)
    ])

# ================= ☁ CLOUD =================
cloud_html = ""
if bg_mode == "Cloudy ☁":
    cloud_html = "".join([
        f'<div class="cloud" style="top:{random.randint(50,300)}px; animation-duration:{random.randint(30,60)}s;"></div>'
        for _ in range(6)
    ])

# ================= 🎨 BACKGROUND FIX =================
st.markdown(f"""
<style>

/* FIX STREAMLIT BACKGROUND */
[data-testid="stAppViewContainer"] {{
    background: {"linear-gradient(to right, #56ccf2, #2f80ed)" if bg_mode=="Clear ☀" else
                 "linear-gradient(to right, #bdc3c7, #2c3e50)" if bg_mode=="Cloudy ☁" else
                 "linear-gradient(to right, #232526, #414345)" if bg_mode=="Rainy 🌧" else
                 "linear-gradient(to right, #0f2027, #203a43, #2c5364)"};
    background-attachment: fixed;
    background-size: cover;
}}

/* 🌧 RAIN */
.rain {{
    position: fixed;
    top: -100px;
    width: 2px;
    height: 100px;
    background: rgba(255,255,255,0.4);
    animation: rainFall linear infinite;
    z-index: 1;
}}

@keyframes rainFall {{
    to {{ transform: translateY(110vh); }}
}}

/* ☁ CLOUD */
.cloud {{
    position: fixed;
    left: -200px;
    width: 200px;
    height: 60px;
    background: white;
    border-radius: 100px;
    opacity: 0.7;
    animation: moveClouds linear infinite;
    z-index: 1;
}}

@keyframes moveClouds {{
    from {{ transform: translateX(-300px); }}
    to {{ transform: translateX(110vw); }}
}}

/* MAIN CONTENT */
.block-container {{
    position: relative;
    z-index: 10;
    background: rgba(0,0,0,0.3);
    padding: 20px;
    border-radius: 20px;
}}

</style>

{rain_html}
{cloud_html}
""", unsafe_allow_html=True)

# ================= 📍 LOCATION =================
city = st.sidebar.text_input("City", "delhi")
lat, lon = 23.03, 72.58

try:
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}").json()
    if "results" in geo:
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
except:
    pass

st.write(f"📍 {city} ({lat:.2f},{lon:.2f})")

# ================= 🔮 PREDICTION =================
st.markdown("## Climate Change Analysis and Prediction")

model = joblib.load("model/model.pkl")
year = st.slider("Prediction Year", 2025, 2050, 2030)
pred = model.predict([[year, 420, 5]])[0]

if pred > 2:
    st.error(f"🔥 High Risk: {pred:.2f}")
elif pred > 1:
    st.warning(f"⚠ Medium Risk: {pred:.2f}")
else:
    st.success(f"✅ Low Risk: {pred:.2f}")

# ================= 🌍 AQI =================
pm25, temp = 50, 25

try:
    air = requests.get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=pm2_5").json()
    pm25 = int(air["hourly"]["pm2_5"][0])

    weather = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
    temp = weather["current_weather"]["temperature"]
except:
    pass

fig = go.Figure(go.Indicator(mode="gauge+number", value=pm25,
    title={'text': "AQI"},
    gauge={'axis': {'range': [0,300]}}))
st.plotly_chart(fig, use_container_width=True)

# ================= 🌍 HEATMAP =================
cities = ["Delhi","Mumbai","London","New York"]
points = []

for c in cities:
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={c}").json()
        if "results" in geo:
            lat_c = geo["results"][0]["latitude"]
            lon_c = geo["results"][0]["longitude"]
            air = requests.get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat_c}&longitude={lon_c}&hourly=pm2_5").json()
            points.append({"lat":lat_c,"lon":lon_c,"value":air["hourly"]["pm2_5"][0]})
    except:
        pass

df = pd.DataFrame(points)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1),
    layers=[pdk.Layer("HeatmapLayer", data=df, get_position='[lon,lat]', get_weight="value")]
))

# ================= 📡 NASA FIRE =================
st.markdown("## 📡 NASA Wildfire")

try:
    url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/VIIRS_SNPP_NRT/IND/1"
    df_fire = pd.read_csv(url)
    df_fire = df_fire.rename(columns={"latitude":"lat","longitude":"lon"})
    df_fire = df_fire[["lat","lon"]].dropna().head(200)

    st.pydeck_chart(pdk.Deck(
        layers=[pdk.Layer("ScatterplotLayer",
                          data=df_fire,
                          get_position='[lon,lat]',
                          get_color='[255,80,0]',
                          get_radius=50000)]
    ))
except:
    st.warning("NASA API failed")

# ================= 🌊 FLOOD =================
flood = [{"lat":p["lat"],"lon":p["lon"],
          "color":[255,0,0] if p["value"]>100 else [0,255,0]} for p in points]

st.pydeck_chart(pdk.Deck(
    layers=[pdk.Layer("ScatterplotLayer",
                      data=pd.DataFrame(flood),
                      get_position='[lon,lat]',
                      get_color='color',
                      get_radius=80000)]
))

# ================= 📡 WEATHER MAP =================
API_KEY = "YOUR_API_KEY"

m = folium.Map(location=[lat, lon], zoom_start=4)

folium.TileLayer(
    tiles=f"https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}",
    attr="Map data © OpenWeatherMap",
    name="Clouds",
    overlay=True,
    control=True
).add_to(m)

folium.LayerControl().add_to(m)
st_folium(m, height=400)

# ================= 🤖 AI =================
client = OpenAI(api_key=os.getenv(""))

q = st.text_input("Ask AI")
if q:
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":q}]
    )
    st.write(res.choices[0].message.content)

# ================= 🤖 AUTO REFRESH =================
if st.checkbox("Auto Refresh"):
    time.sleep(5)
    st.rerun()

# ================= 📄 PDF =================
if st.button("Generate PDF"):
    file = generate_pdf(year,420,5,pred)
    with open(file,"rb") as f:
        st.download_button("Download Report", f)