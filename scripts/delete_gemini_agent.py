import os
import httpx
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request

def _get_bearer_token():
    credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    request = Request()
    credentials.refresh(request)
    return credentials.token

def main():
    load_dotenv()

    project_id = os.environ.get("PROJECT_ID")
    app_id = os.environ.get("GEMINI_ENTERPRISE_APP_ID")
    agent_id = "combined_poc_1776983833"  # The older agent ID

    api_endpoint = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/"
        f"locations/global/collections/default_collection/engines/{app_id}/"
        f"assistants/default_assistant/agents/{agent_id}"
    )

    bearer_token = _get_bearer_token()
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "X-Goog-User-Project": project_id,
    }

    print(f"Deleting agent: {api_endpoint}")
    response = httpx.delete(api_endpoint, headers=headers)
    
    if response.status_code == 200:
        print(f"✓ Agent {agent_id} deleted successfully.")
        print(response.json())
    elif response.status_code == 204:
        print(f"✓ Agent {agent_id} deleted successfully (No Content).")
    else:
        print(f"✗ Failed to delete agent. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
