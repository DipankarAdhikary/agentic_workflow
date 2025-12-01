import argparse
import os
import sys
from jira_client import JiraClient
from github_client import GitHubClient
from ai_engine import AIEngine

def main():
    parser = argparse.ArgumentParser(description='AI Agent for Jira-GitHub Integration')
    parser.add_argument('--issue-key', required=True, help='Jira Issue Key')
    parser.add_argument('--summary', required=True, help='Jira Issue Summary')
    args = parser.parse_args()

    print(f"Starting AI Agent for Issue: {args.issue_key}")
    print(f"Summary: {args.summary}")

    # Initialize Clients
    jira = JiraClient(
        domain=os.environ.get('JIRA_DOMAIN'),
        email=os.environ.get('JIRA_EMAIL'),
        token=os.environ.get('JIRA_API_TOKEN')
    )
    
    github_client = GitHubClient(
        app_id=os.environ.get('APP_ID'),
        private_key=os.environ.get('APP_PRIVATE_KEY'),
        installation_id=os.environ.get('INSTALLATION_ID')
    )
    
    ai_engine = AIEngine(api_key=os.environ.get('AI_MODEL_TOKEN'))

    try:
        # 1. Get Full Issue Details
        print("Fetching issue details from Jira...")
        issue_details = jira.get_issue(args.issue_key)
        print(f"Issue Description found: {len(issue_details.get('description', ''))} chars")

        # 2. Setup Git Branch
        import time
        timestamp = int(time.time())
        branch_name = f"feature/{args.issue_key}-{timestamp}"
        print(f"Creating branch: {branch_name}")
        github_client.create_branch(branch_name)

        # 3. AI Coding
        print("Asking AI to generate code...")
        # For now, we pass the summary and description. 
        # In a real scenario, we'd pass the codebase context too.
        changes = ai_engine.generate_code(
            summary=args.summary,
            description=issue_details.get('description', ''),
            existing_files=github_client.list_files()
        )

        # 4. Apply Changes
        print("Applying changes...")
        github_client.apply_changes(changes)

        # 5. Commit and Push
        print("Committing and pushing...")
        github_client.commit_and_push(branch_name, f"feat: {args.issue_key} {args.summary}")

        # 6. Create PR
        print("Creating Pull Request...")
        pr_url = github_client.create_pr(
            title=f"{args.issue_key}: {args.summary}",
            body=f"AI Implementation for {args.issue_key}\n\n{issue_details.get('description', '')}",
            head=branch_name,
            base="main"
        )
        print(f"PR Created: {pr_url}")

        # 7. Comment on Jira (Optional - good for feedback)
        jira.add_comment(args.issue_key, f"AI Agent started work. PR created: {pr_url}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
