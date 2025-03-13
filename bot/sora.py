"""
Discord Bot Implementation

Handles bot initialization, command processing, and message interactions.
Integrates with OpenRouter API for AI responses and maintains conversation context.
"""
import asyncio
import discord
from discord.ext import commands
import shutil
import json
import aiohttp
from api.context_manager import ContextManager
from api.openrouter import OpenRouterAPI  # We'll modify this class too
from bot.ui import ModelListView

class Sora:
    """Main Discord bot class handling interactions and AI integration.
    
    Attributes:
        bot (commands.Bot): Discord.py bot instance
        api (OpenRouterAPI): OpenRouter API client
        context_manager (ContextManager): Manages conversation history
        token (str): Discord bot token
        channel_id (int): Restricted channel for bot responses
        default_model (str): Default AI model for responses
    """
    
    def __init__(self, token, api_key):
        """Initialize bot with credentials and dependencies.
        
        Args:
            token (str): Discord bot token from developer portal
            api_key (str): OpenRouter API key for AI access
        """
        self.bot = commands.Bot(intents=discord.Intents.all(), command_prefix="")
        self.api = OpenRouterAPI(api_key)
        self.context_manager = ContextManager()
        self.token = token
        self.channel_id = 874348504502370331
        self.allow_user_model_selection = False
        self.default_model = "google/gemini-2.0-flash-lite-preview-02-05:free"
        self.setup()

    def setup(self):
        """Configure bot event handlers and slash commands."""
        @self.bot.event
        async def on_ready():
            """Handle bot startup completion event."""
            terminal_width = shutil.get_terminal_size().columns  # Get the width of the terminal

            # Calculate the padding needed to center the message
            padding = (terminal_width - 60) // 2

            print("\n" + " " * padding + "\033[94m╔══════════════════════════════════════════════════════╗\033[0m")
            print(" " * padding + "\033[94m║\033[0m                                                      \033[94m║\033[0m")
            print(" " * padding + "\033[94m║\033[0m                   \033[1m\033[96mSoul's Assistant\033[0m                   \033[94m║\033[0m")
            print(" " * padding + "\033[94m║\033[0m                    \033[96m\033[0m                       \033[94m║\033[0m")
            print(" " * padding + "\033[94m╠══════════════════════════════════════════════════════╣\033[0m")
            print(" " * padding + "\033[94m║\033[0m                                                      \033[94m║\033[0m")
            print(" " * padding + f"\033[94m║\033[0m \033[1m\033[96mLogged in as:\033[0m \033[96mSoul\033[0m                  \033[94m║\033[0m")
            print(" " * padding + f"\033[94m║\033[0m \033[1m\033[96mUser ID:\033[0m      \033[96m{self.bot.user.id}\033[0m                    \033[94m║\033[0m")
            print(" " * padding + "\033[94m║\033[0m                                                      \033[94m║\033[0m")
            print(" " * padding + "\033[94m╚══════════════════════════════════════════════════════╝\033[0m")
            print("\n")
            print(" " * padding + "\033[96m         Let's engage in delightful conversations! \033[0m\n")

            await self.bot.tree.sync()  # Sync slash commands

        @self.bot.tree.command(name="set_channel", description="Set the channel ID for the bot to respond to")
        async def set_channel(interaction: discord.Interaction, channel: str):
            """Restrict or allow bot responses across channels.
            
            Args:
                channel (str): 'all' or specific channel ID to restrict to
            """
            if channel.lower() == "all":
                self.channel_id = None
                await interaction.response.send_message("Bot will now respond to messages in all channels.")
            else:
                try:
                    self.channel_id = int(channel)
                    await interaction.response.send_message(f"Bot will now respond to messages in channel ID: {self.channel_id}")
                except ValueError:
                    await interaction.response.send_message("Invalid channel ID. Please provide a valid channel ID or 'all'.")

        @self.bot.tree.command(name="list_models", description="Retrieve the list of available models")
        async def list_models(interaction: discord.Interaction):
            """Display paginated list of available AI models."""
            # Use the async version of get_models
            models_data = await self.api.get_models_async()
            if models_data:
                models = models_data["data"]
                
                # Format the model list with custom styling
                model_list = []
                for model in models:
                    # Truncate the description if it exceeds 100 characters
                    description = model['description'][:100] + "..." if len(model['description']) > 100 else model['description']
                    
                    model_info = (
                        f"🤖 **{model['name']}**\n"
                        f"  ╰ *Model ID:* `{model['id']}`\n"
                    )
                    model_list.append(model_info)
                
                # Split the model list into chunks of 5 models per page
                chunk_size = 5
                model_chunks = [model_list[i:i+chunk_size] for i in range(0, len(model_list), chunk_size)]
                
                # Create the paginated embed
                embed = discord.Embed(
                    title="📚 Available Models",
                    description="Browse the list of available models using the buttons below.",
                    color=discord.Color.blue()
                )
                
                def update_embed(page):
                    embed.clear_fields()
                    embed.add_field(name="Models", value="\n".join(model_chunks[page]), inline=False)
                    embed.set_footer(text=f"Page {page + 1}/{len(model_chunks)}")
                
                update_embed(0)
                
                view = ModelListView(model_chunks, update_embed, embed)
                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.response.send_message("Failed to retrieve the list of models.")

        @self.bot.tree.command(name="set_model", description="Set the model to use")
        async def set_model(interaction: discord.Interaction, model_id: str):
            """Set user's preferred AI model (admin-restricted).
            
            Args:
                model_id (str): Model ID from OpenRouter's list
            """
            user_id = interaction.user.id
            if self.allow_user_model_selection or interaction.user.guild_permissions.administrator:
                self.context_manager.set_user_model(user_id, model_id)
                await interaction.response.send_message(f"Model set to: {model_id}")
            else:
                await interaction.response.send_message("You don't have permission to set the model.")
        
        @self.bot.tree.command(name="set_default_model", description="Set the default model for all users (admin only)")
        async def set_default_model(interaction: discord.Interaction, model_id: str):
            """Admin command to set server-wide default model.
            
            Args:
                model_id (str): Model ID from OpenRouter's list
            """
            if interaction.user.guild_permissions.administrator:
                self.default_model = model_id
                await interaction.response.send_message(f"Default model set to: {model_id}")
            else:
                await interaction.response.send_message("You don't have permission to set the default model.")
        
        @self.bot.tree.command(name="toggle_user_model_selection", description="Toggle user model selection (admin only)")
        async def toggle_user_model_selection(interaction: discord.Interaction):
            """Enable/disable user model selection capability."""
            if interaction.user.guild_permissions.administrator:
                self.allow_user_model_selection = not self.allow_user_model_selection
                status = "enabled" if self.allow_user_model_selection else "disabled"
                await interaction.response.send_message(f"User model selection {status}.")
            else:
                await interaction.response.send_message("You don't have permission to toggle user model selection.")
        
        @self.bot.tree.command(name="clear_context", description="Clear the conversation context")
        async def clear_context(interaction: discord.Interaction):
            """Reset user's conversation history."""
            user_id = interaction.user.id
            self.context_manager.clear_context(user_id)
            await interaction.response.send_message("Conversation context cleared.")

        @self.bot.event
        async def on_message(message):
            """Process incoming messages and generate AI responses.
            
            Handles:
            - Channel restrictions
            - Context management
            - Async response generation
            - Error handling
            """
            if message.author == self.bot.user:
                return

            if self.channel_id is not None and message.channel.id != self.channel_id:
                return

            user_id = message.author.id
            question = message.content

            messages = self.context_manager.get_context(user_id)
            messages.append({"role": "user", "content": question})

            user_model = self.context_manager.get_user_model(user_id)
            if not user_model:
                user_model = self.default_model

            # Show typing indicator
            async with message.channel.typing():
                try:
                    # Use the async version of chat_completion
                    response_data = await self.api.chat_completion_async(messages, user_model)
                    
                    if response_data and "choices" in response_data:
                        ai_response = response_data["choices"][0]["message"]["content"]
                        
                        # Update the context
                        self.context_manager.update_context(user_id, question, ai_response)
                        
                        # Split the response into chunks based on natural boundaries
                        chunks = self.smart_split_text(ai_response, 1900)  # 1900 to be safe
                        
                        # Send first chunk as a direct reply
                        first_msg = await message.reply(chunks[0])
                        
                        # Send remaining chunks as followups
                        # In your on_message function, replace the for loop with:
                        for chunk in chunks[1:]:
                            await asyncio.sleep(1)  # Avoid rate limiting
                            # Additional safety check
                            if len(chunk) > 2000:
                                sub_chunks = [chunk[i:i+1900] for i in range(0, len(chunk), 1900)]
                                for sub_chunk in sub_chunks:
                                    await message.channel.send(sub_chunk, reference=first_msg)
                                    await asyncio.sleep(0.5)
                            else:
                                await message.channel.send(chunk, reference=first_msg)
                    else:
                        error_message = "An error occurred while processing your request."
                        if response_data and "error" in response_data:
                            error_message = f"Error: {response_data['error'].get('message', 'Unknown error')}"
                        await message.reply(error_message)
                
                except Exception as e:
                    print(f"Error in on_message: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    await message.reply("An error occurred while processing your request. Please try again later.")

    def smart_split_text(self, text, max_length):
        """Split long messages while preserving markdown formatting.
        
        Args:
            text (str): Message content to split
            max_length (int): Discord message character limit
            
        Returns:
            list: Chunked text preserving code blocks and markdown
        """
        """Split text into chunks while preserving markdown and code blocks."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        code_block_open = False
        code_block_lang = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            # Check if adding this paragraph would exceed the limit
            if len(current_chunk) + len(paragraph) + 2 > max_length:
                # If we're in a code block, close it properly
                if code_block_open:
                    current_chunk += "\n```"
                    code_block_open = False
                
                # Add the current chunk to our list
                chunks.append(current_chunk.strip())
                
                # Start a new chunk
                current_chunk = ""
                
                # If we were in a code block and have a language, open a new one
                if code_block_lang:
                    current_chunk = f"```{code_block_lang}\n"
                    code_block_open = True
            
            # Count code block markers in this paragraph
            markers = paragraph.count('```')
            
            # Process code block markers
            if markers > 0:
                # If odd number of markers, this paragraph crosses a code block boundary
                if markers % 2 != 0:
                    code_block_open = not code_block_open
                    
                    # If opening a code block, try to extract the language
                    if code_block_open and '```' in paragraph:
                        marker_pos = paragraph.find('```')
                        # Extract language if specified
                        if marker_pos + 3 < len(paragraph) and paragraph[marker_pos+3:].strip() and not paragraph[marker_pos+3:].startswith('\n'):
                            code_block_lang = paragraph[marker_pos+3:].split('\n')[0].strip()
            
            # The paragraph itself might be too long, need to split it
            if len(paragraph) > max_length:
                # If we have anything in the current chunk, add it first
                if current_chunk:
                    if code_block_open:
                        current_chunk += "\n```"
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    if code_block_lang:
                        current_chunk = f"```{code_block_lang}\n"
                        code_block_open = True
                
                # Split the paragraph into smaller chunks
                words = paragraph.split(' ')
                temp_chunk = ""
                
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > max_length:
                        if code_block_open:
                            temp_chunk += "\n```"
                        chunks.append(temp_chunk.strip())
                        temp_chunk = ""
                        if code_block_open:
                            temp_chunk = f"```{code_block_lang}\n"
                    temp_chunk += word + " "
                
                # Add any remaining content from temp_chunk
                if temp_chunk:
                    current_chunk += temp_chunk
            else:
                # Add the paragraph to the current chunk
                current_chunk += paragraph + "\n\n"
        
        # Add the last chunk if it's not empty
        if current_chunk.strip():
            # If we're still in a code block, close it
            if code_block_open:
                current_chunk += "\n```"
            chunks.append(current_chunk.strip())
        
        # Final verification: ensure no chunk exceeds max_length
        verified_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_length:
                verified_chunks.append(chunk)
            else:
                # If we still have an oversized chunk, force-split it
                for i in range(0, len(chunk), max_length):
                    verified_chunks.append(chunk[i:i+max_length])
        
        return verified_chunks

    def run(self):
        """Start the Discord bot connection."""
        self.bot.run(self.token)
