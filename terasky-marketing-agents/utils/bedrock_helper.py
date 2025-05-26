import boto3
import json
from typing import Dict, Any, Optional
import logging
from .config import get_bedrock_config

logger = logging.getLogger(__name__)

class BedrockHelper:
    def __init__(self):
        self.config = get_bedrock_config()
        self.client = self._initialize_client()

    def _initialize_client(self) -> boto3.client:
        """Initialize the Bedrock client."""
        try:
            return boto3.client(
                'bedrock-runtime',
                region_name=self.config['aws_region']
            )
        except Exception as e:
            logger.error(f"Error initializing Bedrock client: {str(e)}")
            raise

    def invoke_model(self, prompt: str, model_id: Optional[str] = None) -> str:
        """Invoke a Bedrock model with the given prompt."""
        try:
            model_id = model_id or self.config['model_id']
            
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens_to_sample": self.config['max_tokens'],
                    "temperature": self.config['temperature'],
                    "top_p": 1,
                    "stop_sequences": ["\n\nHuman:"]
                })
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('completion', '')
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {str(e)}")
            raise

    def generate_image(self, prompt: str, width: int, height: int) -> str:
        """Generate an image using Bedrock's image generation model."""
        try:
            request_body = {
                "textToImageParams": {
                    "text": prompt,
                    "numberOfImages": 1,
                    "width": width,
                    "height": height,
                    "cfgScale": 7.5,
                    "seed": 0,
                    "quality": "standard",
                    "stylePreset": "photographic"
                }
            }
            
            response = self.client.invoke_model(
                modelId=self.config['image_model_id'],
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('images', [{}])[0].get('base64', '')
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from the model."""
        try:
            # Find JSON content between triple backticks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            raise

    def format_prompt(self, template: str, **kwargs) -> str:
        """Format prompt template with given parameters."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            raise

def get_bedrock_helper() -> BedrockHelper:
    """Get a BedrockHelper instance."""
    return BedrockHelper() 