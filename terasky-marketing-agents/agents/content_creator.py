from typing import Dict, List
import json
from .base_agent import BaseAgent

class ContentCreator(BaseAgent):
    def __init__(self, bedrock_client, config):
        super().__init__(bedrock_client, config)
        self.prompt_template = """
You are a TeraSky content creation expert. Based on the provided product research, audience analysis, and campaign strategy, create compelling marketing content in JSON format.

Product Research: {product_research}
Audience Research: {audience_research}
Campaign Strategy: {campaign_strategy}

Please create the following content types in a structured JSON format:

1. Social Media Content:
   - LinkedIn posts
   - Twitter posts
   - Facebook posts
   - Instagram captions

2. Email Marketing:
   - Newsletter content
   - Drip campaign emails
   - Event invitations
   - Product updates

3. Blog Content:
   - Featured article
   - Technical deep-dive
   - Case study outline
   - How-to guide

4. Ad Copy:
   - Google Ads
   - LinkedIn Ads
   - Display ads
   - Retargeting ads

5. Landing Page:
   - Hero section
   - Feature highlights
   - Call-to-action
   - Social proof

Format your response as a JSON object with the following structure:
{{
    "social_media": {{
        "linkedin_posts": [],
        "twitter_posts": [],
        "facebook_posts": [],
        "instagram_captions": []
    }},
    "email_marketing": {{
        "newsletter_content": [],
        "drip_campaign_emails": [],
        "event_invitations": [],
        "product_updates": []
    }},
    "blog_content": {{
        "featured_article": [],
        "technical_deep_dive": [],
        "case_study_outline": [],
        "how_to_guide": []
    }},
    "ad_copy": {{
        "google_ads": [],
        "linkedin_ads": [],
        "display_ads": [],
        "retargeting_ads": []
    }},
    "landing_page": {{
        "hero_section": [],
        "feature_highlights": [],
        "call_to_action": [],
        "social_proof": []
    }}
}}

For each content piece, include:
- Main message
- Target audience
- Key benefits
- Call to action
- Tone and style
- Keywords

Focus on maintaining TeraSky's professional and technical brand voice while addressing the target audience's needs.
"""

    def create_content(self, product_research: Dict, audience_research: Dict, campaign_strategy: Dict) -> Dict:
        """Create marketing content based on research and strategy."""
        try:
            self.log_activity("Starting content creation")
            
            # Format the prompt with research and strategy data
            prompt = self._format_prompt(
                self.prompt_template,
                product_research=json.dumps(product_research, indent=2),
                audience_research=json.dumps(audience_research, indent=2),
                campaign_strategy=json.dumps(campaign_strategy, indent=2)
            )
            
            # Get response from Bedrock
            response = self._invoke_bedrock(prompt)
            
            # Parse and validate the response
            content = self._parse_json_response(response)
            
            self.log_activity("Completed content creation")
            return content
            
        except Exception as e:
            return self.handle_error(e, "Content creation")

    def improve_content(self, content: Dict, improvements: List[str]) -> Dict:
        """Improve existing content based on QA feedback."""
        try:
            self.log_activity("Starting content improvement")
            
            improvement_prompt = f"""
Based on the following feedback, improve the marketing content:

Content: {json.dumps(content, indent=2)}
Improvements Needed: {json.dumps(improvements, indent=2)}

Please provide improved versions of the content while maintaining the same structure.
Focus on addressing the specific improvement points while preserving the original intent and brand voice.
"""
            
            # Get response from Bedrock
            response = self._invoke_bedrock(improvement_prompt)
            
            # Parse and validate the response
            improved_content = self._parse_json_response(response)
            
            self.log_activity("Completed content improvement")
            return improved_content
            
        except Exception as e:
            return self.handle_error(e, "Content improvement")

    def process(self, input_data: Dict) -> Dict:
        """Process input data and return created content."""
        return self.create_content(
            input_data.get('product_research', {}),
            input_data.get('audience_research', {}),
            input_data.get('campaign_strategy', {})
        ) 