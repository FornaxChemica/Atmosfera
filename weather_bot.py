import discord
import requests
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def get_weather(city):
    geocode_url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
    response = requests.get(geocode_url)
    if response.status_code == 200 and len(response.json()) > 0:
        location = response.json()[0]
        latitude = location['lat']
        longitude = location['lon']
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        weather_response = requests.get(weather_url)
        if weather_response.status_code == 200:
            weather_data = weather_response.json()['current_weather']
            temp = weather_data['temperature']
            windspeed = weather_data['windspeed']
            weathercode = weather_data['weathercode']
            return (temp, windspeed, weathercode)
    return None

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Weather Bot'))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!weather'):
        city = message.content.split('!weather ')[1]
        weather = get_weather(city)
        if weather:
            temp, windspeed, weathercode = weather
            description = f"Weather code: {weathercode}" 
            embed = discord.Embed(
                title=f"Weather in {city}",
                description=description,
                color=discord.Color.blue()
            )
            embed.add_field(name="Temperature", value=f"{temp}°C", inline=False)
            embed.add_field(name="Windspeed", value=f"{windspeed} km/h", inline=False)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"Could not find weather data for {city}")

client.run(DISCORD_TOKEN)
