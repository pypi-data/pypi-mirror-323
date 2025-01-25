# SoftwareAI CLI (Command Line Interface)

## Overview

The SoftwareAI Command Line Interface (CLI) is designed to simplify and automate various tasks related to managing and using the SoftwareAI framework.

## Key Problems Solved

### 1. Configuration Management

#### Database Configuration
- Configure and securely store company database credentials
- Easily set up database connections for managed applications

##### Example Commands
```bash
# Company Database Configuration
python softwareai-cli.py configure-db-company \
  --namefordb "Company Database Name" \
  --databaseurl "https://database.url" \
  --storagebucketurl "https://storage.bucket" \
  --pathkey "/path/to/firebase-admin-sdk-key.json"
```

#### API and Service Integrations
- Quick configuration for:
  - OpenAI credentials
  - Hugging Face API keys
  - Other required service integrations

### 2. Automated Code Generation

- Automatically generate functions based on specified requirements
- Create agent instructions with ease
- Generate optimized prompts for agent interactions

### 3. Agent and System Management

- Local execution of SoftwareAI web interface
- Automated modification of agent components
- Direct execution of agent-specific tasks

## CLI Command Reference

### Configuration Commands
```bash
# Database Configuration
python cli.py configure-db-company --key "your_db_key"
python cli.py configure-db-app --key "your_app_db_key"

# AI Service Configuration
python cli.py configure-openai --key "your_openai_key"
python cli.py configure-huggingface --key "your_huggingface_key"
```

### Automation Commands
```bash
# Function and Agent Creation
python cli.py create-function --description "Example Function"
python cli.py create-instruction --agent-name "Agent1" --instruction "Example Instruction"
python cli.py create-prompt --agent-name "Agent1" --prompt "Example Prompt"
```

### Management Commands
```bash
# System and Agent Management
python cli.py run-web
python cli.py modify-agent --agent-name "Agent1" --component "componentX" --new-value "new_value"
python cli.py execute-agent-task --agent-name "Agent1" --task "taskX"
```

## Best Practices

- Always use secure, environment-specific keys
- Regularly update and rotate credentials
- Validate configurations before deployment
