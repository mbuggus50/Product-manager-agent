# requirements_automation/base.py

import os
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Configuration and Environment Setup
class Config:
    DEFAULT_MODEL = "gpt-4o"
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_MAX_TOKENS = 4000
    DEBUG = True
    
    @classmethod
    def get_llm(cls, model=None, temperature=None):
        """Get a configured LLM instance"""
        return ChatOpenAI(
            model_name=model or cls.DEFAULT_MODEL,
            temperature=temperature or cls.DEFAULT_TEMPERATURE,
            max_tokens=cls.DEFAULT_MAX_TOKENS,
        )

# Base State Model for all teams
class WorkflowState(BaseModel):
    """Base state model for workflow management"""
    status: str = Field(default="initialized", description="Current status of the workflow")
    error: Optional[str] = Field(default=None, description="Error message if any")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Add helper methods for state management
    def is_error(self) -> bool:
        """Check if the state has an error"""
        return self.status == "error" and self.error is not None
    
    def is_completed(self) -> bool:
        """Check if the workflow is completed"""
        return self.status == "completed"
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the state"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default=None) -> Any:
        """Get metadata from the state"""
        return self.metadata.get(key, default)

# Executive State Model
class ExecutiveState(WorkflowState):
    """State model for Executive Supervisor"""
    current_team: str = Field(default="validation", description="Current active team")
    input_requirements: Dict[str, Any] = Field(default_factory=dict, description="Input requirements data")
    validation_results: Optional[Dict[str, Any]] = Field(default=None, description="Results from Validation team")
    content_results: Optional[Dict[str, Any]] = Field(default=None, description="Results from Content team")
    integration_results: Optional[Dict[str, Any]] = Field(default=None, description="Results from Integration team")
    final_output: Optional[Dict[str, Any]] = Field(default=None, description="Final processed output")

# Validation Team State
class ValidationState(WorkflowState):
    """State model for Validation Team"""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for validation")
    preprocessed_data: Optional[Dict[str, Any]] = Field(default=None, description="Preprocessed requirements data")
    completeness_check: Optional[Dict[str, Any]] = Field(default=None, description="Completeness check results")
    quality_check: Optional[Dict[str, Any]] = Field(default=None, description="Quality validation results")
    validation_summary: Optional[Dict[str, Any]] = Field(default=None, description="Summary of all validation results")

# Content Team State
class ContentState(WorkflowState):
    """State model for Content Team"""
    validated_requirements: Dict[str, Any] = Field(default_factory=dict, description="Validated requirements data")
    formatted_content: Optional[Dict[str, Any]] = Field(default=None, description="Formatted content")
    document_structure: Optional[Dict[str, Any]] = Field(default=None, description="Document structure and layout")
    design_elements: Optional[Dict[str, Any]] = Field(default=None, description="Design elements for the document")
    final_document: Optional[Dict[str, Any]] = Field(default=None, description="Final document content")

# Integration Team State
class IntegrationState(WorkflowState):
    """State model for Integration Team"""
    document_content: Dict[str, Any] = Field(default_factory=dict, description="Document content to be integrated")
    google_docs_status: Optional[Dict[str, Any]] = Field(default=None, description="Google Docs integration status")
    jira_status: Optional[Dict[str, Any]] = Field(default=None, description="JIRA integration status")
    wiki_status: Optional[Dict[str, Any]] = Field(default=None, description="Wiki integration status")
    slack_status: Optional[Dict[str, Any]] = Field(default=None, description="Slack notification status")
    integration_summary: Optional[Dict[str, Any]] = Field(default=None, description="Summary of all integrations")

# Utility functions for creating agent nodes
def create_llm_node(system_prompt: str, user_prompt: str, output_parser=None):
    """
    Creates a standard LLM node with appropriate prompting and parsing
    
    Args:
        system_prompt: The system prompt for the LLM
        user_prompt: The user prompt template
        output_parser: Parser for the LLM output (default: StrOutputParser)
    
    Returns:
        A runnable chain
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])
    
    llm = Config.get_llm()
    
    if output_parser is None:
        output_parser = StrOutputParser()
    
    return prompt | llm | output_parser

# Error handling decorator
def with_error_handling(func):
    """Decorator to add error handling to agent functions"""
    def wrapper(state):
        try:
            return func(state)
        except Exception as e:
            # Create a copy of the state to avoid modifying the original
            new_state = state.model_copy(deep=True)
            new_state.status = "error"
            new_state.error = str(e)
            return new_state
    return wrapper