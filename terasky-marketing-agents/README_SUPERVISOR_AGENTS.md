# TeraSky Marketing Campaign Generator - Supervisor Agent Implementation

## Overview

This implementation uses the **Marketing Supervisor Agent** to orchestrate a comprehensive marketing campaign generation workflow. Unlike the previous linear approach, this version leverages AWS Bedrock's true supervisor-agent collaboration model for enterprise-grade campaign orchestration.

## 🏗️ Architecture

### Supervisor Agent Model
```
Marketing Supervisor Agent (Orchestrator)
├── Product Researcher (Collaborator)
├── Audience Researcher (Collaborator)
├── Campaign Strategist (Collaborator)
├── Content Creator (Collaborator)
└── QA Validator (Collaborator)
```

### Key Benefits
- **True Agent Collaboration**: Real AWS Bedrock Agents with supervisor orchestration
- **Enterprise Scalability**: Designed for production enterprise workflows
- **Quality Assurance**: Built-in coordination and validation at each step
- **AWS Console Visibility**: All agents visible and manageable in AWS Bedrock console
- **Flexible Task Management**: YAML-driven task definitions with dynamic inputs

## 🚀 Quick Start

### Option 1: Streamlit Web Interface (Recommended)
```bash
# Setup and run Streamlit app
python setup_supervisor_agents.py --mode streamlit

# Or with existing environment
python setup_supervisor_agents.py --mode streamlit --skip_setup
```

### Option 2: Command Line Interface
```bash
# Generate campaign for cloud migration
python setup_supervisor_agents.py --mode cli --product_key cloud_migration

# With custom options
python setup_supervisor_agents.py --mode cli \
  --product_key data_analytics \
  --recreate_agents true \
  --enable_trace true \
  --trace_level full
```

### Option 3: Direct Execution
```bash
# Run Streamlit directly
python streamlit_supervisor_agents.py

# Run CLI directly
python supervisor_bedrock_agents.py --product_key cybersecurity
```

## 📋 Prerequisites

### AWS Requirements
- AWS CLI configured with appropriate credentials
- AWS Bedrock service access enabled
- Claude 3.5 Sonnet model access enabled in Bedrock
- IAM permissions for Bedrock Agents service

### System Requirements
- Python 3.8 or higher
- 4GB+ RAM (for agent orchestration)
- Internet connection for AWS API calls

### Required IAM Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:*",
                "bedrock-agent:*",
                "bedrock-agent-runtime:*",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "lambda:CreateFunction",
                "lambda:InvokeFunction"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🎯 Available Products

| Product Key | Name | Description |
|-------------|------|-------------|
| `cloud_migration` | TeraSky Cloud Migration Services | Comprehensive cloud migration and modernization |
| `data_analytics` | TeraSky Advanced Data Analytics Platform | End-to-end data analytics and BI solutions |
| `cybersecurity` | TeraSky Cybersecurity Solutions | Enterprise-grade security services |
| `devops` | TeraSky DevOps Transformation | Complete DevOps transformation services |
| `ai_ml` | TeraSky AI/ML Solutions | AI and ML solutions for business automation |

## 🤖 Agent Roles

### Marketing Supervisor
- **Role**: Campaign orchestration and coordination
- **Responsibilities**: 
  - Manages workflow execution
  - Ensures quality and consistency
  - Coordinates between specialist agents
  - Validates final deliverables

### Specialist Agents

#### Product Researcher
- **Focus**: Deep product analysis and competitive positioning
- **Outputs**: Feature analysis, value propositions, market positioning

#### Audience Researcher  
- **Focus**: Target audience identification and persona development
- **Outputs**: Buyer personas, pain points, communication preferences

#### Campaign Strategist
- **Focus**: Comprehensive marketing strategy development
- **Outputs**: Channel strategy, messaging framework, campaign objectives

#### Content Creator
- **Focus**: Multi-channel content creation
- **Outputs**: Social media content, email campaigns, blog articles, ad copy

#### QA Validator
- **Focus**: Quality assurance and brand alignment
- **Outputs**: Content validation, brand compliance, improvement recommendations

## 📊 Workflow Process

### Sequential Task Execution
1. **Product Research Task**
   - Analyze product features and capabilities
   - Identify competitive advantages
   - Define value propositions

2. **Audience Research Task**
   - Develop target personas
   - Analyze decision-making processes
   - Identify communication channels

3. **Campaign Strategy Task**
   - Create comprehensive marketing strategy
   - Define campaign objectives and KPIs
   - Plan multi-channel approach

4. **Content Creation Task**
   - Generate compelling marketing content
   - Create channel-specific messaging
   - Develop creative assets

5. **Quality Assurance Task**
   - Validate content quality and accuracy
   - Ensure brand alignment
   - Provide improvement recommendations

6. **Final Campaign Report Task**
   - Compile comprehensive campaign package
   - Create executive summary
   - Package deliverables

## 🔧 Configuration

### Agent Configuration (`agents.yaml`)
```yaml
marketing_supervisor:
  role: Marketing Campaign Supervisor
  goal: Orchestrate complete marketing campaign development
  collaboration_type: SUPERVISOR
  collaborator_agents:
    - agent: product_researcher
      instructions: Use for product analysis and positioning
    - agent: audience_researcher  
      instructions: Use for audience analysis and personas
    # ... additional collaborators
```

### Task Configuration (`tasks.yaml`)
```yaml
product_research_task:
  description: Comprehensive product research and analysis
  expected_output: Detailed product analysis with competitive positioning
  agent: product_researcher
  inputs:
    - product_name
    - product_description
```

## 📈 Usage Examples

### Streamlit Interface
1. **Launch Application**
   ```bash
   python setup_supervisor_agents.py --mode streamlit
   ```

2. **Create Agents**
   - Click "Create Bedrock Agents" in sidebar
   - Wait for all agents to be created and prepared

3. **Generate Campaign**
   - Select product from dropdown
   - Click "Generate Campaign"
   - Monitor progress through supervisor orchestration

### Command Line Interface
```bash
# Basic campaign generation
python supervisor_bedrock_agents.py --product_key cloud_migration

# With full tracing
python supervisor_bedrock_agents.py \
  --product_key data_analytics \
  --enable_trace true \
  --trace_level full

# Recreate agents and generate campaign
python supervisor_bedrock_agents.py \
  --product_key cybersecurity \
  --recreate_agents true

# Clean up all agents
python supervisor_bedrock_agents.py --clean_up true
```

## 🔍 Monitoring and Debugging

### AWS Console Monitoring
- **Bedrock Agents Console**: View all created agents and their status
- **CloudWatch Logs**: Monitor agent execution and errors
- **CloudTrail**: Track API calls and agent interactions

### Trace Levels
- **Core**: Basic execution flow and key decisions
- **Full**: Detailed step-by-step execution with all intermediate results

### Common Issues and Solutions

#### Agent Creation Failures
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify Bedrock permissions
aws bedrock list-foundation-models

# Fix permissions if needed
python fix_agent_permissions.py
```

#### Permission Errors
```bash
# Run permission fix script
python fix_agent_permissions.py --agent_name product_researcher

# Or fix all agents
python fix_agent_permissions.py --fix_all true
```

## 📁 File Structure

```
terasky-marketing-agents/
├── supervisor_bedrock_agents.py      # CLI supervisor implementation
├── streamlit_supervisor_agents.py    # Streamlit supervisor app
├── setup_supervisor_agents.py        # Setup and run script
├── agents.yaml                       # Agent definitions
├── tasks.yaml                        # Task definitions
├── fix_agent_permissions.py          # Permission management
├── test_current_agents.py           # Agent testing utility
└── README_SUPERVISOR_AGENTS.md      # This documentation
```

## 🎨 Streamlit Interface Features

### Dashboard
- **Product Selection**: Visual product picker with descriptions
- **Agent Status**: Real-time agent creation and status monitoring
- **Progress Tracking**: Live progress updates during campaign generation

### Results Display
- **Campaign Summary**: Key metrics and execution details
- **Structured Output**: Organized display of all campaign components
- **Download Options**: JSON export of complete campaign results
- **Agent Traceability**: Clear visibility into which agents contributed

### User Experience
- **Responsive Design**: Works on desktop and tablet devices
- **Error Handling**: Clear error messages and recovery suggestions
- **Session Management**: Maintains state across interactions
- **Real-time Updates**: Live progress and status updates

## 🔄 Comparison with Previous Implementation

| Feature | Linear Approach | Supervisor Approach |
|---------|----------------|-------------------|
| **Orchestration** | Sequential function calls | True supervisor agent coordination |
| **Agent Collaboration** | Simulated through prompts | Real Bedrock agent collaboration |
| **Scalability** | Limited to predefined flow | Flexible task-based execution |
| **Monitoring** | Application-level logging | AWS Console + CloudWatch |
| **Error Handling** | Basic try-catch | Enterprise-grade error management |
| **Extensibility** | Code modifications required | YAML configuration changes |

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment
export AWS_PROFILE=production
export BEDROCK_REGION=us-east-1
export LOG_LEVEL=INFO

# Run with production settings
python setup_supervisor_agents.py --mode streamlit
```

### Scaling Considerations
- **Agent Limits**: AWS Bedrock has service limits on concurrent agents
- **Cost Management**: Monitor token usage and agent invocations
- **Performance**: Consider agent warm-up time for high-frequency usage

### Security Best Practices
- Use IAM roles with minimal required permissions
- Enable CloudTrail for audit logging
- Implement VPC endpoints for private network access
- Regular rotation of access keys

## 📞 Support and Troubleshooting

### Getting Help
1. **Check AWS Console**: Verify agent status in Bedrock console
2. **Review Logs**: Check CloudWatch logs for detailed error information
3. **Test Permissions**: Use `fix_agent_permissions.py` to diagnose issues
4. **Validate Configuration**: Ensure `agents.yaml` and `tasks.yaml` are correct

### Common Solutions
- **Agent Creation Timeout**: Increase wait times in configuration
- **Permission Denied**: Run permission fix script
- **Model Access**: Enable Claude 3.5 Sonnet in Bedrock console
- **Rate Limiting**: Implement exponential backoff in production

---

**Note**: This supervisor implementation represents the enterprise-grade approach to marketing campaign generation using AWS Bedrock's true multi-agent collaboration capabilities. 