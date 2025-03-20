# test_validation.py
import json
from agents.validation_agent import ValidationAgent

def run_test(validator, input_data, test_name):
    """Run a test and print formatted results"""
    print(f"\n===== TEST: {test_name} =====")
    print(f"Input: {json.dumps(input_data, indent=2)}")
    
    result = validator.validate(input_data)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result["is_valid"]:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")
        if result.get("missing_fields"):
            print(f"Missing fields: {result['missing_fields']}")
        if result.get("unclear_fields"):
            print(f"Unclear fields: {result['unclear_fields']}")
        print(f"Feedback: {result['feedback']}")

def main():
    """Main test function"""
    # Initialize the validation agent
    validator = ValidationAgent()
    
    # Test 1: Complete and valid input
    complete_input = {
        "business_need": "We need to track foreign bank account indicators for tax filing customers to enable personalized expert matching for customers with complex tax situations.",
        "requirements": "To hyperpersonalize PY expert match use cases. Post engagement, no action, FS only, should trigger when a customer who auths in, but doesn't take any action like uploading a document OR expert chat OR expert call for over 5 days.",
        "business_impact": "CS will not be able to launch certain aspects of their PY Expert Match campaign without this data. The data will be used for both segmentation and personalization.",
        "delivery_date": "02/28/2025",
        "campaign_date": "03/05/2025",
        "contributors": ["Sarah Johnson", "Data Analytics Team"]
    }
    run_test(validator, complete_input, "Complete Input")
    
    # Test 2: Missing fields
    missing_fields_input = {
        "business_need": "We need to track foreign bank accounts",
        "requirements": "To personalize expert matching",
        "business_impact": "",
        "delivery_date": "",
        "campaign_date": "",
        "contributors": []
    }
    run_test(validator, missing_fields_input, "Missing Fields")
    
    # Test 3: Unclear but present fields
    unclear_fields_input = {
        "business_need": "Track accounts",
        "requirements": "Match experts",
        "business_impact": "Important for business",
        "delivery_date": "Soon",
        "campaign_date": "Later",
        "contributors": ["Someone"]
    }
    run_test(validator, unclear_fields_input, "Unclear Fields")
    
    # Test 4: The real user input example you provided
    user_example = {
        "business_need": "WE need to track foreign bank account indicators for tax filling customers to enable personalized expert matching for customers with complex tax situations.",
        "requirements": "To hyperpersonalized PY expert match use case. Post engagement, no action, FS only, should trigger when a customer who auths in, but doesn't take any action like uploading a document OR expert chat OR expert call for over 5 days",
        "business_impact": "CS will not be able to launch certain aspects of their PY Expert Match campaign without this data. The data will be used for both segmentation and personalization",
        "delivery_date": "02/28/2025",
        "campaign_date": "03/05/2025",
        "contributors": "Charles Mbugua, Data team"
    }
    run_test(validator, user_example, "User Example")
    
    # Test 5: Fixed user example (contributors as list)
    fixed_user_example = {
        "business_need": "WE need to track foreign bank account indicators for tax filling customers to enable personalized expert matching for customers with complex tax situations.",
        "requirements": "To hyperpersonalized PY expert match use case. Post engagement, no action, FS only, should trigger when a customer who auths in, but doesn't take any action like uploading a document OR expert chat OR expert call for over 5 days",
        "business_impact": "CS will not be able to launch certain aspects of their PY Expert Match campaign without this data. The data will be used for both segmentation and personalization",
        "delivery_date": "02/28/2025",
        "campaign_date": "03/05/2025",
        "contributors": ["Charles Mbugua", "Data team"]
    }
    run_test(validator, fixed_user_example, "Fixed User Example")

if __name__ == "__main__":
    main()