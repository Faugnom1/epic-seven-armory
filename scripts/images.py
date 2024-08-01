import json
import requests
import os
import time

# Path to the JSON file containing hero data
input_file = 'hero_data.json'

# Directory to store downloaded images
image_dir = 'hero_images'
os.makedirs(image_dir, exist_ok=True)

# Function to download and save hero image
def download_image(image_url, hero_name):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image_path = os.path.join(image_dir, f"{hero_name}.png")
        with open(image_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded image for {hero_name}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image for {hero_name}: {e}")

# Load the hero data from the JSON file
with open(input_file, 'r', encoding='utf-8') as file:
    hero_data = json.load(file)

# Iterate through each hero and download their image
for hero_name, data in hero_data.items():
    # Extract the image URL
    image_url = data.get('image')
    if image_url:
        download_image(image_url, hero_name)
        time.sleep(2)
    else:
        print(f"No image URL found for {hero_name}")
