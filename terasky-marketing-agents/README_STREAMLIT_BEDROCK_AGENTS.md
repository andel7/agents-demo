# 🚀 TeraSky Marketing Campaign Generator - Real Bedrock Agents + Streamlit

This is the **REAL** Bedrock Agents implementation with a beautiful Streamlit interface!

## 🎯 What This Solves

### ❌ **Previous Problem:**
- The original Streamlit app used **fake "agents"** (just direct model calls)
- No actual Bedrock Agents were created in AWS
- Agents were **NOT visible** in AWS Bedrock console
- No real agent collaboration

### ✅ **New Solution:**
- **Real Amazon Bedrock Agents** created and managed by AWS
- Agents **visible in AWS Bedrock console** with unique IDs
- **True agent collaboration** with session management
- **Professional Streamlit UI** for easy interaction
- **Enterprise-grade marketing workflows**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB APP                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              User Interface                         │   │
│  │  • Product Selection                                │   │
│  │  • Agent Discovery                                  │   │
│  │  • Campaign Generation                              │   │
│  │  • Results Display                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 AWS BEDROCK AGENTS                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Product   │  │  Audience   │  │  Campaign   │        │
│  │ Researcher  │  │ Researcher  │  │ Strategist  │        │
│  │             │  │             │  │             │        │
│  │ ID: ABC123  │  │ ID: DEF456  │  │ ID: GHI789  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐                         │
│  │   Content   │  │     QA      │                         │
│  │   Creator   │  │  Validator  │                         │
│  │             │  │             │                         │
│  │ ID: JKL012  │  │ ID: MNO345  │                         │
│  └─────────────┘  └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the all-in-one setup script
python3 setup_and_run.py
```

This will:
1. ✅ Check for existing agents
2. ✅ Create missing agents if needed
3. ✅ Fix IAM permissions
4. ✅ Launch Streamlit app automatically

### Option 2: Manual Setup
```bash
# 1. Create agents (if not already created)
python3 simple_bedrock_agents.py --product_key hashicorp_vault --recreate_agents true --cleanup_after false

# 2. Fix permissions
python3 fix_agent_permissions.py

# 3. Launch Streamlit
streamlit run streamlit_bedrock_agents.py
```

## 🎮 How to Use

1. **🔍 Discover Agents**
   - Click "Discover Agents" in the sidebar
   - App will find your real Bedrock agents
   - Agent IDs will be displayed

2. **📦 Select Product**
   - Choose from TeraSky's product catalog
   - Each product has specialized marketing needs

3. **🚀 Generate Campaign**
   - Click "Generate Marketing Campaign"
   - Watch real agents collaborate in real-time
   - See progress through 5 specialized steps

4. **📊 View Results**
   - Comprehensive campaign results in organized tabs
   - Professional marketing content
   - Quality assurance validation

## 🤖 The 5 Marketing Agents

| Agent | Role | Specialization |
|-------|------|----------------|
| **🔍 Product Researcher** | Research Specialist | Technical analysis, competitive positioning |
| **👥 Audience Researcher** | Target Analyst | Buyer personas, decision-maker profiles |
| **📋 Campaign Strategist** | Strategy Director | Multi-channel campaigns, KPIs, budgets |
| **✍️ Content Creator** | Content Specialist | Social media, emails, ads, landing pages |
| **✅ QA Validator** | Quality Assurance | Brand compliance, technical accuracy |

## 🎯 Products Supported

- 🔐 **HashiCorp Vault** - Enterprise secrets management
- 🛡️ **UpWind Security** - Cloud-native Kubernetes security
- 💾 **Portworx by Pure** - Enterprise Kubernetes storage
- 🤖 **Prompt.security** - AI security and compliance
- ☁️ **Spectro Cloud** - Kubernetes management platform
- ⚡ **Other TeraSky Solutions** - Custom enterprise solutions

## 🔧 Files Overview

| File | Purpose |
|------|---------|
| `streamlit_bedrock_agents.py` | **Main Streamlit app** with real Bedrock agents |
| `simple_bedrock_agents.py` | Command-line agent creation and testing |
| `fix_agent_permissions.py` | IAM permission fixes for agents |
| `setup_and_run.py` | **One-click setup and launch** |
| `test_current_agents.py` | Test existing agents |
| `agents.yaml` | Agent role definitions |
| `tasks.yaml` | Workflow task definitions |

## 🆚 Comparison: Old vs New

| Feature | Old Streamlit App | New Bedrock Agents App |
|---------|-------------------|------------------------|
| **Agent Type** | ❌ Fake (direct model calls) | ✅ Real AWS Bedrock Agents |
| **AWS Console** | ❌ Not visible | ✅ Visible with IDs |
| **Collaboration** | ❌ Simulated | ✅ True agent sessions |
| **Management** | ❌ Manual code | ✅ AWS managed service |
| **Scalability** | ❌ Limited | ✅ Enterprise-grade |
| **Monitoring** | ❌ None | ✅ AWS CloudWatch integration |

## 🎨 Streamlit Features

- **🎯 Modern UI** - Professional gradient design
- **📊 Real-time Progress** - Live progress bars and status
- **🔄 Agent Discovery** - Automatic agent detection
- **📋 Organized Results** - Tabbed interface for easy navigation
- **⚡ Caching** - Optimized AWS client caching
- **🎮 Interactive** - Click-to-generate workflow

## 🔍 Verification

### Check Agents in AWS Console:
1. Go to **AWS Bedrock Console**
2. Navigate to **Agents**
3. You should see 5 agents:
   - `product_researcher`
   - `audience_researcher`
   - `campaign_strategist`
   - `content_creator`
   - `qa_validator`

### Test Individual Agents:
```bash
python3 test_current_agents.py
```

## 🚨 Troubleshooting

### Permission Issues:
```bash
python3 fix_agent_permissions.py
# Wait 2-3 minutes for IAM propagation
```

### Missing Agents:
```bash
python3 simple_bedrock_agents.py --recreate_agents true
```

### Streamlit Issues:
```bash
# Install dependencies
pip install streamlit boto3 pyyaml

# Clear cache
streamlit cache clear
```

## 🎉 Success Indicators

✅ **Agents visible in AWS Bedrock console**  
✅ **Real agent IDs displayed in Streamlit**  
✅ **Professional marketing content generated**  
✅ **Multi-step collaborative workflow**  
✅ **Enterprise-grade campaign strategies**  

## 🏆 What You've Achieved

You now have a **production-ready marketing campaign generator** that:

- Uses **real Amazon Bedrock Agents** (not simulations)
- Provides a **beautiful Streamlit interface**
- Generates **professional marketing campaigns**
- Demonstrates **true agent collaboration**
- Is **visible and manageable in AWS console**

This is exactly what enterprise customers expect from Bedrock Agents! 🚀 