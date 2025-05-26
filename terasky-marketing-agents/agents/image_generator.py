from typing import Dict, List
import json
import base64
from .base_agent import BaseAgent

class ImageGenerator(BaseAgent):
    def __init__(self, bedrock_client, config):
        super().__init__(bedrock_client, config)
        # Get bedrock config from the bedrock section
        bedrock_config = config.get('bedrock', config)
        self.image_model_id = bedrock_config.get('image_model_id', 'stability.stable-diffusion-xl-v1')
        self.prompt_template = """
You are a TeraSky image generation expert. Based on the provided product research and content, create detailed image generation prompts in JSON format.

Product Research: {product_research}
Content: {content}

Please create image generation prompts for the following types of visuals:

1. Social Media Graphics:
   - LinkedIn header
   - Twitter card
   - Facebook cover
   - Instagram post

2. Blog Graphics:
   - Featured image
   - Technical diagram
   - Infographic
   - Process flow

3. Ad Graphics:
   - Display ad
   - Social media ad
   - Retargeting ad
   - Banner ad

4. Landing Page Graphics:
   - Hero image
   - Feature illustration
   - Testimonial background
   - CTA background

Format your response as a JSON object with the following structure:
{{
    "social_media": {{
        "linkedin_header": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x627",
            "description": ""
        }},
        "twitter_card": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x600",
            "description": ""
        }},
        "facebook_cover": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "820x312",
            "description": ""
        }},
        "instagram_post": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1080x1080",
            "description": ""
        }}
    }},
    "blog_graphics": {{
        "featured_image": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x630",
            "description": ""
        }},
        "technical_diagram": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "800x600",
            "description": ""
        }},
        "infographic": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x1800",
            "description": ""
        }},
        "process_flow": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x800",
            "description": ""
        }}
    }},
    "ad_graphics": {{
        "display_ad": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "728x90",
            "description": ""
        }},
        "social_media_ad": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x628",
            "description": ""
        }},
        "retargeting_ad": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "300x250",
            "description": ""
        }},
        "banner_ad": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "970x250",
            "description": ""
        }}
    }},
    "landing_page": {{
        "hero_image": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1920x1080",
            "description": ""
        }},
        "feature_illustration": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "800x600",
            "description": ""
        }},
        "testimonial_background": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x400",
            "description": ""
        }},
        "cta_background": {{
            "prompt": "",
            "style": "",
            "aspect_ratio": "1200x400",
            "description": ""
        }}
    }}
}}

For each image prompt, include:
- Detailed visual description
- Style guidelines
- Color scheme
- Key elements to include
- Brand consistency notes

Focus on creating professional, technical, and modern visuals that align with TeraSky's brand identity.
"""

    def generate_images(self, product_research: Dict, content: Dict) -> List[Dict]:
        """Generate images based on product research and content."""
        try:
            self.log_activity("Starting image generation")
            
            # Get image generation prompts
            prompt = self._format_prompt(
                self.prompt_template,
                product_research=json.dumps(product_research, indent=2),
                content=json.dumps(content, indent=2)
            )
            
            # Get response from Bedrock
            response = self._invoke_bedrock(prompt)
            
            # Parse and validate the response
            image_prompts = self._parse_json_response(response)
            
            # Generate images for each prompt
            generated_images = []
            for category, images in image_prompts.items():
                for image_type, details in images.items():
                    try:
                        # Generate image using Bedrock
                        image_data = self._generate_image(
                            details['prompt'],
                            details['aspect_ratio']
                        )
                        
                        generated_images.append({
                            'category': category,
                            'type': image_type,
                            'prompt': details['prompt'],
                            'description': details['description'],
                            'aspect_ratio': details['aspect_ratio'],
                            'image_data': image_data
                        })
                        
                    except Exception as e:
                        self.log_activity(f"Error generating {image_type}: {str(e)}", "error")
            
            self.log_activity("Completed image generation")
            return generated_images
            
        except Exception as e:
            return self.handle_error(e, "Image generation")

    def _generate_image(self, prompt: str, aspect_ratio: str) -> str:
        """Generate a single image using Bedrock's image generation model."""
        try:
            # Parse aspect ratio
            width, height = map(int, aspect_ratio.split('x'))
            
            # Prepare request body for Stable Diffusion
            request_body = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": 7.5,
                "steps": 50,
                "seed": 0,
                "width": width,
                "height": height,
                "style_preset": "photographic"
            }
            
            # Call Bedrock image generation
            response = self.bedrock_client.invoke_model(
                modelId=self.image_model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            image_data = response_body.get('artifacts', [{}])[0].get('base64', '')
            
            return image_data
            
        except Exception as e:
            self.log_activity(f"Error in image generation: {str(e)}", "error")
            raise

    def improve_images(self, images: List[Dict], improvements: List[str]) -> List[Dict]:
        """Improve existing images based on QA feedback."""
        try:
            self.log_activity("Starting image improvement")
            
            improved_images = []
            for image in images:
                try:
                    # Generate improved prompt
                    improvement_prompt = f"""
Based on the following feedback, improve the image generation prompt:

Original Prompt: {image['prompt']}
Improvements Needed: {json.dumps(improvements, indent=2)}

Please provide an improved prompt that addresses the feedback while maintaining the original intent.
"""
                    
                    # Get improved prompt from Bedrock
                    response = self._invoke_bedrock(improvement_prompt)
                    improved_prompt = response.strip()
                    
                    # Generate new image with improved prompt
                    improved_image_data = self._generate_image(
                        improved_prompt,
                        image['aspect_ratio']
                    )
                    
                    improved_images.append({
                        **image,
                        'prompt': improved_prompt,
                        'image_data': improved_image_data,
                        'improved': True
                    })
                    
                except Exception as e:
                    self.log_activity(f"Error improving image: {str(e)}", "error")
                    improved_images.append(image)
            
            self.log_activity("Completed image improvement")
            return improved_images
            
        except Exception as e:
            return self.handle_error(e, "Image improvement")

    def process(self, input_data: Dict) -> List[Dict]:
        """Process input data and return generated images."""
        return self.generate_images(
            input_data.get('product_research', {}),
            input_data.get('content', {})
        ) 