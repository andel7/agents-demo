import os
import json
from typing import Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment variables."""
        try:
            # Try to load from file first
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            
            # Fall back to environment variables
            return {
                'model_id': os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0'),
                'image_model_id': os.getenv('BEDROCK_IMAGE_MODEL_ID', 'stability.stable-diffusion-xl-v1'),
                'max_tokens': int(os.getenv('BEDROCK_MAX_TOKENS', '4096')),
                'temperature': float(os.getenv('BEDROCK_TEMPERATURE', '0.7')),
                'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'terasky_brand': {
                    'primary_color': os.getenv('TERASKY_PRIMARY_COLOR', '#0066CC'),
                    'secondary_color': os.getenv('TERASKY_SECONDARY_COLOR', '#FF9900'),
                    'font_family': os.getenv('TERASKY_FONT_FAMILY', 'Arial, sans-serif'),
                    'logo_path': os.getenv('TERASKY_LOGO_PATH', 'static/terasky-logo.png')
                }
            }
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise

    def _validate_config(self):
        """Validate the configuration values."""
        required_fields = [
            ('bedrock', 'model_id'),
            ('bedrock', 'image_model_id'),
            ('bedrock', 'max_tokens'),
            ('bedrock', 'temperature'),
            ('aws', 'region')
        ]
        
        for section, field in required_fields:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
            if field not in self.config[section]:
                raise ValueError(f"Missing required configuration field: {section}.{field}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self.config[key] = value
        self._save_config()

    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load and return the application configuration."""
    config = Config(config_path)
    return config.config

def get_bedrock_config() -> Dict[str, Any]:
    """Get Bedrock-specific configuration."""
    config = load_config()
    return {
        'model_id': config.get('model_id'),
        'image_model_id': config.get('image_model_id'),
        'max_tokens': config.get('max_tokens'),
        'temperature': config.get('temperature'),
        'aws_region': config.get('aws_region')
    }

def get_brand_config() -> Dict[str, Any]:
    """Get TeraSky brand configuration."""
    config = load_config()
    return config.get('terasky_brand', {}) 