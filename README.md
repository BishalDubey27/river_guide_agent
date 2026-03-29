# River Guide Agent

Welcome to the **Global Hydrology Institute** assistant! This project is a multi-agent system built using the Google Agent Development Kit (ADK) and LangChain. It is designed to act as an expert hydrologist and geographer, providing comprehensive research and reports on rivers, lakes, and other water bodies around the world.

## 🔗 Live App

[**Click here to view the live application!**](https://river-tour-guide-653423988024.europe-west1.run.app)
*(Note: Replace the link above with the actual URL where your app is hosted)*

## 🏗️ Agent Workflow

The system utilizes a hierarchical and sequential workflow with several specialized agents working together:

1. **Root Agent (`hydrology_institute_greeter`)**
   - **Role:** The main entry point.
   - **Action:** Welcomes the user, asks for a specific destination or river name, and uses a custom tool (`add_prompt_to_state`) to save the user's inquiry into the application's shared state. It then transfers control to the main workflow.

2. **River Explorer Workflow (`river_explorer_workflow`)**
   - **Role:** The orchestrator.
   - **Action:** A `SequentialAgent` that manages the execution of the research and reporting sub-agents step-by-step.

3. **Step 1: River Researcher (`comprehensive_researcher`)**
   - **Role:** Expert Hydrologist.
   - **Action:** Reads the user's prompt from the state and uses external tools (such as Wikipedia via LangChain) to gather geographical, hydrological, and historical facts about the requested water body. It outputs its findings into the state as `research_data`.

4. **Step 2: Report Formatter (`response_formatter`)**
   - **Role:** Chief Geographer.
   - **Action:** Takes the raw `research_data` generated in the previous step and synthesizes it into a well-structured, professional, and educational final report for the user.

## 🛠️ Built With

- Google Agent Development Kit (ADK)
- LangChain (Wikipedia Integration)
- Python & Google Cloud Logging
