# Setup Guide: Jira to GitHub Copilot Workspace Integration

This guide will help you set up an automated workflow where moving a Jira ticket to "Assign to AI" status creates a GitHub Issue that you can open in Copilot Workspace.

## Prerequisites

- GitHub account with Copilot subscription (for Workspace access)
- Jira account with admin access to your project
- GitHub repository (this one: `DipankarAdhikary/agentic_workflow`)

## Step 1: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Add the following secrets:

| Secret Name | Value | How to Get It |
|-------------|-------|---------------|
| `JIRA_DOMAIN` | Your Jira domain (e.g., `dipankaradhikary1994.atlassian.net`) | Just the domain, **without** `https://` |
| `JIRA_EMAIL` | The email address you use to log in to Jira | Your Jira login email |
| `JIRA_API_TOKEN` | Jira API token | Create one at [id.atlassian.com](https://id.atlassian.com/manage-profile/security/api-tokens) |

> [!IMPORTANT]
> **JIRA_DOMAIN** should be just the domain name:
> - ✅ Correct: `dipankaradhikary1994.atlassian.net`
> - ❌ Wrong: `https://dipankaradhikary1994.atlassian.net`

## Step 2: Set Up Jira Automation

You need to create a Jira automation rule that triggers when a ticket moves to "Assign to AI" status.

### 2.1 Navigate to Jira Automation

1. Go to your Jira project
2. Click **Project settings** (bottom left)
3. Click **Automation** in the left sidebar
4. Click **Create rule** (blue button at the top right)

> [!TIP]
> **Alternative**: Use the global automation page:
> [https://dipankaradhikary1994.atlassian.net/jira/settings/automation](https://dipankaradhikary1994.atlassian.net/jira/settings/automation)

### 2.2 Configure the Trigger

1. Select **Field value changed**
2. **Fields to monitor for changes**: Select **Status**
3. **Change type**: Select **Value changes**
4. Click **Save**

### 2.3 Add a Condition

1. Click **New condition**
2. Select **Work item fields condition** (or "Issue fields condition")
3. **Field**: Status
4. **Condition**: equals
5. **Value**: Assign to AI
6. Click **Save**

### 2.4 Add the Webhook Action

1. Click **New action**
2. Search for and select **Send web request**
3. Configure the webhook:
   - **Webhook URL**: `https://api.github.com/repos/DipankarAdhikary/agentic_workflow/dispatches`
   - **HTTP Method**: `POST`
   - **Webhook Body**: `Custom data`
   - **Custom Data**:
     ```json
     {
       "event_type": "assign-to-ai",
       "client_payload": {
         "issue_key": "{{issue.key}}",
         "summary": "{{issue.summary}}"
       }
     }
     ```
   - **Headers**:
     - `Authorization`: `Bearer <YOUR_GITHUB_PAT>`
     - `Accept`: `application/vnd.github.v3+json`

4. Click **Save**

> [!WARNING]
> You need a GitHub Personal Access Token (PAT) for the webhook:
> 1. Go to [GitHub Settings → Personal access tokens](https://github.com/settings/tokens)
> 2. Generate a new token (Classic)
> 3. Select scope: **`public_repo`** (or `repo` for private repos)
> 4. Copy the token and use it in the `Authorization` header above

### 2.5 Name and Activate the Rule

1. Give your rule a name (e.g., "Assign to AI - Create GitHub Issue")
2. **IMPORTANT**: Set the scope to your project (e.g., "SCRUM")
3. Click **Turn it on**

## Step 3: Test the Integration

1. Create a new Jira ticket (or use an existing one)
2. In the description, write clear requirements:
   ```
   Create a new Python file called hello.py with a function that prints "Hello from AI!"
   ```
3. Move the ticket to **"Assign to AI"** status
4. Check your GitHub repository:
   - Go to the **Issues** tab
   - You should see a new issue with the label `ai-task`
   - The issue will contain the Jira ticket details

## Step 4: Use Copilot Workspace

1. Open the GitHub Issue that was created
2. Click **"Open in Copilot Workspace"** (if available in your GitHub plan)
3. Copilot will analyze the requirements and generate code
4. Review the AI-generated changes
5. Commit and create a Pull Request

## Troubleshooting

### Issue: GitHub Action Not Triggering

1. **Check Jira Automation Execution**:
   - Go to your Jira Automation Rule
   - Click **Audit log** or **Execution history**
   - See if the webhook ran and what error it returned

2. **Test the Webhook Manually**:
   ```powershell
   Invoke-WebRequest -Uri "https://api.github.com/repos/DipankarAdhikary/agentic_workflow/dispatches" -Method POST -Headers @{"Accept"="application/vnd.github.v3+json"; "Authorization"="Bearer <YOUR_PAT>"} -Body '{"event_type":"assign-to-ai","client_payload":{"issue_key":"TEST-1","summary":"Test issue"}}' -ContentType "application/json"
   ```
   - Go to GitHub Actions and see if a workflow run appears

3. **Check GitHub Secrets**:
   - Verify all secrets are set correctly (no typos)
   - Ensure `JIRA_DOMAIN` is without `https://`

4. **Check Workflow Syntax**:
   - Go to your GitHub repo → Actions tab
   - If there's a syntax error, GitHub will show it there

### Issue: No "Open in Copilot Workspace" Button

- This feature requires a GitHub Copilot subscription
- It may not be available in all GitHub plans
- Check [GitHub Copilot documentation](https://docs.github.com/en/copilot) for availability

## What Happens Next?

Once set up:
1. ✅ Jira ticket moved to "Assign to AI"
2. ✅ Webhook triggers GitHub Action
3. ✅ GitHub Issue created with Jira details
4. ✅ You open in Copilot Workspace
5. ✅ AI generates code
6. ✅ You review and create PR

## Architecture

```
Jira Ticket (Status: "Assign to AI")
    ↓
Jira Automation (Webhook)
    ↓
GitHub Actions (Repository Dispatch)
    ↓
Create GitHub Issue
    ↓
Manual: Open in Copilot Workspace
    ↓
AI Generates Code
    ↓
Create Pull Request
```

## Support

For issues or questions:
- Check the [GitHub Actions logs](https://github.com/DipankarAdhikary/agentic_workflow/actions)
- Review the Jira Automation audit log
- Ensure all secrets are correctly configured
