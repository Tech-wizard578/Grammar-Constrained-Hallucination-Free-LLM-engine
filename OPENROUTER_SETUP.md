# OpenRouter API Setup Guide

## ✅ Code Updated for OpenRouter Support!

The engine now supports **OpenRouter API** which gives you access to multiple LLM providers through a single API:
- OpenAI (GPT-4, GPT-4o, GPT-3.5)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google (Gemini Pro)
- Meta (Llama models)
- And many more!

## 🔑 How to Use OpenRouter

### Step 1: Get Your OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign up or log in
3. Navigate to https://openrouter.ai/keys
4. Create a new API key
5. Copy your key (starts with `sk-or-v1-...`)

### Step 2: Configure Your .env File

Edit `d:\RTRP\hallucination_free_engine\.env`:

```bash
# Set USE_OPENROUTER to true
USE_OPENROUTER=true

# Add your OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Add your Tavily API key (still required for web search)
TAVILY_API_KEY=tvly-your-key-here

# Choose your models (use provider/model format)
DEFAULT_MODEL=openai/gpt-4o-mini
SMART_MODEL=openai/gpt-4o
```

### Step 3: Choose Your Models

OpenRouter uses the format `provider/model`. Popular options:

**Fast/Cheap (for DEFAULT_MODEL)**:
- `openai/gpt-4o-mini` - Fast and cheap
- `anthropic/claude-3-haiku` - Fast Claude model
- `google/gemini-flash-1.5` - Google's fast model

**Smart/Powerful (for SMART_MODEL)**:
- `openai/gpt-4o` - Best OpenAI model
- `anthropic/claude-3-opus` - Most capable Claude
- `anthropic/claude-3-sonnet` - Balanced Claude
- `google/gemini-pro-1.5` - Google's best

**Full model list**: https://openrouter.ai/models

## 📝 Example Configuration

### Using OpenAI models via OpenRouter:
```bash
USE_OPENROUTER=true
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEFAULT_MODEL=openai/gpt-4o-mini
SMART_MODEL=openai/gpt-4o
```

### Using Claude models:
```bash
USE_OPENROUTER=true
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEFAULT_MODEL=anthropic/claude-3-haiku
SMART_MODEL=anthropic/claude-3-sonnet
```

### Using mixed providers:
```bash
USE_OPENROUTER=true
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEFAULT_MODEL=openai/gpt-4o-mini      # Fast OpenAI for routing
SMART_MODEL=anthropic/claude-3-opus   # Smart Claude for generation
```

## ⚠️ Important Notes

### Embeddings
OpenRouter **does not support embeddings API**. The engine will automatically use local Sentence Transformers for embeddings when using OpenRouter.

You'll see this message:
```
🏠 Using local Sentence Transformer embeddings (all-MiniLM-L6-v2)
   Note: OpenRouter doesn't support embeddings API
```

This is normal and works fine! The local embeddings are free and fast.

### If You Want OpenAI Embeddings
If you want to use OpenAI's embeddings (text-embedding-3-small) while using OpenRouter for LLMs:

```bash
# Keep both API keys
OPENAI_API_KEY=sk-proj-xxxxx          # For embeddings only
OPENROUTER_API_KEY=sk-or-v1-xxxxx     # For LLMs
USE_OPENROUTER=true
```

The engine will use:
- OpenRouter for LLM calls (generation, grading, verification)
- OpenAI for embeddings

## 💰 Pricing

OpenRouter pricing varies by model. Check https://openrouter.ai/models for current rates.

**Example costs per 1M tokens**:
- `openai/gpt-4o-mini`: ~$0.15 input, ~$0.60 output
- `anthropic/claude-3-haiku`: ~$0.25 input, ~$1.25 output
- `anthropic/claude-3-sonnet`: ~$3 input, ~$15 output

## 🧪 Testing Your Setup

After configuring, test with:

```bash
cd d:\RTRP\hallucination_free_engine

# Test configuration
python -c "from config import validate_config, get_config_summary; validate_config(); print(get_config_summary())"

# Test with a query (after ingesting documents)
python main.py query "What is Python?"
```

You should see:
```
api_provider: OpenRouter
api_base_url: https://openrouter.ai/api/v1
```

## 🔄 Switching Back to OpenAI

To switch back to direct OpenAI:

```bash
USE_OPENROUTER=false
OPENAI_API_KEY=sk-proj-xxxxx
DEFAULT_MODEL=gpt-4o-mini
SMART_MODEL=gpt-4o
```

## ✅ Summary

1. Get OpenRouter key from https://openrouter.ai/keys
2. Edit `.env`: Set `USE_OPENROUTER=true` and add `OPENROUTER_API_KEY`
3. Choose models in `provider/model` format
4. Local embeddings will be used automatically (free!)
5. Test with `python main.py stats`

**You're all set!** 🚀
