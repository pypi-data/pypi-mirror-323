from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

import os


def get_model(provider: str):
    if provider == 'openai':
        return 'openai:gpt-4o'
    elif provider == 'anthropic':
        return 'claude-3-5-sonnet-latest'
    elif provider == 'groq':
        return 'groq:llama-3.1-70b-versatile'
    elif provider == 'openrouter':
        return OpenAIModel( 'anthropic/claude-3.5-sonnet', base_url='https://openrouter.ai/api/v1', api_key=os.getenv('OPENROUTER_API_KEY'))
    else:
        raise ValueError(f'Provider {provider} not supported')
