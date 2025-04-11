#!/usr/bin/env python3
"""
validation_team.py

This script implements a validation workflow using LangGraph, in which
human-in-the-loop (human feedback) is achieved by collecting input from the
console via Python's input() function.

The workflow includes the following agents:
    - Preprocessor: Standardizes and preprocesses the requirements.
    - Validator: Checks the preprocessed data against criteria.
    - Human Feedback: If issues exist, prompts the user for updates.
    - Finalizer: Completes the process if validation passes.
    - Supervisor: Routes control between agents.

Requirements:
    - langchain_core and langgraph packages should be installed.
    - An appropriate API key must be set for ChatOpenAI.

Usage:
    Run from the command-line:
        python validation_team.py
"""

import operator
import json
from typing import Dict, Any, List, TypedDict, Literal, Annotated

from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.types import Command  # interrupt still imported if needed
from langgraph.checkpoint.memory import MemorySaver

# Define the validation criteria (each field must meet the following guidelines)
REQUIRED_FIELDS = {
    "business_need": {
        "min_length": 20,
        "required": True,
        "description": "A clear description of what the business is asking for and its impact"
    },
    "requirements": {
        "min_length": 30,
        "required": True,
        "description": "Detailed requirements information"
    },
    "business_impact": {
        "min_length": 20,
        "required": True,
        "description": "Description of business impact if delivered or not delivered"
    },
    "delivery_date": {
        "min_length": 5,
        "required": True,
        "description": "When this is needed to be delivered"
    },
    "campaign_date": {
        "min_length": 5,
        "required": True,
        "description": "Campaign or product launch date"
    },
    "contributors": {
        "min_length": 1,
        "required": True,
        "description": "List of contributors to the requirement"
    }
}


# Define the state for the workflow using a TypedDict
class ValidationState(TypedDict):
    """
    State for the validation workflow.
    
    Attributes:
        messages: List of messages exchanged between agents.
        next: The next node to execute.
        input_requirements: Original input requirements.
        preprocessed_data: Standardized and preprocessed data.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    next: str
    input_requirements: Dict[str, Any]
    preprocessed_data: Dict[str, Any]


# Initialize the ChatOpenAI model (replace with your API key)
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=""
)


def preprocessor_agent(state: ValidationState) -> Command:
    """
    Preprocess the requirements data.
    """
    print("Preprocessor agent working...")
    input_data = state["input_requirements"]
    preprocessed_data = {}

    # Process each field; if missing, set as empty string.
    for field, criteria in REQUIRED_FIELDS.items():
        preprocessed_data[field] = input_data.get(field, "")

    message = HumanMessage(
        content=f"I've preprocessed the requirements data. Here's the standardized format:\n{json.dumps(preprocessed_data, indent=2)}",
        name="preprocessor"
    )
    return Command(
        update={"messages": [message], "preprocessed_data": preprocessed_data},
        goto="supervisor"
    )


def validator_agent(state: ValidationState) -> Command:
    """
    Validate the preprocessed data against required criteria.
    """
    print("Validator agent working...")
    data = state["preprocessed_data"]
    issues = {}

    for field, criteria in REQUIRED_FIELDS.items():
        field_issues = []
        # Check required fields
        if criteria["required"] and not data.get(field):
            field_issues.append(f"Field '{field}' is required but missing")
        # Check minimum length requirement
        if data.get(field) and len(str(data[field])) < criteria["min_length"]:
            field_issues.append(
                f"Field '{field}' is too short. Minimum length is {criteria['min_length']} characters. "
                f"Current length: {len(str(data[field]))} characters."
            )
        if field_issues:
            issues[field] = field_issues

    if issues:
        issues_text = ""
        for field, field_issues in issues.items():
            description = REQUIRED_FIELDS[field]["description"]
            issues_text += f"\n## {field} ({description}):\n"
            for issue in field_issues:
                issues_text += f"- {issue}\n"

        message = HumanMessage(
            content=f"I've found validation issues with the requirements:\n{issues_text}\nHuman feedback is needed to address these issues.",
            name="validator"
        )
        return Command(update={"messages": [message]}, goto="human_feedback")
    else:
        message = HumanMessage(
            content="The requirements have passed validation against all criteria.",
            name="validator"
        )
        return Command(update={"messages": [message]}, goto="finalizer")


def human_feedback_agent(state: ValidationState) -> Command:
    """
    Collect human feedback via console input.
    
    The feedback is expected in valid JSON format. Upon receiving feedback,
    the state is updated with the new data and control returns to the supervisor.
    """
    print("Human feedback agent working...")
    last_message = state["messages"][-1]
    current_data_text = json.dumps(state["preprocessed_data"], indent=2)

    feedback_prompt = f"""
{last_message.content}

Current requirements data:
```json
{current_data_text}
```
Please provide updated requirements data in valid JSON format that addresses the validation issues. 
You may provide the complete updated JSON or only specific field updates.
"""

    # Collect human input from the console
    feedback = input(feedback_prompt + "\nYour input: ")

    try:
        updated_data = json.loads(feedback)
    except Exception as e:
        error_msg = f"Error: The provided feedback is not valid JSON. Please try again. (Detail: {e})"
        return Command(
            update={"messages": [HumanMessage(content=error_msg, name="human_feedback")]}
        )

    return Command(
        update={
            "preprocessed_data": updated_data,
            "messages": [HumanMessage(content="Human feedback processed successfully.", name="human_feedback")]
        },
        goto="supervisor"
    )


def finalizer_agent(state: ValidationState) -> Command:
    """
    Finalize the validation process after successful validation.
    """
    print("Finalizer agent working...")
    data = state["preprocessed_data"]
    results = {
        "is_valid": True,
        "validated_data": data,
        "summary": "All requirements have been validated and meet the criteria."
    }
    message = HumanMessage(
        content=f"Validation process completed successfully. The requirements are valid and can proceed to the next stage.\n\nValidated Requirements:\n{json.dumps(data, indent=2)}",
        name="finalizer"
    )
    return Command(update={"messages": [message]}, goto="FINISH")


# Team members and supervisor options
members = ["preprocessor", "validator", "human_feedback", "finalizer"]
options = members + ["FINISH"]

system_prompt = (
    "You are a validation supervisor tasked with managing a conversation between the following specialists: " 
    + ", ".join(members) 
    + ". Given the following conversation, respond with which specialist should work next. "
    "If the validation process is complete, respond with FINISH."
)


# Define the supervisor's routing schema
class RouterOutput(BaseModel):
    next: Literal["preprocessor", "validator", "human_feedback", "finalizer", "FINISH"]


prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Given the conversation above, who should act next? Or should we FINISH? "
              f"Select one of: {', '.join(options)}")
])

supervisor_chain = prompt | llm.with_structured_output(RouterOutput)


def create_validation_workflow():
    """
    Create the full validation workflow using the agent-supervisor pattern.
    """
    workflow = StateGraph(ValidationState)
    
    # Add nodes
    workflow.add_node("preprocessor", preprocessor_agent)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("human_feedback", human_feedback_agent)
    workflow.add_node("finalizer", finalizer_agent)
    workflow.add_node("supervisor", supervisor_chain)

    # Route supervisor output to agents
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "preprocessor": "preprocessor",
            "validator": "validator",
            "human_feedback": "human_feedback",
            "finalizer": "finalizer",
            "FINISH": END
        }
    )
    
    # All agents return to supervisor
    workflow.add_edge("preprocessor", "supervisor")
    workflow.add_edge("validator", "supervisor")
    workflow.add_edge("human_feedback", "supervisor")
    workflow.add_edge("finalizer", "supervisor")

    workflow.set_entry_point("supervisor")
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def run_validation_example(thread_id):
    """
    Run a test example of the validation workflow.
    """
    validation_workflow = create_validation_workflow()

    # Sample input requirements (with intentional issues)
    input_requirements = {
        "business_need": "New feature",  # Too short
        "requirements": "Add a button to the homepage",  # Too short
        "business_impact": "Important for users",  # Too short
        "delivery_date": "Soon",  # Too short
        # Missing campaign_date
        "contributors": ["John"]
    }
    valid_input = {
                "business_need": "We need to add a prominent call-to-action button to increase user engagement with our product offerings",
                "requirements": "The button should be blue, positioned centrally on the homepage, and link to the products page. It should have tracking for analytics.",
                "business_impact": "This change is expected to increase clickthrough rates by 15% and improve conversion by at least 5%",
                "delivery_date": "June 15, 2025",
                "campaign_date": "July 1, 2025",
                "contributors": ["John", "Sarah", "Marketing Team"]
            }

    initial_state = {
        "messages": [
            SystemMessage(content="Let's validate these requirements."),
            HumanMessage(content=f"I need to validate these requirements: {json.dumps(input_requirements, indent=2)}")
        ],
        "next": "preprocessor",
        "input_requirements": input_requirements,
        "preprocessed_data": {}
    }

    config = {"configurable": {"thread_id": thread_id}}

    print("Starting validation workflow...\n")
    try:
        for event in validation_workflow.stream(initial_state, config, stream_mode="values"):
            print(f"\nCurrent state:")
            print(f"- Next step: {event.get('next', 'unknown')}")
            if "messages" in event and event["messages"]:
                latest_message = event["messages"][-1]
                sender = getattr(latest_message, 'name', 'unknown')
                content = latest_message.content
                print(f"- Latest message from: {sender}")
                if len(content) > 100:
                    print(f"- Content: {content[:100]}...")
                else:
                    print(f"- Content: {content}")
    except Exception as e:
        if "interrupt" in str(e).lower():
            print("\nWorkflow interrupted for human feedback.")
            print("Please provide the required input as prompted.")
        else:
            print(f"Error running workflow: {e}")


if __name__ == "__main__":
    run_validation_example("1")