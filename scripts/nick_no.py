import json
import requests

# https://static.smilegatemegaport.com/gameRecord/epic7/epic7_user_world_global.json
# Load the JSON data
with open('global.json', 'r') as global_file:
    global_data = json.load(global_file)

with open('armory_users.json', 'r') as armory_file:
    armory_data = json.load(armory_file)

# Create a dictionary to map nick_nm to nick_no from global.json
nick_no_map = {user['nick_nm']: user['nick_no'] for user in global_data['users']}

# Add nick_no to each user in armory_users.json if it exists in global.json
for user in armory_data['users']:
    user['nick_no'] = nick_no_map.get(user['nick_nm'], None)

# Save the updated data to a new JSON file
output_file = 'user_nick_no.json'
with open(output_file, 'w') as file:
    json.dump(armory_data, file, indent=4)

print(f"Data saved to {output_file}")
