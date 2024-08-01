import json
import time
import requests

# Load the JSON data
with open('hero.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract hero names and format them
def format_hero_name(name):
    if name == "Ainos 2.0":
        return "ainos-20"
    if name == "Jack-O'":
        return "jack-o"
    if name == "Baal and Sezan":
        return "baal-and-sezan"
    if name == "Sage Baal and Sezan":
        return "sage-baal-and-sezan"
    
#Failed to fetch data for baal-&-sezan
# birgitta doesnt exist yet
# Failed to fetch data for jack-o'
# Failed to fetch data for sage-baal-&-sezan
# Failed to fetch data for dragon-bride-senya
# Failed to fetch data for summer's-disciple-alexa
# Failed to fetch data for archdemon's-shadow
    return name.replace(' ', '-').lower()

hero_names = [format_hero_name(hero['name']) for hero in data['en']]

print(hero_names)

# Function to fetch data from the API for a given hero
def fetch_hero_data(hero_name):
    url = f"https://epic7db.com/api/heroes/{hero_name}/mikeyfogs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {hero_name}")
        return None

# Fetch data for all heroes
hero_data = {}
for hero_name in hero_names:
    data = fetch_hero_data(hero_name)
    if data:
        hero_data[hero_name] = data
    time.sleep(2)

# Save the fetched data to a new JSON file
output_file = 'hero_data.json'
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(hero_data, file, indent=4)

print(f"Data saved to {output_file}")
