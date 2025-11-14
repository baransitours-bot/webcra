# Assistant Service Documentation

The Assistant Service provides AI-powered answers about immigration using OpenRouter or OpenAI.

## Quick Start

### Setup

**Option 1: OpenRouter (FREE)** ✅ Recommended

```bash
# Get free API key from https://openrouter.ai/keys
# Then either:

# A. Set environment variable (Windows PowerShell)
$env:OPENROUTER_API_KEY = 'sk-or-v1-...'

# B. Or put directly in config.yaml
# Edit services/assistant/config.yaml:
#   api_key_env: "sk-or-v1-..."
```

**Option 2: OpenAI (Paid)**

```yaml
# Edit services/assistant/config.yaml
provider: "openai"  # Change from "openrouter"

# Set API key
# Windows: $env:OPENAI_API_KEY = 'sk-...'
# Linux/Mac: export OPENAI_API_KEY='sk-...'
```

### Usage

```bash
# Single query
python main.py assist --query "What work visas are available in Canada?"

# Interactive chat mode
python main.py assist --chat

# With user profile
python main.py assist --query "Am I eligible?" --profile user.json
```

## Configuration

File: `services/assistant/config.yaml`

```yaml
llm:
  # Choose provider: "openai" or "openrouter"
  provider: "openrouter"  # Default to free option

  # OpenAI Configuration (paid service)
  openai:
    model: "gpt-4o-mini"  # cost-effective model
    api_key_env: "OPENAI_API_KEY"

  # OpenRouter Configuration (free models available)
  openrouter:
    model: "meta-llama/llama-3.1-8b-instruct:free"  # free model
    api_key_env: "OPENROUTER_API_KEY"
    base_url: "https://openrouter.ai/api/v1"

  # Shared LLM parameters
  temperature: 0.3
  max_tokens: 1000

context:
  max_visas: 5
  max_tokens_per_visa: 500
```

## Features

### 1. Context-Aware Responses

The assistant automatically:
1. Identifies relevant country/visa from your query
2. Retrieves visa information from database
3. Generates answer based on official data
4. Cites source URLs

### 2. Multiple LLM Providers

| Provider | Cost | Setup | Model |
|----------|------|-------|-------|
| **OpenRouter** | FREE | Get key from [openrouter.ai/keys](https://openrouter.ai/keys) | Llama 3.1 8B |
| **OpenAI** | Paid | Get key from [platform.openai.com](https://platform.openai.com) | GPT-4o-mini |

### 3. User Profile Integration

Provide your profile for personalized answers:

```bash
python main.py assist --query "Am I eligible for Canada?" --profile user.json
```

The assistant will:
- Consider your age, education, experience
- Identify which requirements you meet
- Highlight any gaps

### 4. Interactive Chat Mode

Have a conversation:

```bash
python main.py assist --chat
```

```
You: What work visas are available in Australia?
Assistant: Australia offers several work visa options...

You: What are the requirements for the Skilled Independent visa?
Assistant: The Skilled Independent visa (subclass 189) requires...

You: exit
```

## Query Examples

### General Questions

```bash
# Country-specific
python main.py assist --query "What visas are available in Canada?"

# Category-specific
python main.py assist --query "Tell me about student visas in UK"

# Requirement-specific
python main.py assist --query "What are the age requirements for Australian work visas?"
```

### Eligibility Questions

```bash
# With profile
python main.py assist --query "Which Canadian visas am I eligible for?" --profile user.json

# Specific visa
python main.py assist --query "Am I eligible for the Skilled Worker visa?" --profile user.json
```

### Process Questions

```bash
python main.py assist --query "How do I apply for a German work visa?"
python main.py assist --query "What documents do I need for UK student visa?"
python main.py assist --query "How long does Canada visa processing take?"
```

## How It Works

### 1. Query Analysis

```
User: "What work visas are available in Canada?"
      ↓
Extract: country=canada, category=work
```

### 2. Context Retrieval

```
Retrieve relevant visas from data/structured/canada.json
Filter by category: work
Top 5 most relevant visas
```

### 3. LLM Prompting

```
System: You are an expert immigration consultant...

Context: [Structured visa data with requirements]

User Query: What work visas are available in Canada?

Generate: Accurate answer with citations
```

### 4. Response Generation

```
Assistant: Canada offers several work visa options:

1. **Federal Skilled Worker Program**
   - For skilled professionals
   - Requirements: Age 18-45, Bachelor's degree...
   - Source: https://...

2. **Temporary Foreign Worker Program**
   ...
```

## Configuration Options

### Temperature

Controls response creativity:

```yaml
temperature: 0.3  # Conservative (0.0 - 1.0)
```

- `0.0-0.3` - Factual, consistent (recommended for immigration)
- `0.4-0.7` - Balanced
- `0.8-1.0` - Creative (not recommended)

### Max Tokens

Controls response length:

```yaml
max_tokens: 1000  # ~750 words
```

- `500` - Brief answers
- `1000` - Standard (recommended)
- `2000` - Detailed answers

### Context Size

Number of visas to include:

```yaml
context:
  max_visas: 5  # Top 5 most relevant
```

## Troubleshooting

### API Key Errors

**Error:**
```
❌ Error: OPENROUTER_API_KEY environment variable not set!
```

**Solutions:**

1. **Windows PowerShell:**
   ```powershell
   $env:OPENROUTER_API_KEY = 'your-key-here'
   ```

2. **Linux/Mac:**
   ```bash
   export OPENROUTER_API_KEY='your-key-here'
   ```

3. **Or put directly in config:**
   ```yaml
   # services/assistant/config.yaml
   openrouter:
     api_key_env: "sk-or-v1-your-actual-key-here"
   ```

### No Visa Data Found

**Error:**
```
❌ No relevant visa information found for your query.
```

**Solutions:**
1. Run classifier first:
   ```bash
   python main.py classify --all
   ```

2. Be more specific in query:
   ```
   Bad: "tell me about visas"
   Good: "what work visas are available in Canada?"
   ```

### Rate Limiting

If using free tier, you may hit rate limits.

**Solutions:**
1. Wait a few seconds between queries
2. Upgrade to paid tier
3. Switch providers

### Poor Quality Answers

**Causes:**
- Insufficient context
- Vague query
- Missing structured data

**Solutions:**
1. Be specific in queries
2. Ensure classifier has run successfully
3. Adjust temperature (lower = more factual)

## API Reference

### LLMClient

```python
from services.assistant.llm_client import LLMClient

client = LLMClient(config)
answer = client.generate_answer(system_prompt, user_prompt)
```

### ContextRetriever

```python
from services.assistant.retriever import ContextRetriever

retriever = ContextRetriever(config)
visas = retriever.retrieve_relevant_visas(
    query="work visas in Canada",
    user_profile={"age": 28, ...}
)
```

## Cost Estimation

### OpenRouter (FREE)

- **Model**: Llama 3.1 8B Instruct
- **Cost**: $0.00
- **Limits**: Rate limited (generous free tier)

### OpenAI

- **Model**: GPT-4o-mini
- **Cost**: ~$0.15 per million input tokens, ~$0.60 per million output tokens
- **Estimate**: ~$0.001 per query (very cheap)
- **Example**: 1000 queries ≈ $1.00

## Advanced Usage

### Custom Prompts

Edit `services/assistant/prompts.py`:

```python
SYSTEM_PROMPT = """You are an expert immigration consultant...
[Customize this for your use case]
"""
```

### Multiple Providers

Switch providers dynamically:

```python
# Use OpenRouter
config['llm']['provider'] = 'openrouter'
client1 = LLMClient(config)

# Use OpenAI
config['llm']['provider'] = 'openai'
client2 = LLMClient(config)
```

## See Also

- [Matcher Service](matcher.md) - Get visa matches first
- [Configuration Guide](../guides/configuration.md) - Full configuration
- [Troubleshooting](../troubleshooting.md) - Common issues

---

**Previous**: [← Matcher Service](matcher.md)
