from datetime import datetime

import pandas as pd
import requests
import streamlit as st


WEATHER_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    56: "Freezing drizzle",
    57: "Dense freezing drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}

WEATHER_ICONS = {
    0: "sunny",
    1: "sunny",
    2: "partly_cloudy_day",
    3: "cloud",
    45: "foggy",
    48: "foggy",
    51: "rainy",
    53: "rainy",
    55: "rainy",
    56: "rainy",
    57: "rainy",
    61: "rainy",
    63: "rainy",
    65: "rainy",
    66: "rainy",
    67: "rainy",
    71: "weather_snowy",
    73: "weather_snowy",
    75: "weather_snowy",
    77: "weather_snowy",
    80: "rainy",
    81: "rainy",
    82: "rainy",
    85: "weather_snowy",
    86: "weather_snowy",
    95: "thunderstorm",
    96: "thunderstorm",
    99: "thunderstorm",
}


def get_json(url: str, parameters: dict[str, str]) -> dict:
    response = requests.get(url, params=parameters, timeout=15)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=900, max_entries=50)
def load_weather(city: str, units: str) -> dict:
    locations = get_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": city, "count": "1", "language": "en", "format": "json"},
    ).get("results", [])
    if not locations:
        raise ValueError(
            f"No location found for '{city}'. Try another city name.")

    location = locations[0]
    is_fahrenheit = units == "Fahrenheit / mph"
    forecast = get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": str(location["latitude"]),
            "longitude": str(location["longitude"]),
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "temperature_unit": "fahrenheit" if is_fahrenheit else "celsius",
            "wind_speed_unit": "mph" if is_fahrenheit else "kmh",
            "timezone": "auto",
            "forecast_days": "5",
        },
    )
    return {"location": location, "forecast": forecast}


st.set_page_config(
    page_title="Weather, at a glance",
    page_icon=":material/partly_cloudy_day:",
    layout="wide",
)
st.title("A little closer to the sky")
st.caption("Live conditions, local details, and the shape of the next five days.")

with st.form("weather-search"):
    search_column, units_column, action_column = st.columns([3, 1.5, 1])
    city = search_column.text_input(
        "Find a place", value="London", placeholder="Try Tokyo or New York")
    units = units_column.selectbox(
        "Units", ["Celsius / km/h", "Fahrenheit / mph"])
    submitted = action_column.form_submit_button(
        "Show my forecast", type="primary", icon=":material/search:"
    )

if submitted:
    if not city.strip():
        st.warning("Enter a city to see its weather.")
    else:
        try:
            result = load_weather(city.strip(), units)
            location = result["location"]
            current = result["forecast"]["current"]
            daily = result["forecast"]["daily"]
            unit = "°F" if units == "Fahrenheit / mph" else "°C"
            speed_unit = "mph" if units == "Fahrenheit / mph" else "km/h"
            place = ", ".join(
                part
                for part in (location.get("name"), location.get("admin1"), location.get("country"))
                if part
            )

            weather_code = current["weather_code"]
            description = WEATHER_DESCRIPTIONS.get(
                weather_code, "Weather update")
            weather_icon = WEATHER_ICONS.get(weather_code, "partly_cloudy_day")

            with st.container(border=True):
                hero, conditions = st.columns(
                    [1.3, 1], vertical_alignment="center")
                with hero:
                    st.badge(
                        "RIGHT NOW", icon=":material/location_on:", color="green")
                    st.subheader(place)
                    st.markdown(f"## :material/{weather_icon}:  {description}")
                    st.metric("Temperature",
                              f"{current['temperature_2m']:.0f}{unit}")
                with conditions:
                    feels_like, humidity, wind = st.columns(3)
                    feels_like.metric(
                        "Feels like", f"{current['apparent_temperature']:.0f}{unit}")
                    humidity.metric(
                        "Humidity", f"{current['relative_humidity_2m']}%")
                    wind.metric(
                        "Wind", f"{current['wind_speed_10m']:.0f} {speed_unit}")
                    st.caption(
                        f"Local time · {current['time'].replace('T', ' ')}")

            st.subheader("The next five days")
            st.caption(
                "A small look at the highs, lows, and chance of rain ahead.")
            forecast_rows = []
            for index, date in enumerate(daily["time"]):
                code = daily["weather_code"][index]
                forecast_rows.append(
                    {
                        "Day": datetime.fromisoformat(date).strftime("%a, %b %d"),
                        "Conditions": WEATHER_DESCRIPTIONS.get(code, "Variable conditions"),
                        "High": f"{daily['temperature_2m_max'][index]:.0f}{unit}",
                        "Low": f"{daily['temperature_2m_min'][index]:.0f}{unit}",
                        "Rain chance": f"{daily['precipitation_probability_max'][index] or 0}%",
                    }
                )
            chart_data = pd.DataFrame(
                {
                    "Day": [datetime.fromisoformat(date) for date in daily["time"]],
                    "High": daily["temperature_2m_max"],
                    "Low": daily["temperature_2m_min"],
                }
            ).set_index("Day")
            st.line_chart(chart_data, y_label=f"Temperature ({unit})")
            st.dataframe(forecast_rows, hide_index=True, width="stretch")
        except requests.RequestException as error:
            st.error(f"Could not reach the weather service: {error}")
        except (KeyError, ValueError) as error:
            st.error(
                str(error) or "The weather service returned an unexpected response.")
