import os
import json
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request
import httpx

def _get_bearer_token():
    credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    request = Request()
    credentials.refresh(request)
    return credentials.token

def main():
    load_dotenv()

    project_id = os.environ.get("PROJECT_ID")
    app_id = os.environ.get("GEMINI_ENTERPRISE_APP_ID")

    api_endpoint = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/"
        f"locations/global/collections/default_collection/engines/{app_id}/"
        f"assistants/default_assistant/agents"
    )

    bearer_token = _get_bearer_token()
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id,
    }

    print(f"Listing agents from: {api_endpoint}")
    response = httpx.get(api_endpoint, headers=headers)
    
    if response.status_code == 200:
        agents = response.json().get("agents", [])
        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"Name: {agent.get('name')}")
            print(f"  Display Name: {agent.get('displayName')}")
            print(f"  Description: {agent.get('description')}")
            print(f"  Create Time: {agent.get('createTime')}")
            print("-" * 40)
    else:
        print(f"Failed to list agents. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
