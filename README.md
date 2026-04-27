# Combined A2UI Agent (Refactored)

This project contains a multi-skill AI agent built with the **Google Agent Development Kit (ADK)** and the **Agent-to-Agent (A2A)** protocol. It provides interactive UI components (Contact Cards and Pricing Charts) for **Gemini Enterprise**.

## 1. Project Structure

The project follows the standard `agent-starter-pack` structure:
- **`app/`**: Core agent logic and tools.
  - **`agent.py`**: Agent definition, prompts, and tool registration.
  - **`executor.py`**: A2A protocol implementation and A2UI JSON parsing.
  - **`tools.py`**: Tool implementations (e.g., `get_contact_info`).
  - **`contact_data.json`**: Mock data for contacts.
  - **`agent_runtime_app.py`**: Entry point for Agent Engine (Reasoning Engine) deployment.
- **`evalsets/`**: Evaluation sets for systematic testing.
- **`examples/0.8/`**: A2UI component examples.
- **`Makefile`**: Standard developer workflows.

## 2. Developer Workflows

This project uses `agents-cli` and a `Makefile` to manage the development lifecycle.

### Setup
Ensure you have `uv` and `gcloud` installed.
```bash
make install
```

### Local Testing
Run a quick smoke test or open the interactive playground:
```bash
# Smoke test
agents-cli run "List all contact cards"

# Interactive Playground
make playground
```

### Evaluation
Systematically test the agent's performance against core use cases:
```bash
make eval
```

### Deployment
Deploy the agent to **Agent Engine** (Vertex AI):
```bash
make deploy
```

## 3. A2A & A2UI
This agent uses the **A2A** protocol to communicate with Gemini Enterprise and the **A2UI** extension to render rich components. It is configured to handle specialized UI events like `view_profile` and `send_email`.

---
*Refer to the original `GEMINI.md` for detailed coding guidelines and ADK patterns.*
