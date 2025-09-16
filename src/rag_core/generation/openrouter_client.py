import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any


def chat_with_openrouter(prompt: str, model: str = "deepseek/deepseek-r1-0528:free") -> Dict[str, Any]:
    """
    Send a chat completion request to OpenRouter API
    
    Args:
        prompt (str): The user's prompt/question
        model (str): The model to use for completion
        
    Returns:
        dict: The API response
    """
    # Set OpenRouter API key
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("RAG_OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("RAG_OPENROUTER_API_KEY not set in .env file.")
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    return response.json()
