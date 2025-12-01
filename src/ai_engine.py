import os
from openai import OpenAI
import json

class AIEngine:
    def __init__(self, api_key):
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=api_key
        )

    def generate_code(self, summary, description, existing_files):
        """
        Generates code based on the issue description.
        Returns a list of dicts: [{'path': '...', 'content': '...'}]
        """
        
        system_prompt = """
        You are an expert software developer. 
        You will be given a Jira issue summary and description, and a list of existing files.
        Your task is to write the code to implement the requested feature or fix.
        
        You must return the response in valid JSON format with the following structure:
        {
            "changes": [
                {
                    "path": "path/to/file.py",
                    "content": "full content of the file"
                }
            ]
        }
        
        If you are creating a new file, specify the path.
        If you are modifying an existing file, provide the FULL content of the file with the changes applied.
        Do not use markdown formatting in the JSON response.
        """
        
        user_message = f"""
        Issue Summary: {summary}
        Issue Description: {description}
        
        Existing Files: {existing_files}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return data.get('changes', [])
            
        except Exception as e:
            print(f"AI Generation failed: {e}")
            # Fallback for testing/demo purposes if API fails or key is missing
            return []
