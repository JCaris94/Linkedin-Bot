# LinkedInBot

Enhance your LinkedIn networking by increasing your profile's visibility through automated profile viewing. This can help you grow your connections and potentially receive interview opportunities.

![GitHub repo size](https://img.shields.io/github/repo-size/JCaris94/Linkedin-Bot?style=plastic) ![GitHub language count](https://img.shields.io/github/languages/count/JCaris94/Linkedin-Bot?style=plastic) ![GitHub top language](https://img.shields.io/github/languages/top/JCaris94/Linkedin-Bot?style=plastic) ![GitHub last commit](https://img.shields.io/github/last-commit/JCaris94/Linkedin-Bot?color=red&style=plastic)

## Overview

When you view a LinkedIn user's profile, they receive a notification of your visit, which can increase your visibility and prompt them to view your profile. This bot automates profile viewing to boost your presence in LinkedIn's network suggestions.

<p align="center">
  <img src="https://preview.ibb.co/mMDuAk/linked_In_Bot_Profile_View_Results.png" alt="LinkedInBot Result" width="325" height="200">
</p>

## Note

This project builds on the work of [helloitsim](https://github.com/helloitsim) from the [LInBot](https://github.com/helloitsim/LInBot) repository. 
It was updated to accommodate changes in LinkedIn's site layout. Recent improvements were made in August 2024, based on code from [MattFlood7](https://github.com/MattFlood7/LinkedInBot). Please note that some errors may still be present.

## Requirements

**Important:** Ensure your [Profile Viewing Setting](https://www.linkedin.com/settings/?trk=nav_account_sub_nav_settings) is set to 'Public' so that LinkedIn members can see your profile visits, encouraging them to check your profile in return. Also, set your language to **English**.

LinkedInBot was developed with [Python 3.8](https://www.python.org/downloads).

To get started, install the required Python dependencies by running `pip3 install -r requirements.txt`.

For Chrome users, download the [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in the same directory as the bot on Windows or in the `/usr/bin` directory on OS X.

## Configuration

Before running the bot, create a `.env` file to configure the script. Include your LinkedIn login credentials (email, password, etc.) and other settings to customize the bot's behavior.

```python
# Configurable Constants
EMAIL = 'youremail@gmail.com'
PASSWORD = 'password'
VIEW_SPECIFIC_USERS = False
SPECIFIC_USERS_TO_VIEW = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
NUM_LAZY_LOAD_ON_MY_NETWORK_PAGE = 5
CONNECT_WITH_USERS = True
RANDOMIZE_CONNECTING_WITH_USERS = True
JOBS_TO_CONNECT_WITH = ['CEO', 'CTO', 'Developer', 'HR', 'Recruiter']
ENDORSE_CONNECTIONS = False
RANDOMIZE_ENDORSING_CONNECTIONS = True
VERBOSE = True
```

## Usage
After setting up your environment and configuration file, you can run the bot.

Navigate to the project directory and execute the command: python LinkedInBot.py

Choose your preferred browser, and the bot will begin visiting profiles.

## Output

T: Total number of profiles the bot attempted to access.

V: Number of profiles successfully visited (accessible profiles with a rank of 3 or less).

Q: Number of profiles in the queue.

## Potential Issues
#### Two-Factor Authentication
Solution: A setting is being developed to provide more time for authentication if enabled; headless mode cannot be used in this scenario.

#### Stuck on -> Scraping User URLs on Network tab.
Solution: Restarting the script typically resolves this problem.

#### LinkedIn Security Email:
Enter the security pin if prompted and not in headless mode, or restart the bot.
Exercise caution, as your account might be flagged or monitored, though this is not confirmed.

## Disclaimer
Bots and scrapers are addressed in LinkedIn's prohibited software policy. Use this bot at your own risk. A California judge ruled against banning bots, as described in this article.

## Additional Information
Over the years, I've made occasional updates to this project. Others have used it as a foundation for their work. As I learn about related projects, I will link them here:

@SethRzeszutek's https://github.com/SethRzeszutek/LinkedIn-Bot [LinkedIn-Bot](https://github.com/SethRzeszutek/LinkedIn-Bot)
