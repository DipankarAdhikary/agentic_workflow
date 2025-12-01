# Setup Guide: Jira + GitHub + Copilot Agent

The codebase is ready. Now you need to connect the services.

## 1. GitHub App Configuration (Recommended)
Instead of a Personal Access Token, we will use a GitHub App for better security and to allow the bot to act on its own behalf.

### Step 1.1: Create a GitHub App
1.  Go to your **Profile Settings** -> **Developer settings** -> **GitHub Apps** -> **New GitHub App**.
2.  **Name**: `Copilot AI Agent` (or similar).
3.  **Homepage URL**: `https://github.com/DipankarAdhikary/agentic_workflow` (or any URL).
4.  **Webhook**: Uncheck "Active" (we don't need webhooks for the app itself, we use Jira webhooks).
5.  **Permissions**:
    *   **Repository permissions**:
        *   `Contents`: **Read and write** (to read code and push changes).
        *   `Pull requests`: **Read and write** (to create PRs).
        *   `Metadata`: **Read-only** (mandatory).
6.  Click **Create GitHub App**.

### Step 1.2: Get Credentials
Once created, you will see the App settings:
1.  **App ID**: Note this number (e.g., `123456`).
2.  **Private Key**: Scroll down and click **Generate a private key**. It will download a `.pem` file. Open it and copy the *entire* content (including `-----BEGIN RSA PRIVATE KEY-----`).
3.  **Install App**: Go to **Install App** on the left menu, and install it on your `agentic_workflow` repository.
4.  **Find Installation ID**:
    *   After installing, click **Configure** next to your account name.
    *   Look at the URL in your browser address bar.
    *   It will look like: `https://github.com/settings/installations/12345678`
    *   The number at the end (`12345678`) is your **Installation ID**.
    *   *Note: Do NOT use the Client ID.*

### Step 1.3: Add Secrets to Repository
Go to your GitHub Repository (`agentic_workflow`) -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.

| Secret Name | Value |
|---|---|
| `APP_ID` | The App ID from Step 1.2 |
| `APP_PRIVATE_KEY` | The content of the `.pem` file |
| `INSTALLATION_ID` | The Installation ID from Step 1.2 |
| `JIRA_DOMAIN` | Your Jira domain (e.g., `dipankaradhikary1994.atlassian.net`) |
| `JIRA_EMAIL` | The email address you use to log in to Jira |
| `JIRA_API_TOKEN` | Create one at [id.atlassian.com](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `AI_MODEL_TOKEN` | A GitHub PAT (Classic or Fine-grained) with no specific scopes, just for authentication. |

> [!TIP]
> **How to get `AI_MODEL_TOKEN`**:
> 1. Go to GitHub Settings -> Developer Settings -> Personal access tokens.
> 2. Generate a new token (Classic is fine).
> 3. You don't need to select any scopes if you just want to access the Models API.
> 4. Copy the token and add it as a secret named `AI_MODEL_TOKEN`.

## 2. Jira Automation Setup
You need to trigger the GitHub Action when a ticket moves to "Assign to AI".

> [!TIP]
> **Alternative: Global Automation Page**
> If you cannot find "Project Settings", use the Global Automation page:
> [**Go to Global Automation**](https://dipankaradhikary1994.atlassian.net/jira/settings/automation)
> 1. Click **Create rule** (Blue button at the top right).
> 2. **Trigger**: Issue transitioned.
> 3. **Action**: Send web request.
> 4. **Scope**: When saving, select your project ("DevOps/SRE" or "SCRUM").

1.  Click **Create rule** (blue button at the top right).
2.  **Trigger**:
    *   Search for and select **Field value changed**.
    *   **Fields to monitor for changes**: Select **Status**.
    *   **Change type**: Select **Value changes**.
    *   Click **Save**.
3.  **Condition** (New Step):
    *   Click **New condition**.
    *   Select **Work item fields condition** (or "Issue fields condition").
    *   **Field**: Status.
    *   **Condition**: equals.
    *   **Value**: Assign to AI.
    *   Click **Save**.
4.  **Action**:
    *   Click **New action**.
    *   Search for and select **Send web request**.
    *   **Webhook URL**: `https://api.github.com/repos/DipankarAdhikary/agentic_workflow/dispatches`
    *   **HTTP Method**: `POST`
    *   **Webhook Body**: `Custom data`
    *   **Custom Data**:
        ```json
        {
          "event_type": "assign-to-ai",
          "client_payload": {
            "issue_key": "{{issue.key}}",
            "summary": "{{issue.summary}}"
          }
        }
        ```
    *   **Headers**:
        *   `Authorization`: `Bearer <YOUR_GITHUB_PAT>`
        *   `Accept`: `application/vnd.github.v3+json`
        *   *(Note: Even for public repos, you need a PAT to trigger the workflow. Use a Classic PAT with **`public_repo`** scope (or `repo` scope).)*

## 3. Verification
1.  Create a Jira Ticket: "Create a README file".
2.  Move it to "Assign to AI".
3.  Check the GitHub Actions tab!

## 4. Troubleshooting

### Issue: GitHub Action Not Triggering

1.  **Check Jira Automation Execution**:
    *   Go to your Jira Automation Rule.
    *   Click on **Audit log** or **Execution history**.
    *   See if the webhook ran and what error it returned (if any).

2.  **Test the Webhook Manually**:
    *   Open PowerShell or Terminal.
    *   Run this command (replace `<YOUR_PAT>` with your actual PAT):
    ```powershell
    Invoke-WebRequest -Uri "https://api.github.com/repos/DipankarAdhikary/agentic_workflow/dispatches" -Method POST -Headers @{"Accept"="application/vnd.github.v3+json"; "Authorization"="Bearer <YOUR_PAT>"} -Body '{"event_type":"assign-to-ai","client_payload":{"issue_key":"TEST-1","summary":"Test issue"}}' -ContentType "application/json"
    ```
    *   Go to GitHub Actions and see if a workflow run appears.

3.  **Check GitHub Secrets**:
    *   Verify all secrets are set correctly (no typos, correct values).
    *   **IMPORTANT**: `JIRA_DOMAIN` should be **just the domain**, without `https://`
        - ✅ Correct: `dipankaradhikary1994.atlassian.net`
        - ❌ Wrong: `https://dipankaradhikary1994.atlassian.net`

4.  **Check Workflow Syntax**:
    *   Go to your GitHub repo -> Actions tab.
    *   If there's a syntax error in the workflow file, GitHub will show it there.
