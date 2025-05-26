from typing import Dict
import json
from .base_agent import BaseAgent

class ProductResearcher(BaseAgent):
    def __init__(self, bedrock_client, config):
        super().__init__(bedrock_client, config)
        self.prompt_template = """
You are a TeraSky product research specialist. Research {product_name} and provide a detailed analysis in JSON format.

Product Description: {product_description}

Please analyze the following aspects and provide your findings in a structured JSON format:

1. Key Features and Capabilities:
   - List the main features
   - Technical specifications
   - Integration capabilities
   - Security features

2. Competitive Advantages:
   - Unique selling points
   - Market differentiators
   - Technical superiority
   - Cost benefits

3. Use Cases:
   - Primary use cases
   - Industry applications
   - Problem-solving scenarios
   - Implementation examples

4. ROI Benefits:
   - Cost savings
   - Efficiency improvements
   - Risk reduction
   - Business value

5. TeraSky Value Add:
   - Implementation expertise
   - Support capabilities
   - Customization options
   - Integration services

Format your response as a JSON object with the following structure:
{{
    "key_features": {{
        "main_features": [],
        "technical_specs": [],
        "integration_capabilities": [],
        "security_features": []
    }},
    "competitive_advantages": {{
        "unique_selling_points": [],
        "market_differentiators": [],
        "technical_superiority": [],
        "cost_benefits": []
    }},
    "use_cases": {{
        "primary_use_cases": [],
        "industry_applications": [],
        "problem_solving_scenarios": [],
        "implementation_examples": []
    }},
    "roi_benefits": {{
        "cost_savings": [],
        "efficiency_improvements": [],
        "risk_reduction": [],
        "business_value": []
    }},
    "terasky_value_add": {{
        "implementation_expertise": [],
        "support_capabilities": [],
        "customization_options": [],
        "integration_services": []
    }}
}}

Focus on how TeraSky's expertise adds value in implementation and support.
"""

    def research(self, product_info: Dict) -> Dict:
        """Research the product and return detailed analysis."""
        try:
            self.log_activity(f"Starting research for {product_info['name']}")
            
            # Format the prompt with product information
            prompt = self._format_prompt(
                self.prompt_template,
                product_name=product_info['name'],
                product_description=product_info['description']
            )
            
            # Get response from Bedrock
            response = self._invoke_bedrock(prompt)
            
            # Parse and validate the response
            research_results = self._parse_json_response(response)
            
            self.log_activity(f"Completed research for {product_info['name']}")
            return research_results
            
        except Exception as e:
            return self.handle_error(e, f"Product research for {product_info['name']}")

    def process(self, input_data: Dict) -> Dict:
        """Process input data and return research results."""
        return self.research(input_data) 