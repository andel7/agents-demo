from typing import Dict
import json
from .base_agent import BaseAgent

class CampaignStrategist(BaseAgent):
    def __init__(self, bedrock_client, config):
        super().__init__(bedrock_client, config)
        self.prompt_template = """
You are a TeraSky campaign strategy expert. Based on the product research and audience analysis provided, develop a comprehensive marketing campaign strategy in JSON format.

Product Research: {product_research}
Audience Research: {audience_research}

Please develop a campaign strategy covering the following aspects in a structured JSON format:

1. Campaign Objectives:
   - Primary goals
   - Success metrics
   - Timeline
   - Budget allocation

2. Channel Strategy:
   - Primary channels
   - Secondary channels
   - Content mix
   - Channel-specific tactics

3. Content Strategy:
   - Key messages
   - Content types
   - Tone and style
   - Brand guidelines

4. Targeting Strategy:
   - Audience segments
   - Geographic focus
   - Industry focus
   - Behavioral targeting

5. Campaign Timeline:
   - Phase 1 (Awareness)
   - Phase 2 (Consideration)
   - Phase 3 (Decision)
   - Phase 4 (Advocacy)

6. Budget Allocation:
   - Channel budget
   - Content creation
   - Paid media
   - Tools and platforms

Format your response as a JSON object with the following structure:
{{
    "campaign_objectives": {{
        "primary_goals": [],
        "success_metrics": [],
        "timeline": [],
        "budget_allocation": []
    }},
    "channel_strategy": {{
        "primary_channels": [],
        "secondary_channels": [],
        "content_mix": [],
        "channel_specific_tactics": []
    }},
    "content_strategy": {{
        "key_messages": [],
        "content_types": [],
        "tone_and_style": [],
        "brand_guidelines": []
    }},
    "targeting_strategy": {{
        "audience_segments": [],
        "geographic_focus": [],
        "industry_focus": [],
        "behavioral_targeting": []
    }},
    "campaign_timeline": {{
        "phase_1_awareness": [],
        "phase_2_consideration": [],
        "phase_3_decision": [],
        "phase_4_advocacy": []
    }},
    "budget_allocation": {{
        "channel_budget": [],
        "content_creation": [],
        "paid_media": [],
        "tools_and_platforms": []
    }}
}}

Focus on how the strategy aligns with TeraSky's brand and target audience needs.
"""

    def develop_strategy(self, product_research: Dict, audience_research: Dict) -> Dict:
        """Develop campaign strategy based on product and audience research."""
        try:
            self.log_activity("Starting campaign strategy development")
            
            # Format the prompt with research data
            prompt = self._format_prompt(
                self.prompt_template,
                product_research=json.dumps(product_research, indent=2),
                audience_research=json.dumps(audience_research, indent=2)
            )
            
            # Get response from Bedrock
            response = self._invoke_bedrock(prompt)
            
            # Parse and validate the response
            strategy = self._parse_json_response(response)
            
            self.log_activity("Completed campaign strategy development")
            return strategy
            
        except Exception as e:
            return self.handle_error(e, "Campaign strategy development")

    def process(self, input_data: Dict) -> Dict:
        """Process input data and return campaign strategy."""
        return self.develop_strategy(
            input_data.get('product_research', {}),
            input_data.get('audience_research', {})
        ) 