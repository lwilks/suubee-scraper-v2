# Installing the Suubee-Scraper script

## Let's get started!

This tutorial will guide you through setting up the Suubee-Scraper python script to run on Google cloud. The script is setup to run every 6 hours by default/

**WARNING**: This script was developed by Liam Wilks and is completly independent of Suubee.com. Under no circumstances shall Liam Wilks or Suubee be liable for any indirect, incidental, consequintial, special or exemplary dmages arising out of or in connection with your access or use or inability to access or use the script, whether or not the damages were foreseeable and whether or not Liam Wilks or Suubee was advised of the possibility of such damages.

**Time to complete**: About 10 minutes

Click the **Start** button to move to the next step.

## Create a Google Cloud project

You will first need to create a project in Google Cloud to house your project

Run the below command in the shell:
```bash
gcloud projects create PROJECT_ID
```

Replace PROJECT_ID with a suitable project name

**Tip**: Click the copy button on the side of the code box and paste the command in the Cloud Shell terminal to run it.

## Set the project you just created as the active project

Run the below command in the shell:
```bash
gcloud config set project PROJECT_ID
```

**Tip**: Click the copy button on the side of the code box and paste the command in the Cloud Shell terminal to run it.

## Edit the .env file with your Username\Password settings for IG & Suubee

In order for the script to recieve the lists from Suubee it must have the correct login details to access the site (as it is not a publicly available website).

Similarly, the script needs your IG login details as well as an API key in order to access the IG API to search for the correct stock symbols and (re)build your lists.

Click on the link below to begin editing the .env file (if it is not currently shown)
<walkthrough-editor-open-file
    filePath="suubee-scraper-v2/.env">
    Open .env for editing
</walkthrough-editor-open-file>

Fill in the correct details and click save

## Initialize your App Engine app

You first need to create an App Engine instance to upload our script to

Run the below command in the shell:
```bash
gcloud app create --project=[YOUR_PROJECT_NAME]
```

**Tip**: Click the copy button on the side of the code box and paste the command in the Cloud Shell terminal to run it.

## Deploy to App Engine

The next step is to deploy the script to Google App engine.

Try running a command now:
```bash
gcloud app deploy ./app.yaml ./cron.yaml
```

**Tip**: Click the copy button on the side of the code box and paste the command in the Cloud Shell terminal to run it.

**Note**: At this point the deployment will probably fail and you will be asked to enable the "Cloud Build API" and in turn enable billing. Click on the supplied link which will open in a new tab, then click "Enable Cloud Build API", follow the instructions for enabling billing. Then click the "Enable Cloud Build API" again and return to this tab in your web browser.

## Test your application

Try running a command now:
```bash
gcloud app browse
```

**Tip**: Click the copy button on the side of the code box and paste the command in the Cloud Shell terminal to run it.

If Cloud Console cannot detect your browser, you will be presented with a clickable link. Click the link to start your script.

**Note**: The script will take between 10-30 minutes depending on the amount of tickers on the site and wether you have arranged with IG to have your throttling relaxed. For example after contacting helpdesk.uk@ig.com I was able to decrease the throttling on my account from 60 requests per minute to 180 requests per minute. If you want to do the same, you will need to give IG the reason you are doing this and the API Key you are using.

## Congratulations

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

You’re all set!

You have now deployed the Suubee-Scraper script to App Engine in Google Cloud and it will run every 6 hours.
