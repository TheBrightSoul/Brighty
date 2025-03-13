"""
OpenRouter API Client Implementation

Provides asynchronous and synchronous (legacy) interfaces for interacting with 
the OpenRouter API. Handles chat completions, model listings, and error handling.
"""
import aiohttp
import json
import asyncio

class OpenRouterAPI:
    """
    Client for interacting with OpenRouter's API.
    
    Features:
    - Async/Await support for non-blocking requests
    - Automatic timeout handling (60s for chat, 30s for models)
    - Detailed error logging and error response generation
    - Backward-compatible sync methods (deprecated)
    
    Attributes:
        BASE_URL (str): Base URL for OpenRouter API endpoints
        api_key (str): Authentication token for API access
        headers (dict): Pre-configured request headers with auth
    """
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key):
        """Initialize API client with authentication credentials.
        
        Args:
            api_key (str): OpenRouter API key obtained from dashboard
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion_async(self, messages, model):
        """Execute asynchronous chat completion request.
        
        Args:
            messages (list): Conversation history in OpenAI format
            model (str): Target model ID (e.g., 'gpt-3.5-turbo')
            
        Returns:
            dict: API response payload or error object
            
        Raises:
            aiohttp.ClientError: For network-level issues
            asyncio.TimeoutError: If request exceeds 60 seconds
        """
        url = f"{self.BASE_URL}/chat/completions"
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000  # Prevent overly long responses
        }
        
        # Diagnostic logging - shows request metadata
        print(f"[OpenRouter] Starting request to {url}")
        print(f"[OpenRouter] Selected model: {model}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    headers=self.headers, 
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60)  # Fail fast if unresponsive
                ) as response:
                    # Process successful response
                    print(f"[OpenRouter] Received status: {response.status}")
                    response_json = await response.json()
                    print(f"[OpenRouter] Response snippet: {str(response_json)[:200]}...")
                    return response_json
                    
        except asyncio.TimeoutError:
            print("[OpenRouter] Timeout after 60 seconds")
            return {"error": {"message": "Request timed out", "code": 408}}
        except Exception as e:
            # Catch-all for unexpected errors
            print(f"[OpenRouter] Critical error: {str(e)}")
            return {"error": {"message": f"Request failed: {str(e)}", "code": 500}}
    
    async def get_models_async(self):
        """Fetch list of available models from OpenRouter.
        
        Returns:
            list/dict: Model list on success, error dict on failure
        """
        url = f"{self.BASE_URL}/models"  # Models endpoint
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)  # Shorter timeout for model list
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"[OpenRouter] Model fetch failed: HTTP {response.status}")
                        return None
        except Exception as e:
            print(f"[OpenRouter] Model list error: {str(e)}")
            return None
    
    # Legacy sync methods ------------------------------------------------------
    def chat_completion(self, messages, model):
        """Synchronous version (DEPRECATED - prefer async)
        
        Warning:
            This method blocks the event loop. Only use for compatibility with
            legacy systems that can't support async/await.
        """
        import requests
        url = f"{self.BASE_URL}/chat/completions"
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000  # Limit response size to avoid timeouts
        }
        
        try:
            print(f"Sending request to {url}")
            print(f"Using model: {model}")
            response = requests.post(
                url, 
                headers=self.headers, 
                data=json.dumps(data),
                timeout=60  # 60 second timeout
            )
            
            print(f"Response status: {response.status_code}")
            if hasattr(response, 'text') and response.text:
                print(f"Response preview: {response.text[:200]}...")
            
            return response
        except requests.exceptions.Timeout:
            print("Request timed out")
            # Create a mock response object with timeout information
            mock_response = requests.Response()
            mock_response.status_code = 408
            mock_response._content = b'{"error": {"message": "Request timed out"}}'
            return mock_response
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {str(e)}")
            # Create a mock response object with error information
            mock_response = requests.Response()
            mock_response.status_code = 500
            mock_response._content = f'{{"error": {{"message": "Request failed: {str(e)}"}}}}'.encode('utf-8')
            return mock_response
    
    def get_models(self):
        """Synchronous model list (DEPRECATED - prefer async)
        
        Note:
            This method may cause performance issues in async contexts
        """
        import requests
        url = f"{self.BASE_URL}/models"
        response = requests.get(url, headers=self.headers)
        return response
