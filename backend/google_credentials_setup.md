# How to get `credentials.json` for Google Docs API

To use the "Share to Docs" feature, you need to create an OAuth 2.0 Client ID in the Google Cloud Console.

## Steps

1.  **Go to Google Cloud Console:**
    - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
    - Sign in with your Google account.

2.  **Create a Project:**
    - Click the project dropdown at the top left.
    - Click **"New Project"**.
    - Name it "0DTE Trader" (or anything you like) and click **Create**.
    - Select the new project.

3.  **Enable Google Docs API:**
    - In the search bar at the top, type **"Google Docs API"**.
    - Click on it and then click **"Enable"**.

4.  **Configure OAuth Consent Screen:**
    - Go to **"APIs & Services" > "OAuth consent screen"**.
    - Choose **"External"** (unless you have a Google Workspace organization, then Internal is fine). Click **Create**.
    - **App Information:**
        - App name: "0DTE Trader"
        - User support email: Select your email.
    - **Developer Contact Information:** Enter your email.
    - Click **Save and Continue** through the other steps (Scopes, Test Users).
    - **Important:** Under **"Test Users"**, add your own email address so you can log in.

5.  **Create Credentials:**
    - Go to **"APIs & Services" > "Credentials"**.
    - Click **"+ CREATE CREDENTIALS"** > **"OAuth client ID"**.
    - **Application type:** Select **"Desktop app"**.
    - Name: "Desktop Client".
    - Click **Create**.

6.  **Download JSON:**
    - You will see a popup "OAuth client created".
    - Click the **Download JSON** button (icon looking like a download arrow).
    - Save this file as `credentials.json`.

7.  **Install:**
    - Move the `credentials.json` file into your backend folder:
      `/Users/marklu/GoogleAntigravity/zero-dte-trader/backend/credentials.json`

8.  **Restart & Run:**
    - Restart your backend server.
    - Click "Share to Docs" in the app.
    - A browser window will open. Log in with the email you added as a Test User.
    - Grant permission.
    - Success!

## Troubleshooting: Adding Test Users
If you get an "Access Blocked" or "Error 403: access_denied" error, you likely forgot to add your email as a Test User.

1.  Go to [Google Cloud Console > APIs & Services > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2.  Scroll down to the **"Test users"** section.
3.  Click **"+ ADD USERS"**.
4.  Enter your Google email address (the one you are trying to log in with).
5.  Click **Save**.
6.  Try sharing to docs again.
