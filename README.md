Epic Seven Armory

To experience the full functionality of the Epic Seven Armory, including real-time updates during Twitch streams, users should download the dedicated Electron app. This app provides integration with Twitch, enabling streamers to display their unit stats dynamically while broadcasting.

Epic Seven Armory  
https://epic-seven-armory.onrender.com/

Features:  
Image Upload and OCR Analysis: Allows users to upload images of their units' stats, which are then analyzed using OCR to extract the relevant data.

Unit Lookup: Provides detailed information about each unit, including base stats, memory imprints, and skills.

Build Finder: Enables users to search for builds based on unit and rank, displaying average stats and the most common builds.

User Profile and Units: Allows users to keep track of their uploaded units and edit import profile data such as RTA Rank. 

Real-time Updates for Streamers: Offers a video overlay component that shows the current stats of the selected units from a database while streaming. 

Tests:  
Tests Location: The tests are located in the tests directory of the project.

Run tests with "pytest tests/"

User Flow:

Home Page: Users arrive at the home page, where they can see an overview of the site's features.  
Sign Up / Log In: Users create an account or log in to their existing account.  
Profile Setup: Users set up their profile, including their in-game account details and RTA rank.  
Upload Stats Image: Users upload an image of their unit's stats, which the site analyzes and extracts the relevant data from.  
View Unit Details: Users can look up detailed information about their units, including base stats, memory imprints, and skills.  
Find Builds: Users search for builds based on their units and specific ranks, viewing average stats and the most common builds.  
Stream Overlay: Streamers can enable the overlay component to show real-time unit stats during their streams.

Twitch Extension:

Enable the extension at: https://dashboard.twitch.tv/extensions/3qerc4w2tf5cv28ka8darpwb8qqerw-0.0.1  
NOTE - curently Twitch.tv has disabled the creation of new extensions. This will be updated as soon as it is enabled again.
![Alt text](https://github.com/Faugnom1/epic-seven-armory/blob/master/twitch.png)


Api Details

External API
ChatGPT
https://api.openai.com/v1/chat/completions

Epic7db
https://epic7db.com/api/heroes/{unit_name.lower()}/{myApiUser}

Smilegate
https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json

Internal API

/get_unit_data: Fetches all unit data from the database.  
/update_selected_units: Updates the selected units based on user input.  
/upload_stats_image: Handles the upload and analysis of unit stats images.  

Technology Stack

Frontend:  
HTML, CSS (Bootstrap), JavaScript  
Python  
Electron

Backend:  
Python  
Flask  
Pytesseract (for testing and local installation)

Database:  
SQLite (for development)  
PostgreSQL (for production)  
Render  

Testing:  
Pytest

Deployment:  
Electron  
Render  

Download and Installation  
To experience the full functionality of the Epic Seven Armory, including real-time updates during Twitch streams, you can download the latest version of the Electron app from the releases page. Simply navigate to the latest release, download the ZIP file appropriate for your operating system, extract the contents, and run the executable file (e.g., epic-seven-armory.exe). This will install and launch the application, providing you with all the features to manage and analyze your units' stats.
