import folium
from folium.plugins import HeatMap

def create_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=5)

    heat_data = [
        [23,72],[28,77],[19,72],
        [40,-74],[51,-0.1]
    ]

    HeatMap(heat_data).add_to(m)

    folium.CircleMarker(
        location=[lat, lon],
        radius=10,
        color="blue",
        fill=True
    ).add_to(m)

    return m