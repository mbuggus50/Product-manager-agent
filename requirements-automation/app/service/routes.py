from flask import Blueprint, request, jsonify
import sys
import os

# Ensure app module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.service.auth import token_required, generate_token
from app.models.user import User
import app.service.api as api_service
from app.models.requirement import RequirementStatus
# Fix import for orchestrator - commented out for now as we're not using it yet
# from app.agents.orchastrator import RequirementWorkflow
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
api = Blueprint('api', __name__)


@api.route('/auth/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.json

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    # Verify user
    user = User.authenticate(data['username'], data['password'])
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Generate token
    token = generate_token(user.id, user.username, user.email)

    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'firstName': user.first_name,
            'lastName': user.last_name
        }
    }), 200


@api.route('/auth/register', methods=['POST'])
def register():
    """Register endpoint."""
    data = request.json

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Create user
        user = User.create(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('firstName'),
            last_name=data.get('lastName')
        )

        # Generate token
        token = generate_token(user.id, user.username, user.email)

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'firstName': user.first_name,
                'lastName': user.last_name
            }
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred during registration'}), 500


@api.route('/requirements', methods=['GET'])
@token_required
def get_requirements():
    """Get all requirements for the authenticated user."""
    try:
        # Get user ID from token
        user_id = request.user['user_id']

        # Get requirements
        requirements = api_service.get_requirements_by_user(user_id)

        return jsonify({
            'requirements': [req.to_dict() for req in requirements]
        }), 200
    except Exception as e:
        logger.error(f"Error in get_requirements endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while fetching requirements'}), 500


@api.route('/requirements', methods=['POST'])
@token_required
def create_requirement():
    """Create a new requirement."""
    try:
        # Get request data
        data = request.json

        # Add user info
        data['user_id'] = request.user['user_id']
        data['user_email'] = request.user['email']
        data['source'] = 'web'

        # Create requirement
        requirement = api_service.create_requirement(data)

        # For now, we'll simulate a successful workflow execution
        # In the real implementation, you would use the workflow orchestrator
        # to process the requirement
        
        # Instead of immediately processing it, we'll return success
        # and let a background job handle the processing
        
        return jsonify({
            'success': True,
            'message': 'Requirement created successfully',
            'requirement': requirement.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error in create_requirement endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'An error occurred while creating the requirement'
        }), 500


@api.route('/requirements/<req_id>', methods=['GET'])
@token_required
def get_requirement(req_id):
    """Get a specific requirement."""
    try:
        # Get user ID from token
        user_id = request.user['user_id']

        # Get requirement
        requirement = api_service.get_requirement_by_id(req_id)

        if not requirement:
            return jsonify({'error': 'Requirement not found'}), 404

        # Check if user has access
        if requirement.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        return jsonify(requirement.to_dict()), 200
    except Exception as e:
        logger.error(f"Error in get_requirement endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while fetching the requirement'}), 500


@api.route('/requirements/<req_id>/status', methods=['GET'])
@token_required
def get_requirement_status(req_id):
    """Get the status of a requirement."""
    try:
        # Get user ID from token
        user_id = request.user['user_id']

        # Get requirement
        requirement = api_service.get_requirement_by_id(req_id)

        if not requirement:
            return jsonify({'error': 'Requirement not found'}), 404

        # Check if user has access
        if requirement.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        # Get document links (if available)
        document_links = getattr(requirement, 'document_links', {})

        return jsonify({
            'id': requirement.id,
            'status': requirement.status.value,
            'steps': [
                {
                    'name': step.name,
                    'status': step.status,
                    'start_time': step.start_time.isoformat() if step.start_time else None,
                    'end_time': step.end_time.isoformat() if step.end_time else None,
                    'details': step.details,
                    'error': step.error
                } for step in requirement.steps
            ],
            'links': document_links,
            'created_at': requirement.created_at.isoformat(),
            'updated_at': requirement.updated_at.isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in get_requirement_status endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while fetching the requirement status'}), 500


@api.route('/requirements/<req_id>/generate', methods=['POST'])
@token_required
def generate_requirement(req_id):
    """Trigger AI generation for a requirement."""
    try:
        # Get user ID from token
        user_id = request.user['user_id']

        # Get requirement
        requirement = api_service.get_requirement_by_id(req_id)

        if not requirement:
            return jsonify({'error': 'Requirement not found'}), 404

        # Check if user has access
        if requirement.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
            
        # Update status to processing
        api_service.update_requirement_status(req_id, RequirementStatus.PROCESSING)
        
        # Update validation step to processing
        api_service.update_step_status(req_id, "validation", "processing")
        
        # In a real implementation, this would trigger an async job
        # For now, we'll simulate a successful validation after a delay
        # and update the step status
        
        # This would be handled by a background job in a real implementation
        # We're mocking success for the demo
        api_service.update_step_status(
            req_id, 
            "validation", 
            "completed", 
            details={"score": 0.92, "feedback": "Requirements are well-defined and clear."}
        )
        
        # Update design step to processing
        api_service.update_step_status(req_id, "design", "processing")
        
        # Mock document links
        api_service.add_document_link(req_id, "prd", "https://docs.google.com/document/d/sample-prd")
        api_service.add_document_link(req_id, "jira", "https://jira.example.com/browse/PRD-123")
        
        return jsonify({
            'success': True,
            'message': 'Requirement generation started',
            'requirement': requirement.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error in generate_requirement endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'An error occurred while triggering the generation'
        }), 500


@api.route('/admin/requirements', methods=['GET'])
@token_required
def admin_get_requirements():
    """Admin endpoint to get all requirements."""
    try:
        # Get user ID from token
        user_id = request.user['user_id']
        
        # Simple admin check - in a real app, use proper role-based auth
        user = User.get_by_id(user_id)
        if not user or user.username != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

        # Get all requirements
        requirements = api_service.get_all_requirements()

        return jsonify({
            'requirements': [req.to_dict() for req in requirements]
        }), 200
    except Exception as e:
        logger.error(f"Error in admin_get_requirements endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while fetching requirements'}), 500