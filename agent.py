import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

# --- Custom Tools ---

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's river inquiry to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

# Configuring the Wikipedia Tool for general geographical knowledge
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# --- Agent Definitions ---

# 1. River Researcher Agent
comprehensive_researcher = Agent(
    name="river_researcher",
    model=model_name,
    description="The primary researcher that accesses geographical data and external hydrological knowledge from Wikipedia.",
    instruction="""
    You are an expert Hydrologist and Geographer. Your goal is to fully answer the user's PROMPT regarding rivers, lakes, or water bodies.
    You have access to two tools:
    1. A tool for getting specific data from our INTERNAL HYDROLOGY DATABASE (current water levels, local sensor data, ecological status).
    2. A tool for searching Wikipedia for general river knowledge (length, source, mouth, discharge rate, historical significance).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both internal sensors AND Wikipedia,
      you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary research data.

    PROMPT:
    { PROMPT }
    """,
    tools=[
        wikipedia_tool
    ],
    output_key="research_data" # Stores findings for the next agent
)

# 2. Hydrological Report Formatter Agent
response_formatter = Agent(
    name="report_formatter",
    model=model_name,
    description="Synthesizes all geographical and hydrological information into a professional report.",
    instruction="""
    You are the Chief Geographer. Your task is to take the
    RESEARCH_DATA and present it to the user in a complete, educational, and well-structured report.

    - First, present the specific information regarding internal data (like current sensor readings or expedition status, if any).
    - Then, add the interesting geographical facts from the general research (like length, basin size, wildlife, or ecological significance).
    - If some information is missing, just present the best data you have available.
    - Use a professional, ecological, and clear tone.

    RESEARCH_DATA:
    { research_data }
    """
)

# --- Workflow Setup ---

river_explorer_workflow = SequentialAgent(
    name="river_explorer_workflow",
    description="The main workflow for handling a user's request about a river or water body.",
    sub_agents=[
        comprehensive_researcher, # Step 1: Gather hydrological data
        response_formatter,       # Step 2: Format the geographical report
    ]
)

root_agent = Agent(
    name="hydrology_institute_greeter",
    model=model_name,
    description="The main entry point for the Global Hydrology Institute.",
    instruction="""
    - Welcome the user to the Global Hydrology Institute.
    - Let the user know you can help them learn about rivers, watersheds, and aquatic ecosystems around the world.
    - When the user responds with a destination or river name, use the 'add_prompt_to_state' tool to save their response.
    - After using the tool, transfer control to the 'river_explorer_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[river_explorer_workflow]
)