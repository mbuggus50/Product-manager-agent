from typing import Dict, List, Any
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser

from app.integrations.wiki import WikiIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DesignAgent:
    """
    Design agent to create technical design documents in wiki.
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4-turbo-preview", 
                 temperature: float = 0.1,
                 wiki_credentials: Dict[str, str] = None):
        """Initialize the design agent with specified LLM and integrations."""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        # Initialize wiki integration if credentials are provided
        self.wiki = WikiIntegration(**wiki_credentials) if wiki_credentials else None
        
        # Create the design document prompt
        self.design_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""
            You are a technical design document expert for Data Engineering projects. Your task is to create 
            a detailed technical design wiki page based on the requirements and PRD.
            
            You need to:
            1. Extract technical specifications from the requirements
            2. Create data mapping tables with source and destination fields
            3. Document SQL queries needed for implementation
            4. Specify dependencies and technical prerequisites
            5. Detail security and compliance considerations
            
            Output format:
            {
                "design_content": {
                    "title": "Technical Design: [Requirement Name]",
                    "overview": "technical overview",
                    "architecture": "description of the technical architecture",
                    "mapping_tables": [{"attribute": "attr", "type": "type", "source": "src", "destination": "dest"}],
                    "queries": ["SQL query 1", "SQL query 2"],
                    "dependencies": ["dependency1", "dependency2"],
                    "security": ["security consideration 1", "security consideration 2"]
                }
            }
            """),
            HumanMessage(content="{input}"),
        ])
        
        # Create the parser
        self.output_parser = JsonOutputParser()
        
        # Create the chain
        self.design_chain = self.design_prompt | self.llm | self.output_parser
    
    def create_design_document(self, formatted_prd: Dict[str, Any], document_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a technical design document in wiki based on formatted PRD content.
        
        Args:
            formatted_prd: The formatted PRD content
            document_results: Results from document creation agent
            
        Returns:
            Design document creation results as a dictionary
        """
        logger.info("Starting design document creation")
        
        try:
            # Prepare input for LLM
            design_input = {
                "input": {
                    "formatted_prd": formatted_prd,
                    "document_results": document_results
                }
            }
            
            # Generate design content
            design_content = self.design_chain.invoke(design_input)
            
            # Create wiki page if integration is available
            if self.wiki:
                try:
                    wiki_result = self.wiki.create_page(
                        space="DENG",
                        title=design_content["design_content"]["title"],
                        content=design_content["design_content"]
                    )
                    design_content["wiki_page"] = wiki_result
                except Exception as e:
                    logger.error(f"Error creating wiki page: {str(e)}")
                    design_content["wiki_page"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            logger.info("Design document creation complete")
            return design_content
        
        except Exception as e:
            logger.error(f"Error during design document creation: {str(e)}")
            return {
                "error": f"Error during design document creation: {str(e)}",
                "wiki_page": {
                    "success": False,
                    "error": str(e)
                }
            }