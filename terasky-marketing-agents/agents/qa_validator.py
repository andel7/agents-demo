from typing import Dict, List
import json
from .base_agent import BaseAgent

class QAValidator(BaseAgent):
    def __init__(self, bedrock_client, config):
        super().__init__(bedrock_client, config)
        self.prompt_template = """
You are a TeraSky QA validation expert. Review the generated campaign content and provide a comprehensive quality assessment in JSON format.

Campaign Content: {campaign_content}

Please validate the following aspects and provide your findings in a structured JSON format:

1. Content Accuracy:
   - Technical accuracy
   - Product information
   - Value propositions
   - Claims verification

2. Brand Alignment:
   - Tone consistency
   - Visual identity
   - Messaging alignment
   - Brand guidelines

3. Target Audience Fit:
   - Audience relevance
   - Pain point addressing
   - Value communication
   - Call-to-action effectiveness

4. Compliance & Safety:
   - Legal compliance
   - Industry regulations
   - Data privacy
   - Security considerations

5. Content Quality:
   - Writing quality
   - Visual quality
   - Technical depth
   - Engagement potential

6. Improvement Suggestions:
   - Content improvements
   - Visual improvements
   - Technical improvements
   - Strategic improvements

Format your response as a JSON object with the following structure:
{{
    "content_accuracy": {{
        "technical_accuracy": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "product_information": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "value_propositions": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "claims_verification": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }}
    }},
    "brand_alignment": {{
        "tone_consistency": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "visual_identity": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "messaging_alignment": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "brand_guidelines": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }}
    }},
    "target_audience_fit": {{
        "audience_relevance": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "pain_point_addressing": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "value_communication": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "cta_effectiveness": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }}
    }},
    "compliance_safety": {{
        "legal_compliance": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "industry_regulations": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "data_privacy": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "security_considerations": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }}
    }},
    "content_quality": {{
        "writing_quality": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "visual_quality": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "technical_depth": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }},
        "engagement_potential": {{
            "status": "pass/fail/warning",
            "issues": [],
            "suggestions": []
        }}
    }},
    "improvement_suggestions": {{
        "content_improvements": [],
        "visual_improvements": [],
        "technical_improvements": [],
        "strategic_improvements": []
    }},
    "overall_assessment": {{
        "status": "pass/fail/warning",
        "summary": "",
        "critical_issues": [],
        "recommendations": []
    }}
}}

Focus on ensuring the content meets TeraSky's high standards for technical accuracy, brand consistency, and audience engagement.
"""

    def validate(self, campaign_content: Dict) -> Dict:
        """Validate the campaign content and provide assessment."""
        try:
            self.log_activity("Starting content validation")
            
            # Format the prompt with campaign content
            prompt = self._format_prompt(
                self.prompt_template,
                campaign_content=json.dumps(campaign_content, indent=2)
            )
            
            # Get response from Bedrock
            response = self._invoke_bedrock(prompt)
            
            # Parse and validate the response
            validation_results = self._parse_json_response(response)
            
            # Determine if improvements are needed
            needs_improvement = self._check_improvement_needed(validation_results)
            validation_results['needs_improvement'] = needs_improvement
            
            self.log_activity("Completed content validation")
            return validation_results
            
        except Exception as e:
            return self.handle_error(e, "Content validation")

    def _check_improvement_needed(self, validation_results: Dict) -> bool:
        """Check if any improvements are needed based on validation results."""
        # Check overall assessment
        if validation_results['overall_assessment']['status'] != 'pass':
            return True
        
        # Check critical issues
        if validation_results['overall_assessment']['critical_issues']:
            return True
        
        # Check if any section has failed status
        for section in ['content_accuracy', 'brand_alignment', 'target_audience_fit', 
                       'compliance_safety', 'content_quality']:
            for subsection in validation_results[section].values():
                if subsection['status'] == 'fail':
                    return True
        
        return False

    def process(self, input_data: Dict) -> Dict:
        """Process input data and return validation results."""
        return self.validate(input_data) 