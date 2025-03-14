#\!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

load_dotenv()

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.service.server import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(debug=True, host='0.0.0.0', port=port)
