"""Deployment script for the Combined Agent."""

import json
import os

from a2a.types import AgentSkill
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request
from google.genai import types
import httpx
import requests
import vertexai
from vertexai.preview.reasoning_engines import A2aAgent
from vertexai.preview.reasoning_engines.templates.a2a import create_agent_card

# Import the CombinedExecutor
from agents.combined_agent.executor import CombinedExecutor


def _get_bearer_token():
  """Gets a bearer token for authenticating with Google Cloud."""
  try:
    credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    request = Request()
    credentials.refresh(request)
    return credentials.token
  except Exception as e:  # pylint: disable=broad-except
    print(f"Error getting credentials: {e}")
    print(
        "Please ensure you have authenticated with 'gcloud auth "
        "application-default login'."
    )
  return None


def _register_agent_on_gemini_enterprise(
    project_id: str,
    app_id: str,
    agent_card: str,
    agent_name: str,
    display_name: str,
    description: str,
    agent_authorization: str | None = None,
):
  """Register an Agent Engine to Gemini Enterprise."""
  api_endpoint = (
      f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/"
      f"locations/global/collections/default_collection/engines/{app_id}/"
      "assistants/default_assistant/agents"
  )

  payload = {
      "name": agent_name,
      "displayName": display_name,
      "description": description,
      "a2aAgentDefinition": {"jsonAgentCard": agent_card},
  }

  if agent_authorization:
    payload["authorization_config"] = {"agent_authorization": agent_authorization}

  bearer_token = _get_bearer_token()
  headers = {
      "Authorization": f"Bearer {bearer_token}",
      "Content-Type": "application/json",
      "X-Goog-User-Project": project_id,
  }

  response = requests.post(api_endpoint, headers=headers, json=payload)

  if response.status_code == 200:
    print("✓ Agent registered successfully!")
    return response.json()
  print(f"✗ Registration failed with status code: {response.status_code}")
  print(f"Response: {response.text}")
  response.raise_for_status()


def main():
  load_dotenv()

  project_id = os.environ.get("PROJECT_ID")
  location = os.environ.get("LOCATION")
  storage = os.environ.get("STORAGE_BUCKET")
  app_id = os.environ.get("GEMINI_ENTERPRISE_APP_ID")
  api_endpoint = f"{location}-aiplatform.googleapis.com"

  print("≈" * 120)

  vertexai.init(
      project=project_id,
      location=location,
      api_endpoint=api_endpoint,
      staging_bucket=storage,
  )

  print("✓ Vertex AI client initialized.")

  client = vertexai.Client(
      project=project_id,
      location=location,
      http_options=types.HttpOptions(
          api_version="v1beta1",
      ),
  )
  print("✓ Vertex AI client created.")

  # Define skills
  skill_pricing = AgentSkill(
      id="get-pricing-comparison",
      name="Get Pricing Comparison",
      description="Compare prices for Nutella products.",
      tags=["pricing", "nutella", "competitor"],
      examples=[
          "Compare Nutella prices",
      ],
  )

  skill_contact = AgentSkill(
      id="contact_card_agent",
      name="Contact Card Agent",
      description="Find contact information for colleagues.",
      tags=["Contact-Card"],
      examples=[
          "Who is John Doe?",
          "List all contact cards.",
      ],
  )

  skill_a2ui_rendering = AgentSkill(
      id="a2ui-ui-rendering",
      name="A2UI UI Rendering",
      description="Generate rich interactive components like charts (VegaChart) and contact cards using the A2UI protocol.",
      tags=["a2ui", "ui", "chart", "widget"],
      examples=[
          "Show me a chart of prices",
          "Display contact card for user",
      ],
  )

  combined_agent_card = create_agent_card(
      agent_name="Combined Agent",
      description="A multi-skill agent that handles contact lookups and pricing analysis.",
      skills=[skill_pricing, skill_contact, skill_a2ui_rendering],
      default_input_modes=["text/plain"],
      default_output_modes=["text/plain"],
  )

  print(f"✓ Combined agent card created. {combined_agent_card}")

  # Create A2aAgent with CombinedExecutor
  a2ui_agent = A2aAgent(
      agent_card=combined_agent_card,
      agent_executor_builder=CombinedExecutor,
  )
  a2ui_agent.set_up()

  print("✓ Local Combined agent created.")

  config = {
      "display_name": "combined_poc",
      "description": (
          "A multi-skill agent that uses A2UI for contacts and pricing."
      ),
      "agent_framework": "google-adk",
      "staging_bucket": storage,
      "gcs_dir_name": "dev_combined",
      "requirements": [
          "google-cloud-aiplatform[agent_engines,adk]",
          "google-genai>=1.27.0",
          "python-dotenv>=1.1.0",
          "uvicorn",
          "a2a-sdk>=0.3.4",
          "cloudpickle>=3.1.2",
          "pydantic",
          "jsonschema>=4.0.0",
          "a2ui-agent-sdk>=0.1.2",
      ],
      "http_options": {
          "api_version": "v1beta1",
      },
      "max_instances": 1,
      "extra_packages": [
          "agents/combined_agent",
          "tools.py",
          "contact_data.json",
          "examples",
      ],
      "env_vars": {
          "NUM_WORKERS": "1",
      },
  }

  remote_agent = client.agent_engines.create(agent=a2ui_agent, config=config)

  remote_engine_resource = remote_agent.api_resource.name
  print(f"✓ Remote agent created. {remote_engine_resource}")

  a2a_endpoint = f"https://{api_endpoint}/v1beta1/{remote_engine_resource}/a2a/v1/card"
  bearer_token = _get_bearer_token()
  headers = {
      "Authorization": f"Bearer {bearer_token}",
      "Content-Type": "application/json",
  }

  print(f"✓ A2A endpoint: {a2a_endpoint}")

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

  print("✓ A2UI agent card fetched.")

  enterprise_agent = _register_agent_on_gemini_enterprise(
      project_id=project_id,
      app_id=app_id,
      agent_card=a2ui_agent_card_str,
      agent_name="combined_poc",
      display_name="combined_poc",
      description="A multi-skill agent that uses A2UI for contacts and pricing.",
      agent_authorization=os.environ.get("AGENT_AUTHORIZATION"),
  )

  print(enterprise_agent)
  print("≈" * 120)


if __name__ == "__main__":
  main()
