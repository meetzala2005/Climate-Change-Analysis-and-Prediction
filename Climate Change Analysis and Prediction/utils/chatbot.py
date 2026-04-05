def fallback_response(query, city, weather):
    if "weather" in query:
        return f"Weather in {city} is {weather}"
    elif "temperature" in query:
        return "Temperature is increasing globally"
    elif "co2" in query:
        return "CO2 causes global warming"
    else:
        return "Climate change is serious issue"