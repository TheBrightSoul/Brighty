"""
Context Management System

Manages conversation history and user preferences for chat applications.
Maintains separate contexts per user to enable continuous conversations.
"""
class ContextManager:
    """Handles user-specific conversation context and model preferences."""
    
    def __init__(self):
        """Initialize empty context and model storage."""
        self.contexts = {}  # {user_id: list of message dicts}
        self.user_models = {}  # {user_id: model_name}

    def update_context(self, user_id, user_message, bot_response):
        """Add new messages to a user's conversation history.
        
        Args:
            user_id (str): Unique identifier for user/session
            user_message (str): User's input message
            bot_response (str): Assistant's generated response
        """
        if user_id not in self.contexts:
            self.contexts[user_id] = []
        # Maintain conversation flow with alternating roles
        self.contexts[user_id].append({"role": "user", "content": user_message})
        self.contexts[user_id].append({"role": "assistant", "content": bot_response})

    def get_context(self, user_id):
        """Retrieve full conversation history for a user.
        
        Args:
            user_id (str): User identifier to fetch context for
            
        Returns:
            list: Conversation history in OpenAI message format
        """
        return self.contexts.get(user_id, [])

    def clear_context(self, user_id):
        """Reset conversation history for a user.
        
        Args:
            user_id (str): User identifier to clear context for
        """
        if user_id in self.contexts:
            self.contexts[user_id] = []  # Maintain user entry but empty history

    def set_user_model(self, user_id, model):
        """Store preferred AI model for a user.
        
        Args:
            user_id (str): User identifier to update
            model (str): Model name from OpenRouter's supported models
        """
        self.user_models[user_id] = model

    def get_user_model(self, user_id):
        """Retrieve user's preferred model or return default.
        
        Args:
            user_id (str): User identifier to check
            
        Returns:
            str: Model name configured for user or fallback default
        """
        return self.user_models.get(user_id, "google/gemini-2.0-flash-lite-preview-02-05:free")
