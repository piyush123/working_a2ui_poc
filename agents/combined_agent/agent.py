import os
import logging
from google.adk.agents import Agent
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.common_modifiers import remove_strict_validation
from a2ui.schema.constants import VERSION_0_8

logger = logging.getLogger(__name__)

# Import tools
from tools import get_contact_info

# Inlined tool from pricing agent
def get_pricing_comparison(title_query: str) -> str:
    """Gets pricing data for Nutella products from BigQuery for both our shop and competitors."""
    import json
    mock_data = [
        {"county": "US", "source": "Our Shop", "price": 5.99, "product": "Nutella 400g"},
        {"county": "US", "source": "Competitor A", "price": 6.49, "product": "Nutella 400g"},
        {"county": "US", "source": "Competitor B", "price": 5.49, "product": "Nutella 400g"}
    ]
    return json.dumps(mock_data)

ROLE_DESCRIPTION = "You are a multi-skill assistant agent. Your job is to help find contact information for colleagues AND analyze competitor prices for products."

WORKFLOW_DESCRIPTION = """
For Contact Queries:
1. Answer user questions about colleagues' contact info.
2. Return a contact card UI.

For Pricing Queries:
1. You MUST ALWAYS call `get_pricing_comparison` first to look up pricing data for the requested product. Do not assume data.
2. After receiving the data, you MUST return a price comparison chart.
3. Present clean, user-friendly pricing insights along with the chart.
"""

UI_DESCRIPTION = """
- For contact cards, follow the standard contact card layout.
- For pricing charts, you MUST generate a price comparison chart using the VegaChart component. The chart data MUST be wrapped in `<a2ui-json>` and `</a2ui-json>` tags. DO NOT output raw JSON without these tags.
"""

def create_agent() -> Agent:
    schema_manager = A2uiSchemaManager(
        version=VERSION_0_8,
        catalogs=[
            BasicCatalog.get_config(
                version=VERSION_0_8,
                examples_path=os.path.join(
                    os.path.dirname(__file__), "../../examples/0.8"
                ),
            )
        ],
        schema_modifiers=[remove_strict_validation],
    )

    instruction = schema_manager.generate_system_prompt(
        role_description=ROLE_DESCRIPTION,
        workflow_description=WORKFLOW_DESCRIPTION,
        ui_description=UI_DESCRIPTION,
        include_schema=True,
        include_examples=True,
        validate_examples=False,
    )

    agent = Agent(
        name="CombinedAgent",
        model=os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.5-flash"),
        description="A multi-skill agent that handles contact lookups and pricing analysis.",
        instruction=instruction,
        tools=[get_contact_info, get_pricing_comparison]
    )

    return agent

_root_agent = None

def get_agent() -> Agent:
    global _root_agent
    if _root_agent is None:
        _root_agent = create_agent()
    return _root_agent

root_agent = get_agent()
