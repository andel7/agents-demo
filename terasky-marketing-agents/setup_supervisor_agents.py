#!/usr/bin/env python3
"""
Setup and Run Script for TeraSky Marketing Campaign Generator with Supervisor Agent
This script sets up the environment and runs the supervisor-based campaign generator.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        logger.info("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        logger.info("Virtual environment created")
    else:
        logger.info("Virtual environment already exists")
    
    return venv_path

def get_pip_command(venv_path):
    """Get the pip command for the virtual environment."""
    if os.name == 'nt':  # Windows
        return str(venv_path / "Scripts" / "pip")
    else:  # Unix/Linux/macOS
        return str(venv_path / "bin" / "pip")

def get_python_command(venv_path):
    """Get the python command for the virtual environment."""
    if os.name == 'nt':  # Windows
        return str(venv_path / "Scripts" / "python")
    else:  # Unix/Linux/macOS
        return str(venv_path / "bin" / "python")

def install_requirements(venv_path):
    """Install required packages."""
    pip_cmd = get_pip_command(venv_path)
    
    logger.info("Installing requirements...")
    
    # Core requirements
    requirements = [
        "boto3>=1.34.0",
        "streamlit>=1.28.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0"
    ]
    
    for req in requirements:
        logger.info(f"Installing {req}...")
        subprocess.run([pip_cmd, "install", req], check=True)
    
    logger.info("All requirements installed successfully")

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            logger.error("AWS credentials not found. Please configure AWS CLI or set environment variables.")
            logger.info("Run: aws configure")
            return False
        
        # Test credentials by making a simple call
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"AWS Account ID: {identity['Account']}")
        logger.info(f"AWS User/Role: {identity['Arn']}")
        return True
        
    except Exception as e:
        logger.error(f"Error checking AWS credentials: {str(e)}")
        return False

def check_bedrock_permissions():
    """Check if the user has necessary Bedrock permissions."""
    try:
        import boto3
        session = boto3.Session()
        bedrock = session.client('bedrock')
        
        # Try to list foundation models
        response = bedrock.list_foundation_models()
        logger.info(f"Found {len(response['modelSummaries'])} foundation models")
        
        # Check for Claude models
        claude_models = [model for model in response['modelSummaries'] 
                        if 'claude' in model['modelId'].lower()]
        if claude_models:
            logger.info(f"Found {len(claude_models)} Claude models available")
        else:
            logger.warning("No Claude models found - may need to enable model access")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking Bedrock permissions: {str(e)}")
        logger.info("Please ensure you have Bedrock permissions and model access enabled")
        return False

def run_command_line_version(venv_path, args):
    """Run the command-line version of the supervisor agent."""
    python_cmd = get_python_command(venv_path)
    
    cmd = [
        python_cmd, 
        "supervisor_bedrock_agents.py",
        "--product_key", args.product_key,
        "--recreate_agents", args.recreate_agents,
        "--clean_up", args.clean_up,
        "--enable_trace", args.enable_trace,
        "--trace_level", args.trace_level
    ]
    
    if args.clean_up_after:
        cmd.extend(["--clean_up_after", args.clean_up_after])
    
    logger.info(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def run_streamlit_version(venv_path):
    """Run the Streamlit version of the supervisor agent."""
    python_cmd = get_python_command(venv_path)
    
    cmd = [python_cmd, "-m", "streamlit", "run", "streamlit_supervisor_agents.py"]
    
    logger.info("Starting Streamlit application...")
    logger.info("The application will open in your default web browser")
    logger.info("Press Ctrl+C to stop the application")
    
    subprocess.run(cmd, check=True)

def main():
    """Main setup and run function."""
    parser = argparse.ArgumentParser(description="Setup and run TeraSky Marketing Campaign Generator with Supervisor Agent")
    parser.add_argument("--mode", type=str, default="streamlit", 
                       choices=["streamlit", "cli"],
                       help="Run mode: streamlit (web UI) or cli (command line)")
    parser.add_argument("--skip_setup", action="store_true",
                       help="Skip environment setup")
    
    # CLI-specific arguments
    parser.add_argument("--product_key", type=str, default="cloud_migration",
                       choices=["cloud_migration", "data_analytics", "cybersecurity", "devops", "ai_ml"],
                       help="Product key for campaign generation (CLI mode only)")
    parser.add_argument("--recreate_agents", type=str, default="false", 
                       choices=["true", "false"],
                       help="Whether to recreate agents (CLI mode only)")
    parser.add_argument("--clean_up", type=str, default="false",
                       choices=["true", "false"], 
                       help="Clean up agents and exit (CLI mode only)")
    parser.add_argument("--clean_up_after", type=str, default="false",
                       choices=["true", "false"],
                       help="Clean up agents after generation (CLI mode only)")
    parser.add_argument("--enable_trace", type=str, default="true",
                       choices=["true", "false"],
                       help="Enable tracing (CLI mode only)")
    parser.add_argument("--trace_level", type=str, default="core",
                       choices=["core", "full"],
                       help="Trace level (CLI mode only)")
    
    args = parser.parse_args()
    
    logger.info("TeraSky Marketing Campaign Generator - Supervisor Agent Setup")
    logger.info("=" * 70)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    if not args.skip_setup:
        # Setup virtual environment
        venv_path = setup_virtual_environment()
        
        # Install requirements
        install_requirements(venv_path)
        
        # Check AWS credentials
        if not check_aws_credentials():
            logger.error("AWS credentials check failed. Please configure AWS credentials.")
            return 1
        
        # Check Bedrock permissions
        if not check_bedrock_permissions():
            logger.warning("Bedrock permissions check failed. You may encounter issues.")
    else:
        venv_path = Path("venv")
        if not venv_path.exists():
            logger.error("Virtual environment not found. Run without --skip_setup first.")
            return 1
    
    logger.info("Setup completed successfully!")
    logger.info("=" * 70)
    
    try:
        if args.mode == "streamlit":
            logger.info("Starting Streamlit application with Supervisor Agent...")
            run_streamlit_version(venv_path)
        else:
            logger.info("Running command-line version with Supervisor Agent...")
            run_command_line_version(venv_path, args)
            
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Error running application: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 