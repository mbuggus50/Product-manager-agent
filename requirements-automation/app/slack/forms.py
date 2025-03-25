from typing import List, Dict, Any

def get_requirement_form_blocks() -> List[Dict[str, Any]]:
    """
    Get the blocks for the requirement form.
    
    Returns:
        List of block elements for the form
    """
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Create a new requirement*\nPlease fill out the details below to create a new requirement."
            }
        },
        {
            "type": "divider"
        },
        # Business Need
        {
            "type": "input",
            "block_id": "business_need_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "business_need_input",
                "multiline": True,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Describe what the business is asking for and what impact these requirements have on the business."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Business Need"
            }
        },
        # Requirements
        {
            "type": "input",
            "block_id": "requirements_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "requirements_input",
                "multiline": True,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Detailed requirements with who/what/where/when/why information."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Requirements"
            }
        },
        # Business Impact
        {
            "type": "input",
            "block_id": "business_impact_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "business_impact_input",
                "multiline": True,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Describe what the business impact if this is delivered and also add details if not delivered."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Business Impact"
            }
        },
        # Delivery Date
        {
            "type": "input",
            "block_id": "delivery_date_block",
            "element": {
                "type": "datepicker",
                "action_id": "delivery_date_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Delivery Date"
            }
        },
        # Campaign Launch Date
        {
            "type": "input",
            "block_id": "campaign_date_block",
            "element": {
                "type": "datepicker",
                "action_id": "campaign_date_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Campaign Launch Date"
            }
        },
        # Contributors
        {
            "type": "input",
            "block_id": "contributors_block",
            "element": {
                "type": "multi_users_select",
                "action_id": "contributors_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select contributors"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Contributors"
            }
        },
        # Definitions (optional)
        {
            "type": "input",
            "block_id": "definitions_block",
            "optional": True,
            "element": {
                "type": "plain_text_input",
                "action_id": "definitions_input",
                "multiline": True,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Add any attribute definitions (format: attribute: definition, one per line)."
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Attribute Definitions (Optional)"
            }
        }
    ]

def parse_form_submission(view: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the form submission data.
    
    Args:
        view: The view state from Slack
        
    Returns:
        Parsed requirement data
    """
    values = view["state"]["values"]
    
    # Parse basic fields
    requirement_data = {
        "business_need": values["business_need_block"]["business_need_input"]["value"],
        "requirements": values["requirements_block"]["requirements_input"]["value"],
        "business_impact": values["business_impact_block"]["business_impact_input"]["value"],
        "delivery_date": values["delivery_date_block"]["delivery_date_input"]["selected_date"],
        "campaign_date": values["campaign_date_block"]["campaign_date_input"]["selected_date"],
        "contributors": values["contributors_block"]["contributors_input"]["selected_users"],
    }
    
    # Parse definitions if provided
    definitions_text = values["definitions_block"]["definitions_input"]["value"]
    if definitions_text:
        definitions = []
        for line in definitions_text.split("\n"):
            if ":" in line:
                attribute, definition = line.split(":", 1)
                definitions.append({
                    "attribute": attribute.strip(),
                    "definition": definition.strip()
                })
        requirement_data["definitions"] = definitions
    else:
        requirement_data["definitions"] = []
    
    return requirement_data