# First we initialize the model we want to use.
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from botrun_flow_lang.langgraph_agents.agents.util.pdf_analyzer import analyze_pdf
from botrun_flow_lang.models.nodes.utils import scrape_single_url
from botrun_flow_lang.models.nodes.vertex_ai_search_node import VertexAISearch
from datetime import datetime
from botrun_flow_lang.langgraph_agents.agents.search_agent_graph import format_dates
from langgraph.checkpoint.memory import MemorySaver

import pytz
import asyncio

# model = ChatOpenAI(model="gpt-4o", temperature=0)
model = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)


# For this tutorial we will use custom tool that returns pre-defined values for weather in two cities (NYC & SF)

from typing import Literal

from langchain_core.tools import tool


@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")


@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# This will be a tool
@tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


@tool
def search(keywords: str):
    """
    Use this to search the web.

    Args:
        keywords: the keywords to search for, use space to separate multiple keywords, e.g. "台灣 政府 福利"
    """
    try:
        vertex_ai_search = VertexAISearch()
        search_results = vertex_ai_search.vertex_search(
            project_id="scoop-386004",
            location="global",
            data_store_id="tw-gov-welfare_1730944342934",
            search_query=keywords,
        )
        return search_results
    except Exception as e:
        return f"Error: {e}"


@tool
def scrape(url: str):
    """
    Use this to scrape the web.

    Args:
        url: the url to scrape
    """
    try:
        return asyncio.run(scrape_single_url(url))
    except Exception as e:
        return f"Error: {e}"


@tool
def current_time():
    """
    Use this to get the current time in local timezone.
    """
    try:
        local_tz = pytz.timezone("Asia/Taipei")
        local_time = datetime.now(local_tz)
        return local_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Error: {e}"


@tool
def days_between(start_date: str, end_date: str):
    """
    Use this to get the days between two dates.

    Args:
        start_date: the start date, format: YYYY-MM-DD
        end_date: the end date, format: YYYY-MM-DD
    """
    return (
        datetime.strptime(end_date, "%Y-%m-%d")
        - datetime.strptime(start_date, "%Y-%m-%d")
    ).days


@tool
def chat_with_pdf(pdf_path: str, user_input: str):
    """
    Use this to chat with a PDF file.
    User can ask about any text, pictures, charts, and tables in PDFs that is provided. Some sample use cases:
    - Analyzing financial reports and understanding charts/tables
    - Extracting key information from legal documents
    - Translation assistance for documents
    - Converting document information into structured formats

    Args:
        pdf_path: the file path to the PDF file
        user_input: the user's input
    """
    return analyze_pdf(pdf_path, user_input)


tools = [current_time, scrape, days_between, chat_with_pdf]


# Define the graph
from langgraph.prebuilt import create_react_agent

now = datetime.now()
dates = format_dates(now)
western_date = dates["western_date"]
taiwan_date = dates["taiwan_date"]


def create_react_agent_graph(system_prompt: str = ""):
    """
    Create a react agent graph with optional system prompt

    Args:
        system_prompt: The system prompt to use for the agent
    """
    return create_react_agent(
        model,
        tools=tools,
        state_modifier=system_prompt,
        checkpointer=MemorySaver(),
    )


# Default graph instance with empty prompt
graph = create_react_agent_graph()
