# from dotenv import load_dotenv
# load_dotenv()

import streamlit as st
import requests
import os
import google.generativeai as genai

headers ={
    "authorization": st.secrets["auth_gemini"],
    "authorization": st.secrets["auth_weather"],
    "content-type": "application/json"
}


genai.configure(api_key=st.secrets["auth_gemini"])
# Function to fetch weather data
def get_weather_forecast(location):
    # api_key = os.getenv("WEATHER_API_KEY")
    api_key = st.secrets["auth_weather"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    print(data)
    return data

# Function to get weather forecast based on location, date, and time
def get_weather_forecast_advanced(location, date, time):
    # Here you can implement more advanced logic to get weather forecast based on date and time
    # For simplicity, I'll just call the get_weather_forecast function with the location
    return get_weather_forecast(location)

def interpret_weather_data(weather_data, date, time):
    location_name = weather_data['name']
    description = weather_data['weather'][0]['description']
    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data["wind"]["speed"]
            

    input_prompt = f"It is currently {time.strftime('%H:%M %p')} in {location_name}. "

    # Add weather description with a comma and space
    input_prompt += f"The weather is {description.lower()}, "




    # Include wind speed if available
    if wind_speed:
        input_prompt += f"and wind speeds of {wind_speed} kilometers per hour. "

    # Include humidity with a comma and space
    input_prompt += f"The humidity is {humidity}%.\n\n"

    # Include a prompt for "data-less" prediction with a specific context
    input_prompt += f"While I don't have specific weather data beyond this point, You must predict the weather for {date.strftime('%B %d, %Y')} based on historical trends and seasonal patterns?"


    # Generate interpretation using Gemma API
    model = genai.GenerativeModel('gemini-pro')
    
    # Set the maximum number of tokens for the response
    max_tokens = 100  # Adjust this value as needed
    
    response = model.generate_content(input_prompt,  generation_config=genai.types.GenerationConfig(max_output_tokens=400,))
    
    return response.text



# Initialize Streamlit app
st.set_page_config(page_title="Weather Forecast App")
st.header("Weather Forecast App")

location = st.text_input("Enter Location:", key="location")
date = st.date_input("Select Date:")
time = st.time_input("Select Time:")

submit = st.button("Get Forecast")

if submit:
    if location:
        weather_data = get_weather_forecast(location)
        
        def kelvin_to_celsius(temp_kelvin):
            return temp_kelvin - 273.15

        def celsius_to_fahrenheit(temp_celsius):
            return temp_celsius * 9/5 + 32

        # Modify the weather display section to include temperature conversions
        if 'main' in weather_data:
            temperature_kelvin = weather_data['main']['temp']
            temperature_celsius = kelvin_to_celsius(temperature_kelvin)
            temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)

            st.subheader(f"Weather Forecast for {location}:")
            st.write(f"Temperature: {temperature_celsius:.2f}°C ({temperature_fahrenheit:.2f}°F)")
            st.write(f"Description: {weather_data['weather'][0]['description']}")
            st.write(f"Humidity: {weather_data['main']['humidity']}%")
            interpretation = interpret_weather_data(weather_data, date, time)
            st.subheader("Interpreted Weather Data:")
            st.write(interpretation)

        else:
            st.write("Weather data not available for this location.")
    else:
        st.write("Please enter a location to get the weather forecast.")
