import requests
from requests.auth import HTTPBasicAuth
import json

class JiraClient:
    def __init__(self, domain, email, token):
        self.base_url = f"https://{domain}/rest/api/3"
        self.auth = HTTPBasicAuth(email, token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_issue(self, issue_key):
        url = f"{self.base_url}/issue/{issue_key}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant fields
        fields = data.get('fields', {})
        description = fields.get('description', '')
        
        # Jira description is often in ADF (Atlassian Document Format). 
        # For simplicity in this agent, we might want to convert it to text.
        # This is a simplified extraction.
        text_description = self._extract_text_from_adf(description)
        
        return {
            'key': issue_key,
            'summary': fields.get('summary'),
            'description': text_description
        }

    def add_comment(self, issue_key, comment):
        url = f"{self.base_url}/issue/{issue_key}/comment"
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": comment,
                                "type": "text"
                            }
                        ]
                    }
                ]
            }
        }
        response = requests.post(url, headers=self.headers, auth=self.auth, data=json.dumps(payload))
        response.raise_for_status()

    def _extract_text_from_adf(self, adf_body):
        """
        Recursively extract text from Atlassian Document Format.
        """
        if not adf_body:
            return ""
        
        if isinstance(adf_body, str):
            return adf_body
            
        text = []
        if isinstance(adf_body, dict):
            if 'text' in adf_body:
                text.append(adf_body['text'])
            if 'content' in adf_body:
                for item in adf_body['content']:
                    text.append(self._extract_text_from_adf(item))
        
        return " ".join(text)
