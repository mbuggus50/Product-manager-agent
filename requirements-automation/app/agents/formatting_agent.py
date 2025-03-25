from typing import Dict, List, Any
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FormattingAgent:
    """
    Formatting agent to structure validated requirements into PRD format.
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", temperature: float = 0.1):
        """Initialize the formatting agent with specified LLM."""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        # Create the formatting prompt
        self.formatting_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are a PRD formatting expert. Your task is to take validated requirement information and format it 
            according to the Intuit Data Engineering PRD template.
            
            Follow these guidelines:
            1. Extract key business need information and format it clearly
            2. Structure requirements in the standard format with who/what/where/when/why
            3. Format business impact statements concisely
            4. Structure timeline information properly
            5. Format contributor information
            6. Create properly formatted tables for definitions and mappings if provided
            
            Output the formatted content for each section of the PRD template.
            
            Output format:
            {
                "business_need": "formatted business need",
                "requirements": [{"name": "req name", "description": "desc", "who_what_where_when_why": "details"}],
                "business_impact": "formatted impact statement",
                "timeline": {"delivery_date": "date", "campaign_date": "date"},
                "contributors": ["person1", "person2"],
                "definitions": [{"attribute": "attr1", "definition": "def1"}],
                "mapping_tables": [{"attribute": "attr", "type": "type", "source": "src", "destination": "dest"}]
            }
            """),
            HumanMessage(content="{input}"),
        ])
        
        # Create the parser
        self.output_parser = JsonOutputParser()
        
        # Create the chain
        self.formatting_chain = self.formatting_prompt | self.llm | self.output_parser
    
    def format(self, requirement_data: Dict[str, Any], validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the validated requirement data into PRD structure.
        
        Args:
            requirement_data: The validated requirement data
            validation_results: The validation results
            
        Returns:
            Formatted PRD content as a dictionary
        """
        logger.info("Starting formatting of requirement submission")
        
        try:
            # Only proceed if the requirement is valid
            if not validation_results.get("is_valid", False):
                logger.warning("Attempting to format an invalid requirement")
                return {
                    "error": "Cannot format an invalid requirement",
                    "validation_issues": validation_results
                }
            
            # Prepare input for LLM
            formatting_input = {
                "input": {
                    **requirement_data,
                    "validation_results": validation_results
                }
            }
            
            # Run the formatting
            formatted_prd = self.formatting_chain.invoke(formatting_input)
            
            # Log the results
            logger.info("Formatting complete")
            
            return formatted_prd
        
        except Exception as e:
            logger.error(f"Error during formatting: {str(e)}")
            # Return an error response
            return {
                "error": f"Error during formatting: {str(e)}",
                "formatted": False
            }