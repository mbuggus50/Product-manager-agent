# requirements_automation/content_team.py

from typing import Dict, Any, List, Optional
import json
from pydantic import BaseModel, Field

from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END

from requirements_automation.base import (
    ContentState, 
    create_llm_node, 
    with_error_handling,
    Config
)

# JSON Schema for content outputs
class FormattedContent(BaseModel):
    sections: List[Dict[str, Any]] = Field(description="Organized sections of content")
    formatting_applied: List[str] = Field(description="List of formatting rules applied")
    readability_score: float = Field(description="Score from 0-1 indicating readability")

class DocumentStructure(BaseModel):
    structure_type: str = Field(description="Type of document structure (hierarchical, sequential, etc.)")
    toc_elements: List[str] = Field(description="Table of contents elements")
    sections: List[Dict[str, Any]] = Field(description="Document sections with headings and content")
    metadata: Dict[str, Any] = Field(description="Document metadata")

class DesignElements(BaseModel):
    theme: str = Field(description="Document theme")
    fonts: Dict[str, str] = Field(description="Font choices for different elements")
    colors: Dict[str, str] = Field(description="Color scheme")
    styling_rules: List[Dict[str, Any]] = Field(description="Styling rules for different elements")
    visual_elements: List[Dict[str, Any]] = Field(description="Additional visual elements")

class FinalDocument(BaseModel):
    title: str = Field(description="Document title")
    version: str = Field(description="Document version")
    sections: List[Dict[str, Any]] = Field(description="Final document sections")
    appendices: Optional[List[Dict[str, Any]]] = Field(default=None, description="Document appendices")
    metadata: Dict[str, Any] = Field(description="Final document metadata")
    toc: List[Dict[str, Any]] = Field(description="Table of contents")
    styling: Dict[str, Any] = Field(description="Document styling information")

# Agent implementations
@with_error_handling
def formatting_agent(state: ContentState) -> ContentState:
    """
    Formats the requirements content according to standards and best practices.
    """
    new_state = state.model_copy(deep=True)
    
    # Define the formatting agent
    formatting_prompt = """
    You are a Requirements Formatting Agent. Your job is to:
    1. Organize requirements into a logical structure
    2. Apply consistent formatting to all requirements
    3. Ensure language consistency and clarity
    4. Improve readability with appropriate headings, lists, and sections
    5. Standardize terminology throughout the document
    
    Return a JSON object with the formatted content, following this schema:
    {
        "sections": [
            {"title": "section_title", "content": "formatted_content", "requirements": [...]},
            ...
        ],
        "formatting_applied": ["rule1", "rule2", ...],
        "readability_score": float (0-1)
    }
    """
    
    formatting_agent = create_llm_node(
        system_prompt=formatting_prompt,
        user_prompt="Format the following validated requirements:\n\n{validated_requirements}",
        output_parser=JsonOutputParser()
    )
    
    # Format content
    new_state.formatted_content = formatting_agent.invoke({"validated_requirements": json.dumps(new_state.validated_requirements)})
    new_state.status = "formatted"
    
    return new_state

@with_error_handling
def document_agent(state: ContentState) -> ContentState:
    """
    Creates the document structure with sections, headings, and organization.
    """
    new_state = state.model_copy(deep=True)
    
    if not new_state.formatted_content:
        new_state.status = "error"
        new_state.error = "Missing formatted content"
        return new_state
    
    # Define the document agent
    document_prompt = """
    You are a Document Structure Agent. Your job is to:
    1. Create a logical document structure for the requirements
    2. Organize content into chapters, sections, and subsections
    3. Generate appropriate headings and subheadings
    4. Create a table of contents
    5. Add necessary front matter and appendices
    
    Return a JSON object with the document structure, following this schema:
    {
        "structure_type": "structure_type",
        "toc_elements": ["element1", "element2", ...],
        "sections": [
            {"level": 1, "title": "title", "content_ref": "content_id", "subsections": [...]},
            ...
        ],
        "metadata": {
            "title": "document_title",
            "version": "document_version",
            "date": "creation_date",
            ...
        }
    }
    """
    
    document_agent = create_llm_node(
        system_prompt=document_prompt,
        user_prompt="Create a document structure for the following formatted content:\n\n{formatted_content}",
        output_parser=JsonOutputParser()
    )
    
    # Create document structure
    new_state.document_structure = document_agent.invoke({"formatted_content": json.dumps(new_state.formatted_content)})
    new_state.status = "structured"
    
    return new_state

@with_error_handling
def design_agent(state: ContentState) -> ContentState:
    """
    Adds design elements, styling, and visual improvements to the document.
    """
    new_state = state.model_copy(deep=True)
    
    if not new_state.document_structure:
        new_state.status = "error"
        new_state.error = "Missing document structure"
        return new_state
    
    # Define the design agent
    design_prompt = """
    You are a Document Design Agent. Your job is to:
    1. Define a visually appealing theme for the document
    2. Specify fonts, colors, and styling for different document elements
    3. Add visual elements like tables, diagrams, or callouts where appropriate
    4. Enhance readability through formatting and whitespace
    5. Ensure consistent styling throughout the document
    
    Return a JSON object with the design elements, following this schema:
    {
        "theme": "theme_name",
        "fonts": {
            "headings": "font_name",
            "body": "font_name",
            ...
        },
        "colors": {
            "primary": "color_code",
            "secondary": "color_code",
            ...
        },
        "styling_rules": [
            {"element": "element_type", "style": "style_description"},
            ...
        ],
        "visual_elements": [
            {"type": "element_type", "location": "section_reference", "description": "description"},
            ...
        ]
    }
    """
    
    design_agent = create_llm_node(
        system_prompt=design_prompt,
        user_prompt="""Design the visual elements for the following document:
        
        Document Structure:
        {document_structure}
        
        Formatted Content:
        {formatted_content}
        """,
        output_parser=JsonOutputParser()
    )
    
    # Create design elements
    new_state.design_elements = design_agent.invoke({
        "document_structure": json.dumps(new_state.document_structure),
        "formatted_content": json.dumps(new_state.formatted_content)
    })
    new_state.status = "designed"
    
    return new_state

@with_error_handling
def content_finalizer(state: ContentState) -> ContentState:
    """
    Finalizes the document by combining structure, content, and design elements.
    """
    new_state = state.model_copy(deep=True)
    
    if not new_state.formatted_content or not new_state.document_structure or not new_state.design_elements:
        new_state.status = "error"
        new_state.error = "Missing required content components"
        return new_state
    
    # Define the content finalizer agent
    finalizer_prompt = """
    You are a Content Finalizer. Your job is to:
    1. Combine the formatted content, document structure, and design elements
    2. Create a complete, publication-ready document
    3. Ensure all elements are properly integrated
    4. Finalize metadata, headers, footers, and page numbering
    5. Generate a comprehensive document that meets all requirements
    
    Return a JSON object with the final document, following this schema:
    {
        "title": "document_title",
        "version": "document_version",
        "sections": [
            {"title": "section_title", "content": "section_content", "level": level, "subsections": [...]},
            ...
        ],
        "appendices": [
            {"title": "appendix_title", "content": "appendix_content"},
            ...
        ],
        "metadata": {
            "author": "author_name",
            "date": "creation_date",
            ...
        },
        "toc": [
            {"title": "entry_title", "page": page_number, "level": level},
            ...
        ],
        "styling": {
            "theme": "theme_name",
            "fonts": {...},
            "colors": {...},
            ...
        }
    }
    """
    
    finalizer_agent = create_llm_node(
        system_prompt=finalizer_prompt,
        user_prompt="""Finalize the document based on the following components:
        
        Formatted Content:
        {formatted_content}
        
        Document Structure:
        {document_structure}
        
        Design Elements:
        {design_elements}
        """,
        output_parser=JsonOutputParser()
    )
    
    # Finalize document
    new_state.final_document = finalizer_agent.invoke({
        "formatted_content": json.dumps(new_state.formatted_content),
        "document_structure": json.dumps(new_state.document_structure),
        "design_elements": json.dumps(new_state.design_elements)
    })
    new_state.status = "completed"
    
    return new_state

# Content Supervisor - Decision function for workflow routing
def content_router(state: ContentState) -> str:
    """Routes the workflow based on the current state"""
    if state.is_error():
        return "error"
    
    if not state.formatted_content:
        return "format"
    elif not state.document_structure:
        return "structure"
    elif not state.design_elements:
        return "design"
    elif not state.final_document:
        return "finalize"
    else:
        return "end"

# Create the Content Team workflow
def create_content_workflow() -> StateGraph:
    """Creates the Content Team workflow graph"""
    workflow = StateGraph(ContentState)
    
    # Add nodes
    workflow.add_node("format", formatting_agent)
    workflow.add_node("structure", document_agent)
    workflow.add_node("design", design_agent)
    workflow.add_node("finalize", content_finalizer)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        None,
        content_router,
        {
            "format": "format",
            "structure": "structure",
            "design": "design",
            "finalize": "finalize",
            "error": END,
            "end": END
        }
    )
    
    workflow.add_edge("format", None)
    workflow.add_edge("structure", None)
    workflow.add_edge("design", None)
    workflow.add_edge("finalize", None)
    
    return workflow.compile()