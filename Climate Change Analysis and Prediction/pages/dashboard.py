import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Background
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to top, #0b1a2a, #1e3c72);
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Climate Dashboard")

data = pd.read_csv("data/climate_data.csv")

st.plotly_chart(
    px.line(data, x="Year", y="Temperature", title="🌡 Temperature Trend"),
    use_container_width=True
)

st.plotly_chart(
    px.line(data, x="Year", y="CO2", title="🌍 CO2 Levels"),
    use_container_width=True
)