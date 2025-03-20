import os
from typing import Dict, List, Any, TypedDict, Optional
import logging
from pydantic import BaseModel, Field

# LangGraph and LangChain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define output schema with Pydantic
class ValidationResult(BaseModel):
    """Schema for validation results."""
    is_valid: bool = Field(description="Whether the requirement is valid")
    missing_fields: List[str] = Field(default_factory=list, description="List of missing required fields")
    unclear_fields: List[str] = Field(default_factory=list, description="List of fields that need more clarity")
    feedback: str = Field(description="Detailed feedback with suggestions for improvement")
    examples: Dict[str, str] = Field(default_factory=dict, description="Examples of good input for unclear fields")

# Define required fields
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
        "min_length": 1,  # At least one contributor
        "required": True,
        "description": "List of contributors to the requirement"
    }
}

# Example inputs for validation feedback
EXAMPLE_INPUTS = {
    "business_need": "We need to track foreign bank account indicators for tax filing customers to enable personalized expert matching for customers with complex tax situations.",
    "requirements": "To hyperpersonalize PY expert match use cases. Post engagement, no action, FS only, should trigger when a customer who auths in, but doesn't take any action like uploading a document OR expert chat OR expert call for over 5 days.",
    "business_impact": "CS will not be able to launch certain aspects of their PY Expert Match campaign without this data. The data will be used for both segmentation and personalization.",
    "delivery_date": "02/28/2025",
    "campaign_date": "03/05/2025",
    "contributors": ["Sarah Johnson", "Data Analytics Team"]
}

class ValidationAgent:
    """
    Validation agent to check requirement submissions for completeness and clarity.
    
    This agent analyzes the fields in a requirement submission, validates them against
    predefined rules, and provides feedback on missing or unclear information.
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo", temperature: float = 0.1):
        """
        Initialize the validation agent with a specific LLM.
        
        Args:
            model_name: The name of the model to use for validation
            temperature: Temperature setting for the model
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        # Create output parser
        self.parser = PydanticOutputParser(pydantic_object=ValidationResult)
        
        # Create the validation prompt
        self.validation_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""
            You are a requirements validation expert for Data Engineering projects. Your task is to 
            analyze the user's requirement submission and determine if it has all necessary information.
            
            Here are the exact required fields and their purpose:
            
            1. business_need: A clear explanation of what the business is asking for and why
            2. requirements: Detailed information about what needs to be built or implemented
            3. business_impact: How this requirement will impact the business if delivered or not delivered
            4. delivery_date: The date when the requirement needs to be completed
            5. campaign_date: The date when the related campaign or product will launch
            6. contributors: The people involved in this requirement
            
            For each field, check if:
            1. It is present (not missing)
            2. It has sufficient detail and clarity
            3. It fulfills its intended purpose
            
            If any required field is missing or lacks sufficient detail, provide specific feedback
            with examples of good input.
            
            Here's an example of a good requirement submission:
            ```
            {EXAMPLE_INPUTS}
            ```
            
            {self.parser.get_format_instructions()}
            """),
            HumanMessage(content="{input}"),
        ])
    
    def preprocess_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess the input before sending to the LLM.
        
        Args:
            raw_input: The raw input from the user
            
        Returns:
            Preprocessed input with basic validation results
        """
        preprocessed = {"input": raw_input}
        
        # Add basic validation results
        missing_fields = []
        unclear_fields = []
        
        for field, rules in REQUIRED_FIELDS.items():
            if rules["required"]:
                # Check if field exists and is not empty
                if field not in raw_input or raw_input[field] is None or raw_input[field] == "":
                    missing_fields.append(field)
                # Check if string field meets minimum length
                elif isinstance(raw_input[field], str) and len(raw_input[field]) < rules["min_length"]:
                    unclear_fields.append(field)
                # Check if list field meets minimum length
                elif isinstance(raw_input[field], list) and len(raw_input[field]) < rules["min_length"]:
                    unclear_fields.append(field)
                
        preprocessed["basic_validation"] = {
            "missing_fields": missing_fields,
            "unclear_fields": unclear_fields
        }
        
        return preprocessed
    
    def validate(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the input using the LLM.
        
        Args:
            raw_input: The raw input from the user
            
        Returns:
            Validation results
        """
        logger.info("Starting validation of requirement submission")
        
        try:
            # Preprocess the input
            preprocessed = self.preprocess_input(raw_input)
            
            # Basic validation first - if fields are simply missing, don't need LLM
            basic_validation = preprocessed["basic_validation"]
            if basic_validation["missing_fields"]:
                logger.info(f"Basic validation failed - missing fields: {basic_validation['missing_fields']}")
                
                # Create a simplified result without calling LLM
                missing_field_descriptions = [
                    f"{field}: {REQUIRED_FIELDS[field]['description']}" 
                    for field in basic_validation["missing_fields"] 
                    if field in REQUIRED_FIELDS
                ]
                
                examples = {}
                for field in basic_validation["missing_fields"]:
                    if field in EXAMPLE_INPUTS:
                        examples[field] = EXAMPLE_INPUTS[field]
                
                return ValidationResult(
                    is_valid=False,
                    missing_fields=basic_validation["missing_fields"],
                    unclear_fields=[],
                    feedback=f"The submission is missing required fields: {', '.join(missing_field_descriptions)}",
                    examples=examples
                ).model_dump()
            
            # If basic fields are present, use LLM for deeper validation
            logger.info("Basic validation passed, proceeding to LLM validation")
            
            # Convert input to string representation for LLM
            input_str = str(raw_input)
            
            # Run the validation chain
            result = self.llm.invoke(
                self.validation_prompt.format(input=input_str)
            )
            
            # Parse the result
            validation_results = self.parser.parse(result.content)
            validation_dict = validation_results.model_dump()
            
            # Log the results
            logger.info(f"Validation complete. Valid: {validation_dict['is_valid']}")
            if not validation_dict["is_valid"]:
                logger.info(f"Missing fields: {validation_dict.get('missing_fields', [])}")
                logger.info(f"Unclear fields: {validation_dict.get('unclear_fields', [])}")
            
            return validation_dict
        
        except Exception as e:
            logger.error(f"Error during validation: {str(e)}")
            # Return a fallback validation result
            return ValidationResult(
                is_valid=False,
                missing_fields=["Error occurred during validation"],
                unclear_fields=[],
                feedback=f"An error occurred during validation: {str(e)}. Please try again or contact support.",
                examples={}
            ).model_dump()

# Example usage
if __name__ == "__main__":
    validator = ValidationAgent()
    
    # Test with complete input
    test_input = {
        "business_need": "We need to track foreign bank account indicators for tax filing customers to enable personalized expert matching for customers with complex tax situations.",
        "requirements": "To hyperpersonalize PY expert match use cases. Post engagement, no action, FS only, should trigger when a customer who auths in, but doesn't take any action like uploading a document OR expert chat OR expert call for over 5 days.",
        "business_impact": "CS will not be able to launch certain aspects of their PY Expert Match campaign without this data. The data will be used for both segmentation and personalization.",
        "delivery_date": "02/28/2025",
        "campaign_date": "03/05/2025",
        "contributors": ["Sarah Johnson", "Data Analytics Team"]
    }
    
    result = validator.validate(test_input)
    print("Validation result:", result)
    
    # Test with incomplete input
    incomplete_input = {
        "business_need": "Track accounts",
        "requirements": "",
        "business_impact": "",
        "delivery_date": "",
        "campaign_date": "",
        "contributors": []
    }
    
    result = validator.validate(incomplete_input)
    print("Validation result for incomplete input:", result)