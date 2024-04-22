import requests

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
api_key = 'd2ed8137acc17a02bcd284b4548d5b88'
cityName = "Accra"

url = f"{BASE_URL}?q={cityName}&appid={api_key}"

response = requests.get(url).json()

print(response)
