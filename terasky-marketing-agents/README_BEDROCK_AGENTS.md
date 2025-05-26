# TeraSky Marketing Campaign Generator - Amazon Bedrock Agents Implementation

This directory contains the **proper implementation** of the TeraSky Marketing Campaign Generator using **Amazon Bedrock Agents** instead of direct model invocations.

## 🔍 Key Differences from Previous Implementation

### Previous Implementation (app.py)
- ❌ Used direct `bedrock-runtime` client calls
- ❌ Custom Python classes that invoke models directly
- ❌ No actual Bedrock Agents created in AWS
- ❌ No agent collaboration framework
- ❌ **Agents NOT visible in AWS Bedrock console**

### New Implementation (Bedrock Agents)
- ✅ Uses proper Amazon Bedrock Agents service
- ✅ Creates actual agents visible in AWS Bedrock console
- ✅ Implements agent collaboration with SupervisorAgent
- ✅ Task-based workflow orchestration
- ✅ **Agents ARE visible and manageable in AWS console**

## 📁 File Structure

```
terasky-marketing-agents/
├── agents.yaml                    # Agent configurations (roles, goals, instructions)
├── tasks.yaml                     # Task definitions for workflow
├── main_bedrock_agents.py         # Command-line version
├── bedrock_agent_app.py           # Streamlit version with Bedrock Agents
├── README_BEDROCK_AGENTS.md       # This file
└── [old files]                    # Previous implementation files
```

## 🚀 Quick Start

### Prerequisites
1. AWS credentials configured
2. Bedrock model access enabled
3. Required Python packages installed

### Command Line Usage

```bash
# Create agents and generate campaign
python main_bedrock_agents.py --product_key hashicorp_vault

# Reuse existing agents (faster)
python main_bedrock_agents.py --product_key upwind_security --recreate_agents false

# Cleanup all agents
python main_bedrock_agents.py --clean_up true
```

### Streamlit Usage

```bash
# Run the Streamlit app with Bedrock Agents
streamlit run bedrock_agent_app.py
```

## 🤖 Agent Architecture

### Individual Agents
1. **Product Researcher** - Analyzes product features and competitive landscape
2. **Audience Researcher** - Identifies target personas and market segments  
3. **Campaign Strategist** - Develops comprehensive marketing strategies
4. **Content Creator** - Creates multi-channel marketing content
5. **QA Validator** - Reviews and validates content quality

### Supervisor Agent
- **Marketing Supervisor** - Orchestrates the entire campaign generation process
- Coordinates collaboration between all specialist agents
- Manages task execution and workflow

## 📋 Task Workflow

1. **Product Research Task** - Comprehensive product analysis
2. **Audience Research Task** - Target audience identification
3. **Campaign Strategy Task** - Multi-channel strategy development
4. **Content Creation Task** - Marketing content generation
5. **Quality Assurance Task** - Content validation and review
6. **Final Campaign Report Task** - Comprehensive report compilation

## 🔧 Configuration

### Agent Configuration (agents.yaml)
- Defines agent roles, goals, and instructions
- Specifies LLM models for each agent
- Configures collaboration relationships

### Task Configuration (tasks.yaml)
- Defines workflow tasks and expected outputs
- Supports variable substitution (e.g., {product_name})
- Specifies output formats (JSON, Markdown)

## 🎯 Benefits of Bedrock Agents Implementation

### 1. **True Agent Collaboration**
- Agents can communicate and share context
- Supervisor orchestrates complex workflows
- Built-in retry and error handling

### 2. **AWS Console Visibility**
- View agents in Bedrock console
- Monitor agent performance and usage
- Access detailed execution traces

### 3. **Enterprise-Ready**
- Proper IAM roles and permissions
- Audit trails and logging
- Scalable architecture

### 4. **Extensibility**
- Easy to add new agents
- Support for external tools (Lambda functions)
- Knowledge base integration

## 🔍 Verification

After running the Bedrock Agents implementation, you can verify it's working correctly by:

1. **AWS Console Check**:
   - Go to Amazon Bedrock console
   - Navigate to "Agents" section
   - You should see the created agents listed

2. **Agent Names to Look For**:
   - `marketing_supervisor`
   - `product_researcher`
   - `audience_researcher`
   - `campaign_strategist`
   - `content_creator`
   - `qa_validator`

3. **Execution Traces**:
   - Enable tracing to see detailed agent interactions
   - View how agents collaborate and pass information

## 🛠️ Troubleshooting

### Common Issues

1. **Agents Not Visible in Console**
   - Ensure you're using the new implementation files
   - Check AWS credentials and permissions
   - Verify Bedrock service availability in your region

2. **Agent Creation Fails**
   - Check IAM permissions for Bedrock
   - Ensure model access is enabled
   - Review CloudWatch logs for detailed errors

3. **Slow Performance**
   - Use `--recreate_agents false` to reuse existing agents
   - Consider using faster models for development

### Debug Commands

```bash
# Enable detailed tracing
python main_bedrock_agents.py --trace_level all

# Check agent status
aws bedrock-agent list-agents

# Cleanup and start fresh
python main_bedrock_agents.py --clean_up true
```

## 📊 Performance Comparison

| Aspect | Direct Model Calls | Bedrock Agents |
|--------|-------------------|----------------|
| Setup Time | Fast | Slower (agent creation) |
| Execution | Direct | Orchestrated |
| Visibility | None | Full AWS console |
| Collaboration | Manual | Built-in |
| Scalability | Limited | Enterprise-ready |
| Debugging | Basic | Advanced tracing |

## 🎯 Next Steps

1. **Test the Implementation**:
   ```bash
   python main_bedrock_agents.py --product_key hashicorp_vault
   ```

2. **Verify in AWS Console**:
   - Check that agents are created and visible

3. **Run Streamlit Demo**:
   ```bash
   streamlit run bedrock_agent_app.py
   ```

4. **Customize for Your Needs**:
   - Modify `agents.yaml` for different roles
   - Update `tasks.yaml` for custom workflows
   - Add external tools and knowledge bases

## 📞 Support

For issues or questions about this Bedrock Agents implementation:
1. Check the AWS Bedrock documentation
2. Review CloudWatch logs for detailed error messages
3. Ensure all prerequisites are met
4. Test with the startup advisor example first

---

**Note**: This implementation creates actual Amazon Bedrock Agents that will be visible and manageable through the AWS console, providing true enterprise-grade agent collaboration capabilities. 