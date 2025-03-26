import os
import asyncio
import chainlit as cl
from typing import Literal
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema.runnable.config import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Missing OPENAI_API_KEY in .env!")

# Define MCP server path
MCP_SERVER_PATH = os.path.abspath("./elasticsearch-mcp-server/main.py")

# Initialize base LLM
llm = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=0,
    openai_api_key=openai_api_key
)

# ---------------------- Tool Definitions ----------------------

@tool
def sonar_status(AppID: str) -> str:
    """Fetches the SonarQube analysis report for the given AppID."""
    return f"✅ SonarQube Analysis for AppID {AppID}: Passed with 2 critical issues."

@tool
def splunk_status(AppID: str) -> str:
    """Fetches the latest logs from Splunk for the given AppID."""
    return f"✅ Splunk Status for AppID {AppID}: No major errors found in the last 24 hours."

@tool
def appdynamics_status(AppID: str) -> str:
    """Fetches the latest application performance insights from AppDynamics for the given AppID."""
    return f"✅ AppDynamics Status for AppID {AppID}: Memory usage at 70%, CPU stable."

@tool
def overall_status(AppID: str) -> str:
    """Fetches an overall health report by aggregating results from SonarQube, Splunk, and AppDynamics."""
    sonar = sonar_status(AppID)
    splunk = splunk_status(AppID)
    appdynamics = appdynamics_status(AppID)
    return f"📊 **Overall Status for AppID {AppID}**:\n\n{sonar}\n{splunk}\n{appdynamics}"

@tool
def elastic_tool(query: str) -> str:
    """
    Forwards any ElasticSearch-related natural language query to a locally running MCP tool server.
    """

    async def run_elastic_agent():
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[MCP_SERVER_PATH]
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await load_mcp_tools(session)

                    model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=openai_api_key)
                    agent = create_react_agent(model, tools)
                    result = await agent.ainvoke({"messages": query})
                    return result.content if hasattr(result, "content") else str(result)


        except Exception as e:
            return f"❌ ElasticTool failed: {str(e)}"

    return asyncio.run(run_elastic_agent())

# ---------------------- Register Tools ----------------------

tools = [sonar_status, splunk_status, appdynamics_status, overall_status, elastic_tool]

llm = llm.bind_tools(tools).with_config(
    system_prompt=(
        "You are a monitoring assistant responsible for checking application health. "
        "You have access to the following tools:\n"
        "- SonarQube (`sonar_status`)\n"
        "- Splunk (`splunk_status`)\n"
        "- AppDynamics (`appdynamics_status`)\n"
        "- ElasticSearch (`elastic_tool`) - Accepts natural language queries for Elastic logs, metrics, or errors\n"
        "- Overall Status (`overall_status`) - Calls all other tools at once\n\n"
        "Use `elastic_tool` when the user asks any Elastic Search-related question like 'list indices', 'search logs', or 'error trends'."
        "All Elastic Operations that end user may ask are all supported by elastic_tool." 
        "Analyse Tool Responses, If they are JSON, DO Not Pass Them back as it, Clean them to make sure they are human readable,"
          "  Match them with Human Intent"
    )
)

# ---------------------- LangGraph Nodes ----------------------

tool_node = ToolNode(tools=tools)

def should_continue(state: MessagesState) -> Literal["tools", "final"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        tool_names = [tc['name'] for tc in last_message.tool_calls]
        print(f"🛠️ Tool(s) invoked: {tool_names}")
        return "tools"
    return "final"

def call_model(state: MessagesState):
    messages = state["messages"]
    response = llm.invoke(messages)
    if not response:
        print("🔴 [ERROR] LLM did not return a response!")
        response = AIMessage(content="⚠️ LLM failed to generate a response.")
    return {"messages": messages + [response]}

def pass_through_final(state: MessagesState):
    messages = state["messages"]
    if not messages or not messages[-1].content.strip():
        print("🔴 [ERROR] No final response generated!")
        return {"messages": [AIMessage(content="⚠️ No response generated. Please try again!")]}
    return {"messages": messages}

# ---------------------- Build Graph ----------------------

builder = StateGraph(MessagesState)

builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)
builder.add_node("final", pass_through_final)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "final")
builder.add_edge("final", END)

graph = builder.compile()

# ---------------------- Chainlit Integration ----------------------

def get_chat_history(new_message):
    if not hasattr(cl.user_session, "chat_history"):
        cl.user_session.chat_history = []
    cl.user_session.chat_history.append(new_message)
    return cl.user_session.chat_history

import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    # In Copilot mode, sessionParams are NOT sent here.
    # Just greet the user and wait for incident context to arrive via @on_message.
    await cl.Message(content="👋 Welcome! Please click on an incident to load its details.").send()

@cl.on_message
async def on_message(msg: cl.Message):
    import json
    print("📥 Received message from frontend:", msg)

    # ✅ Handle system message from Copilot
    if cl.context.session.client_type == "copilot" and msg.type == "system_message":
        print("✅ System message from Copilot received!")

        try:
            data = json.loads(msg.content)  # ✅ FIXED HERE
            cl.user_session.set("incident", data)

            await cl.Message(
                content=f"""✅ **Incident Context Received**
- **ID**: {data.get("id")}
- **Number**: {data.get("incidentnum")}
- **Short Description**: {data.get("shortDescription")}
- **Description**: {data.get("descrption")}
- **Priority**: {data.get("priority")}
- **Status**: {data.get("status")}
- **Opened At**: {data.get("openedAt")}
- **Resolved At**: {data.get("resolvedAt")}
"""
            ).send()
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
            await cl.Message(content=f"⚠️ Failed to load incident context.\n{e}").send()
        return

    # 🧠 Handle user messages via LangGraph agent
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content="")
    full_response = ""

    try:
        async for step, _ in graph.astream(
            {"messages": [HumanMessage(content=msg.content)]},
            stream_mode="messages",
            config=RunnableConfig(callbacks=[cb], **config),
        ):
            if step and getattr(step, "content", "").strip():
                full_response += step.content
                await final_answer.stream_token(step.content)
    except Exception as e:
        print(f"❌ LangGraph execution error: {e}")
        final_answer.content = f"⚠️ Error: {e}"
    else:
        final_answer.content = full_response.strip() or "⚠️ No response generated."

    await final_answer.send()





