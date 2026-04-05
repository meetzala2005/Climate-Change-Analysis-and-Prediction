import requests

def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url).json()

        temp = res["current_weather"]["temperature"]
        code = res["current_weather"]["weathercode"]

        if code == 0:
            weather = "Sunny"
        elif code in [1,2,3]:
            weather = "Cloudy"
        elif code in [51,61]:
            weather = "Rain"
        else:
            weather = "Normal"

        return temp, weather
    except:
        return None, "Unknown"