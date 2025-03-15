#\!/usr/bin/env python
from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime

# Create a simple Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# In-memory storage for requirements
requirements = {}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Backend is running!'
    }), 200

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        'message': 'API is working!',
        'data': [1, 2, 3, 4, 5]
    }), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'app': 'Product Manager Agent',
        'status': 'Running',
        'endpoints': ['/health', '/api/test', '/api/requirements']
    }), 200

@app.route('/api/requirements', methods=['GET', 'POST'])
def handle_requirements():
    if request.method == 'POST':
        try:
            # Get JSON data from request
            data = request.json
            
            # Generate a unique ID
            req_id = str(uuid.uuid4())
            
            # Create requirement object
            requirement = {
                'id': req_id,
                'title': data.get('businessNeed', 'Untitled Requirement'),
                'description': data.get('requirements', ''),
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'user_id': data.get('user_id', 'anonymous'),
                'business_impact': data.get('businessImpact', ''),
                'delivery_date': data.get('deliveryDate', ''),
                'campaign_date': data.get('campaignDate', ''),
                'steps': [
                    {
                        'name': 'validation',
                        'status': 'pending',
                        'start_time': None,
                        'end_time': None,
                        'details': None,
                        'error': None
                    },
                    {
                        'name': 'design',
                        'status': 'pending',
                        'start_time': None,
                        'end_time': None,
                        'details': None,
                        'error': None
                    },
                    {
                        'name': 'document',
                        'status': 'pending',
                        'start_time': None,
                        'end_time': None,
                        'details': None,
                        'error': None
                    },
                    {
                        'name': 'formatting',
                        'status': 'pending',
                        'start_time': None,
                        'end_time': None,
                        'details': None,
                        'error': None
                    }
                ]
            }
            
            # Store requirement
            requirements[req_id] = requirement
            
            # Return success response
            return jsonify({
                'success': True,
                'message': 'Requirement created successfully',
                'requirement': requirement
            }), 201
        except Exception as e:
            print(f"Error creating requirement: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An error occurred while creating the requirement'
            }), 500
    else:
        # Return all requirements for GET request
        user_id = request.args.get('user_id')
        if user_id:
            # Filter by user_id if provided
            user_requirements = [req for req in requirements.values() if req['user_id'] == user_id]
            return jsonify({'requirements': user_requirements}), 200
        else:
            # Return all requirements
            return jsonify({'requirements': list(requirements.values())}), 200

@app.route('/api/requirements/<req_id>', methods=['GET'])
def get_requirement(req_id):
    requirement = requirements.get(req_id)
    if requirement:
        return jsonify(requirement), 200
    else:
        return jsonify({'error': 'Requirement not found'}), 404

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    
    # Simple mock authentication that accepts any login
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data.get('username')
    
    # Return a mock token
    return jsonify({
        'token': f"mock-token-{username}-{uuid.uuid4()}",
        'user': {
            'id': str(uuid.uuid4()),
            'username': username,
            'email': f"{username}@example.com",
            'firstName': 'Test',
            'lastName': 'User'
        }
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    
    # Simple mock registration that accepts any registration
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Missing username, email or password'}), 400
    
    username = data.get('username')
    email = data.get('email')
    
    # Return a mock token and user data
    return jsonify({
        'token': f"mock-token-{username}-{uuid.uuid4()}",
        'user': {
            'id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'firstName': data.get('firstName', 'New'),
            'lastName': data.get('lastName', 'User')
        }
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)