import os
import time
import jwt
import requests
from git import Repo

class GitHubClient:
    def __init__(self, app_id, private_key, installation_id):
        self.app_id = app_id
        self.private_key = private_key
        self.installation_id = installation_id
        self.token = self._get_installation_token()
        
        self.repo_path = os.getcwd()
        self.repo = Repo(self.repo_path)
        self.github_repository = os.environ.get('GITHUB_REPOSITORY')

        # Configure remote with the new token
        self._configure_remote()

    def _get_jwt(self):
        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + (10 * 60),
            "iss": self.app_id
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def _get_installation_token(self):
        jwt_token = self._get_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()["token"]

    def _configure_remote(self):
        # Configure the remote URL to use the installation token
        origin_url = self.repo.remotes.origin.url
        # Strip existing auth if any
        if "@" in origin_url:
            origin_url = "https://" + origin_url.split("@")[1]
        
        # Add token auth
        new_url = origin_url.replace("https://", f"https://x-access-token:{self.token}@")
        self.repo.remotes.origin.set_url(new_url)

    def create_branch(self, branch_name):
        new_branch = self.repo.create_head(branch_name)
        new_branch.checkout()

    def list_files(self):
        files = []
        for root, _, filenames in os.walk(self.repo_path):
            if '.git' in root:
                continue
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    def apply_changes(self, changes):
        for change in changes:
            path = change['path']
            content = change['content']
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)

    def commit_and_push(self, branch_name, message):
        self.repo.git.add(A=True)
        self.repo.index.commit(message)
        self.repo.git.push('--set-upstream', 'origin', branch_name)

    def create_pr(self, title, body, head, base):
        url = f"https://api.github.com/repos/{self.github_repository}/pulls"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get('html_url')
