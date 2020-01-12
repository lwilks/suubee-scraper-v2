# Suubee-Scraper
Script to download lists from Suubee.com and build watchlist in IG

**WARNING**: This script was developed by Liam Wilks and is completly independent of Suubee.com. Under no circumstances shall Liam Wilks or Suubee be liable for any indirect, incidental, consequintial, special or exemplary dmages arising out of or in connection with your access or use or inability to access or use the script, whether or not the damages were foreseeable and whether or not Liam Wilks or Suubee was advised of the possibility of such damages.

# Requirements
-API Key from IG Markets

-Google Cloud account with billing enabled

# Cost of running the application
In it's default configuration the Suubee-Scraper script will only run once every 6 hours. When it runs, it only runs for 10-30 minutes at a time.

This is within the "Always Free" limits of the App Engine. You can find out more here: https://cloud.google.com/free/docs/gcp-free-tier

It is also possible to set alarms and budgets to manage the costs. You can find out more about that here: https://cloud.google.com/appengine/docs/standard/python/console/#billing

**NOTE**: Needles to say, you are using this script at your own discrestion and you are responsable for any charges you incur as part of using it. Please DYOR!

# Getting an IG API key
1.) Log in to IG Account

2.) Click Settings

3.) Click API Key

4.) Follow instructions to create an IG API Key

# Launch Suubee-Script in Google Cloud Shell and Start Tutorial

Click on the link below to copy this repositry to Google Cloud Shell and launch a tutorial which will guide you through the process of setting up the Suubee-Script and deploying it to Google App Engine

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Flwilks%2Fsuubee-scraper.git&cloudshell_open_in_editor=.env&cloudshell_tutorial=Tutorial.md)
