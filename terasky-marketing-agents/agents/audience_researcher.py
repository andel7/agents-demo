from typing import Dict
import json
from .base_agent import BaseAgent

class AudienceResearcher(BaseAgent):
    def __init__(self, bedrock_client, config):
        super().__init__(bedrock_client, config)
        self.prompt_template = """
You are a TeraSky audience research expert. Based on the product research provided, analyze the target audience and market segments in JSON format.

Product Research: {product_research}

Please analyze the following aspects and provide your findings in a structured JSON format:

1. Target Personas:
   - Primary decision makers
   - Technical influencers
   - End users
   - Industry roles

2. Company Profiles:
   - Ideal company size
   - Target industries
   - Geographic focus
   - Technical maturity

3. Pain Points:
   - Primary challenges
   - Current solutions
   - Technical limitations
   - Business impact

4. Decision Process:
   - Buying cycle
   - Key stakeholders
   - Decision criteria
   - Budget considerations

5. Communication Channels:
   - Preferred platforms
   - Content types
   - Engagement methods
   - Technical communities

Format your response as a JSON object with the following structure:
{{
    "target_personas": {{
        "primary_decision_makers": [],
        "technical_influencers": [],
        "end_users": [],
        "industry_roles": []
    }},
    "company_profiles": {{
        "ideal_company_size": [],
        "target_industries": [],
        "geographic_focus": [],
        "technical_maturity": []
    }},
    "pain_points": {{
        "primary_challenges": [],
        "current_solutions": [],
        "technical_limitations": [],
        "business_impact": []
    }},
    "decision_process": {{
        "buying_cycle": [],
        "key_stakeholders": [],
        "decision_criteria": [],
        "budget_considerations": []
    }},
    "communication_channels": {{
        "preferred_platforms": [],
        "content_types": [],
        "engagement_methods": [],
        "technical_communities": []
    }}
}}

Focus on how TeraSky's consulting and implementation services can address the identified needs.
"""

    def research(self, product_research: Dict) -> Dict:
        """Research the target audience based on product information."""
        try:
            self.log_activity("Starting audience research")
            
            # Format the prompt with product research
            prompt = self._format_prompt(
                self.prompt_template,
                product_research=json.dumps(product_research, indent=2)
            )
            
            # Get response from Bedrock
            response = self._invoke_bedrock(prompt)
            
            # Parse and validate the response
            audience_research = self._parse_json_response(response)
            
            self.log_activity("Completed audience research")
            return audience_research
            
        except Exception as e:
            return self.handle_error(e, "Audience research")

    def process(self, input_data: Dict) -> Dict:
        """Process input data and return audience research results."""
        return self.research(input_data) 