import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import pytz
from tzlocal import get_localzone
import requests
import geocoder
import locale
import os

# Function to get the API key from the user or continue without it
def get_api_key():
    api_key = simpledialog.askstring("API Key", "Put your API key here (or click Cancel to continue without it):")
    if api_key is None or api_key.strip() == "":
        # If the user clicks Cancel or leaves the input empty, continue without the API key
        return None
    return api_key

# Get the API key from the user or read it from the config file
config_file_path = "config.txt"
if os.path.exists(config_file_path):
    # If the config file exists, read the API key from it
    with open(config_file_path, "r") as config_file:
        api_key = config_file.readline().strip()
else:
    # If the config file does not exist, get the API key from the user
    api_key = get_api_key()
    if api_key is not None:
        # If the user provided an API key, save it to the config file for future use
        with open(config_file_path, "w") as config_file:
            config_file.write(api_key)

# Function to get the current time in the specified timezone
def get_current_time(timezone):
    tz = pytz.timezone(timezone)
    return datetime.now(tz)

# Function to update the time label with the current time
def update_time_label():
    time_str = ""
    if timezone_var.get() == "UTC":
        time_str = get_current_time("UTC").strftime("%I:%M:%S %p UTC")
    else:
        local_timezone = get_localzone()
        time_str = get_current_time(str(local_timezone)).strftime("%I:%M:%S %p")
    time_label.config(text=time_str)
    window.after(1000, update_time_label)  # Schedule the function to run after 1 second

# Function to toggle fullscreen mode when F11 key is pressed
def toggle_fullscreen(event):
    if window.attributes('-fullscreen'):
        window.attributes('-fullscreen', False)
    else:
        window.attributes('-fullscreen', True)

# Function to get the nearest city and display the temperature
def get_nearest_city():
    if api_key:
        # Get the user's current location using geocoder
        g = geocoder.ip('me')
        lat, lon = g.latlng

        # Make a request to OpenStreetMap Nominatim API to get city information based on latitude and longitude
        url = f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=5'
        response = requests.get(url)
        data = response.json()
        city = data.get('address', {}).get('city', 'Unknown')

        # Use locale library to get the user's country code
        country_code = locale.getdefaultlocale()[0].split('_')[-1]
        if country_code in ('US', 'LR', 'MM'):
            # Display temperature in Fahrenheit for United States, Liberia, and Myanmar
            temperature = get_temperature(city, units='imperial')
            temperature_label.config(text=f'Temperature: {temperature}°F')
        else:
            # Display temperature in Celsius for other regions
            temperature = get_temperature(city, units='metric')
            temperature_label.config(text=f'Temperature: {temperature}°C')

        temperature_label.after(60000, get_nearest_city)  # Update temperature every 1 minute
    else:
        # Disable the temperature label if no API key is provided
        temperature_label.config(text="")

# Function to get the temperature from the API
def get_temperature(city, units='metric'):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}'
    response = requests.get(url)
    data = response.json()
    if 'main' in data and 'temp' in data['main']:
        return data['main']['temp']
    else:
        return 'You do not have an API key selected.'

# Create the main window
window = tk.Tk()
window.title("12-Hour Clock")
window.geometry("400x200")
window.configure(bg="black")

# Set the window in fullscreen mode
window.attributes('-fullscreen', True)

# Set the initial timezone to Local
timezone_var = tk.StringVar()
timezone_var.set("Local")

# Create a label to display the time and center it in the window
time_label = tk.Label(window, font=("Comic Sans MS", 72), bg="black", fg="white")
time_label.pack(expand=True)

# Update the time label every second
update_time_label()

# Bind F11 key to toggle fullscreen
window.bind("<F11>", toggle_fullscreen)

# Create a label to display the temperature and place it in the bottom right corner
temperature_label = tk.Label(window, font=("Comic Sans MS", 14), bg="black", fg="white")
temperature_label.pack(side=tk.RIGHT, anchor=tk.SE, padx=10, pady=10)

# Get nearest city and update the label every minute
get_nearest_city()

window.mainloop()
