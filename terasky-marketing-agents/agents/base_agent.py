from typing import Dict, Any, Optional
import json
import logging
import boto3
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, bedrock_client: boto3.client, config: Dict):
        self.bedrock_client = bedrock_client
        self.config = config
        # Get bedrock config from the bedrock section
        bedrock_config = config.get('bedrock', config)
        self.model_id = bedrock_config.get('model_id', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')
        self.max_tokens = bedrock_config.get('max_tokens', 4096)
        self.temperature = bedrock_config.get('temperature', 0.7)
        
        # Debug logging
        logger.info(f"Agent {self.__class__.__name__} initialized with model_id: {self.model_id}")
        logger.info(f"Full config: {config}")

    def _invoke_bedrock(self, prompt: str) -> str:
        """Invoke Bedrock model with the given prompt."""
        try:
            logger.info(f"Invoking Bedrock with model: {self.model_id}")
            
            # Format the request body according to Claude 3 specifications
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('content', [{}])[0].get('text', '')
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock with model {self.model_id}: {str(e)}")
            raise

    def _parse_json_response(self, response: str) -> Dict:
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
            logger.error(f"Raw response content: {response[:500]}...")
            # Return a default error structure instead of raising
            return {
                "error": True,
                "message": f"Failed to parse JSON response: {str(e)}",
                "raw_response": response[:200] + "..." if len(response) > 200 else response
            }

    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format prompt template with given parameters."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            raise

    @abstractmethod
    def process(self, input_data: Dict) -> Dict:
        """Process input data and return results."""
        pass

    def log_activity(self, message: str, level: str = "info"):
        """Log agent activity."""
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"[{self.__class__.__name__}] {message}")

    def validate_input(self, input_data: Dict, required_fields: list) -> bool:
        """Validate input data contains required fields."""
        return all(field in input_data for field in required_fields)

    def handle_error(self, error: Exception, context: str = "") -> Dict:
        """Handle errors and return appropriate response."""
        error_message = f"Error in {self.__class__.__name__}: {str(error)}"
        if context:
            error_message = f"{context} - {error_message}"
        
        logger.error(error_message)
        return {
            "error": True,
            "message": error_message,
            "context": context
        } 