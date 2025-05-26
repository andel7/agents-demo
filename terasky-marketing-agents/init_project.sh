#!/bin/bash

# Create project structure
mkdir -p agents utils aws logs

# Create Python package files
touch agents/__init__.py
touch utils/__init__.py

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up AWS credentials
echo "Setting up AWS credentials..."
aws configure

# Create log directory
mkdir -p logs

# Set permissions
chmod +x aws/deployment-script.sh
chmod +x init_project.sh

# Initialize git repository
git init
git add .
git commit -m "Initial commit"

echo "Project initialization complete!"
echo "To start the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the Streamlit app: streamlit run app.py" 