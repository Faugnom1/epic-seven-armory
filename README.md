# <center> Epic Seven Armory </center>

To experience the full functionality of the Epic Seven Armory, including real-time updates during Twitch streams, users should download the dedicated Electron app. This app provides integration with Twitch, enabling streamers to display their unit stats dynamically while broadcasting.

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

Unit Stat Extraction Results:
![DesktopApp](https://github.com/Faugnom1/epic-seven-armory/blob/master/Desktop%20App.png)

Twitch Extension:

![Demo Animation](https://github.com/Faugnom1/epic-seven-armory/blob/master/Sidebar.gif)

![InGame](https://github.com/Faugnom1/epic-seven-armory/blob/master/inGameUI.png)


Enable the extension at: https://dashboard.twitch.tv/extensions/3qerc4w2tf5cv28ka8darpwb8qqerw-0.0.1  

Technology Stack

Frontend:  
React,  
Python,  
Electron

Backend:  
Python,  
Flask,  
Pytesseract

Database:  
MongoDB

Testing:  
Pytest

Deployment:  
Electron  
AWS

Download and Installation  
To experience the full functionality of the Epic Seven Armory, including real-time updates during Twitch streams, you can download the latest version of the Electron app from the releases page. Simply navigate to the latest release, download the ZIP file appropriate for your operating system, extract the contents, and run the executable file (e.g., epic-seven-armory.exe). This will install and launch the application, providing you with all the features to manage and analyze your units' stats.
