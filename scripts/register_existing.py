import os
import json
import time
import httpx
import requests
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request

def _get_bearer_token():
    """Gets a bearer token for authenticating with Google Cloud."""
    try:
        credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        request = Request()
        credentials.refresh(request)
        return credentials.token
    except Exception as e:
        print(f"Error getting credentials: {e}")
        print("Please ensure you have authenticated with 'gcloud auth application-default login'.")
    return None

def main():
    load_dotenv()

    project_id = os.environ.get("PROJECT_ID")
    location = os.environ.get("LOCATION")
    app_id = os.environ.get("GEMINI_ENTERPRISE_APP_ID")
    agent_authorization = os.environ.get("AGENT_AUTHORIZATION")

    # Using the ID from the successful deployment
    remote_engine_resource = "projects/1084764818763/locations/us-central1/reasoningEngines/5780375069532356608"
    
    api_endpoint = f"{location}-aiplatform.googleapis.com"
    a2a_endpoint = f"https://{api_endpoint}/v1beta1/{remote_engine_resource}/a2a/v1/card"

    bearer_token = _get_bearer_token()
    if not bearer_token:
        return

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    print(f"Fetching agent card from: {a2a_endpoint}")
    response = httpx.get(a2a_endpoint, headers=headers)
    response.raise_for_status()
    a2ui_agent_card_json = response.json()

    # Add A2UI capabilities to the agent card.
    a2ui_agent_card_json["capabilities"] = {
        "streaming": False,
        "extensions": [{
            "uri": "https://a2ui.org/a2a-extension/a2ui/v0.8",
            "description": "Ability to render A2UI",
            "required": False,
            "params": {
                "supportedCatalogIds": [
                    "https://a2ui.org/specification/v0_8/standard_catalog_definition.json"
                ]
            },
        }],
    }
    a2ui_agent_card_str = json.dumps(a2ui_agent_card_json)

    print("✓ A2UI agent card fetched and updated.")

    unique_agent_id = f"combined_poc_{int(time.time())}"
    api_endpoint_register = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/"
        f"locations/global/collections/default_collection/engines/{app_id}/"
        f"assistants/default_assistant/agents?agentId={unique_agent_id}"
    )

    headers_register = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id,
    }

    payload = {
        "displayName": "combined_poc",
        "description": "A multi-skill agent that uses A2UI for contacts and pricing.",
        "a2aAgentDefinition": {"jsonAgentCard": a2ui_agent_card_str},
    }

    if agent_authorization:
        payload["authorization_config"] = {"agent_authorization": agent_authorization}

    print(f"Registering agent with Gemini Enterprise at: {api_endpoint_register}")
    response = requests.post(api_endpoint_register, headers=headers_register, json=payload)

    if response.status_code == 200:
        print(f"✓ Agent registered successfully with ID: {unique_agent_id}")
        print(response.json())
    else:
        print(f"✗ Registration failed with status code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    main()
