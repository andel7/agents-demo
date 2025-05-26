from typing import Dict, List, Optional
import json
import logging
from datetime import datetime
import boto3
from .product_researcher import ProductResearcher
from .audience_researcher import AudienceResearcher
from .campaign_strategist import CampaignStrategist
from .content_creator import ContentCreator
from .image_generator import ImageGenerator
from .qa_validator import QAValidator

logger = logging.getLogger(__name__)

class CampaignSupervisor:
    def __init__(self, product_info: Dict, bedrock_client: boto3.client, config: Dict):
        self.product_info = product_info
        self.bedrock_client = bedrock_client
        self.config = config
        self.agents = {}
        self.initialize_agents()

    def initialize_agents(self):
        """Initialize all specialized agents."""
        self.agents = {
            'product_researcher': ProductResearcher(
                bedrock_client=self.bedrock_client,
                config=self.config
            ),
            'audience_researcher': AudienceResearcher(
                bedrock_client=self.bedrock_client,
                config=self.config
            ),
            'campaign_strategist': CampaignStrategist(
                bedrock_client=self.bedrock_client,
                config=self.config
            ),
            'content_creator': ContentCreator(
                bedrock_client=self.bedrock_client,
                config=self.config
            ),
            'image_generator': ImageGenerator(
                bedrock_client=self.bedrock_client,
                config=self.config
            ),
            'qa_validator': QAValidator(
                bedrock_client=self.bedrock_client,
                config=self.config
            )
        }

    def generate_campaign(self) -> Dict:
        """Orchestrate the campaign generation process."""
        campaign_data = {
            'product': self.product_info,
            'timestamp': datetime.now().isoformat(),
            'strategy': {},
            'audience': {},
            'content': {},
            'images': []
        }

        try:
            # Step 1: Product Research
            logger.info("Starting product research...")
            product_research = self.agents['product_researcher'].research(self.product_info)
            campaign_data['product_research'] = product_research

            # Step 2: Audience Research
            logger.info("Starting audience research...")
            audience_research = self.agents['audience_researcher'].research(
                product_research
            )
            campaign_data['audience'] = audience_research

            # Step 3: Campaign Strategy
            logger.info("Developing campaign strategy...")
            strategy = self.agents['campaign_strategist'].develop_strategy(
                product_research,
                audience_research
            )
            campaign_data['strategy'] = strategy

            # Step 4: Content Creation
            logger.info("Creating campaign content...")
            content = self.agents['content_creator'].create_content(
                product_research,
                audience_research,
                strategy
            )
            campaign_data['content'] = content

            # Step 5: Image Generation
            logger.info("Generating campaign images...")
            images = self.agents['image_generator'].generate_images(
                product_research,
                content
            )
            campaign_data['images'] = images

            # Step 6: Quality Assurance
            logger.info("Performing quality assurance...")
            qa_results = self.agents['qa_validator'].validate(
                campaign_data
            )
            campaign_data['qa_results'] = qa_results

            # Apply QA improvements if needed
            if qa_results.get('needs_improvement', False):
                logger.info("Applying QA improvements...")
                self._apply_qa_improvements(campaign_data, qa_results)

            return campaign_data

        except Exception as e:
            logger.error(f"Error in campaign generation: {str(e)}")
            raise

    def _apply_qa_improvements(self, campaign_data: Dict, qa_results: Dict):
        """Apply improvements suggested by the QA validator."""
        if qa_results.get('content_improvements'):
            improved_content = self.agents['content_creator'].improve_content(
                campaign_data['content'],
                qa_results['content_improvements']
            )
            campaign_data['content'] = improved_content

        if qa_results.get('image_improvements'):
            improved_images = self.agents['image_generator'].improve_images(
                campaign_data['images'],
                qa_results['image_improvements']
            )
            campaign_data['images'] = improved_images

    def get_agent_status(self, agent_name: str) -> Dict:
        """Get the current status of a specific agent."""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return {
            'name': agent_name,
            'status': 'ready',
            'last_activity': datetime.now().isoformat()
        }

    def get_all_agent_statuses(self) -> Dict[str, Dict]:
        """Get the status of all agents."""
        return {
            name: self.get_agent_status(name)
            for name in self.agents.keys()
        } 