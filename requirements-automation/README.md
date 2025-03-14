# Requirements Automation System

This system automates the process of creating, validating, and generating product requirements documents using AI.

> **Important Note**: Before running the application, make sure to set PYTHONPATH to include the project root:
> ```
> export PYTHONPATH=/path/to/requirements-automation:$PYTHONPATH
> ```
> This ensures all Python modules can be properly imported.

## Components

### Frontend

The frontend is a React application built with:
- React 18 with TypeScript
- Material UI for components
- React Router for navigation

### Backend

The backend is a Flask API with:
- JWT authentication
- In-memory data storage (for development)
- AI processing capabilities

## Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm 8+

### Installation

1. Install backend dependencies and setup the environment:
```
pip install -r requirements.txt
python init.py  # This installs the package in development mode
```

2. Install frontend dependencies:
```
cd frontend && npm install
```

### Running the Application

For development, use the development script:
```
./run_dev.sh
```

This will start both the frontend and backend servers.

- Frontend: http://localhost:3003
- Backend API: http://localhost:5555/api
- Health check: http://localhost:5555/health

> **Note**: If port 5555 is already in use, you can set a different port using the PORT environment variable:
> ```
> PORT=8000 python run.py
> ```
> Remember to update the proxy configuration in the frontend's `setupProxy.js` file if you change the backend port.

## API Endpoints

### Authentication

- `POST /api/auth/login`: Login with username and password
- `POST /api/auth/register`: Register a new user

### Requirements

- `GET /api/requirements`: Get all requirements for the authenticated user
- `POST /api/requirements`: Create a new requirement
- `GET /api/requirements/:id`: Get a specific requirement
- `GET /api/requirements/:id/status`: Get the status of a requirement
- `POST /api/requirements/:id/generate`: Trigger AI generation for a requirement

### Admin

- `GET /api/admin/requirements`: Get all requirements (admin only)

## Testing

Run the tests:
```
pytest
```

## Demo Accounts

- Admin: username `admin`, password `admin123`
- User: username `user`, password `user123`

## Troubleshooting

### CORS Issues

If you encounter CORS errors:

1. Ensure the backend server is running on port 5555
2. Check if the frontend is correctly proxying requests (using proxy in setupProxy.js)
3. Verify CORS is properly enabled in the backend server
4. Try accessing the backend directly in your browser: http://localhost:5555/health

### 403 Access Denied

If you see a 403 Access Denied:

1. Make sure both servers are running (check the backend logs)
2. Verify the proxy setup is correct in the frontend
3. Try restarting both servers with the run_dev.sh script
4. As a last resort, turn off CORS protection in your browser for local development

### Database/Storage Issues

The current implementation uses in-memory storage for development. All data will be lost when the server restarts.
