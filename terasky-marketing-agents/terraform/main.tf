# TeraSky Marketing Agents - IAM Configuration
# This Terraform configuration creates proper IAM roles and policies for Bedrock agents

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "agent_names" {
  description = "List of agent names"
  type        = list(string)
  default = [
    "product_researcher",
    "audience_researcher",
    "campaign_strategist",
    "content_creator",
    "qa_validator"
  ]
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "terasky-marketing"
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# IAM Trust Policy for Bedrock Agents
data "aws_iam_policy_document" "bedrock_agent_trust" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# IAM Policy for Bedrock Agent Execution
data "aws_iam_policy_document" "bedrock_agent_execution" {
  statement {
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
      "bedrock:GetFoundationModel",
      "bedrock:ListFoundationModels",
      "bedrock:GetModelInvocationLoggingConfiguration",
      "bedrock:GetUsageMetrics",
      "bedrock:ApplyGuardrail",
      "bedrock:GetGuardrail",
      "bedrock:ListGuardrails",
      "bedrock:ListInferenceProfiles",
      "bedrock:GetInferenceProfile"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "bedrock-agent:InvokeAgent",
      "bedrock-agent:GetAgent",
      "bedrock-agent:ListAgents",
      "bedrock-agent:GetAgentAlias",
      "bedrock-agent:ListAgentAliases"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:CreateLogDelivery",
      "logs:DescribeResourcePolicies",
      "logs:DescribeLogGroups"
    ]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "iam:PassRole"
    ]
    resources = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AmazonBedrockExecutionRoleForAgents_*"
    ]
  }
}

# IAM Roles for each agent
resource "aws_iam_role" "bedrock_agent_role" {
  for_each = toset(var.agent_names)
  
  name               = "AmazonBedrockExecutionRoleForAgents_${each.value}"
  assume_role_policy = data.aws_iam_policy_document.bedrock_agent_trust.json
  
  tags = {
    Project = var.project_name
    Agent   = each.value
    Purpose = "Bedrock Agent Execution"
  }
}

# IAM Policy attachment for each agent
resource "aws_iam_role_policy" "bedrock_agent_policy" {
  for_each = toset(var.agent_names)
  
  name   = "${each.value}_comprehensive_bedrock_access"
  role   = aws_iam_role.bedrock_agent_role[each.value].id
  policy = data.aws_iam_policy_document.bedrock_agent_execution.json
}

# Output the role ARNs
output "agent_role_arns" {
  description = "ARNs of the created IAM roles for Bedrock agents"
  value = {
    for agent_name in var.agent_names :
    agent_name => aws_iam_role.bedrock_agent_role[agent_name].arn
  }
}

output "agent_role_names" {
  description = "Names of the created IAM roles for Bedrock agents"
  value = {
    for agent_name in var.agent_names :
    agent_name => aws_iam_role.bedrock_agent_role[agent_name].name
  }
}

# Create a summary output
output "setup_summary" {
  description = "Setup summary for the marketing agents"
  value = {
    project_name = var.project_name
    aws_region   = var.aws_region
    agent_count  = length(var.agent_names)
    agents       = var.agent_names
    account_id   = data.aws_caller_identity.current.account_id
  }
} 