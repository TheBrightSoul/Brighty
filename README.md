# Brighty: AI-Powered Discord Assistant

Brighty is an advanced Discord bot leveraging OpenRouter's API for intelligent conversations. Built with Python 3.10+ and discord.py, it features robust context management and model customization.

![Brighty in Action](/images/showcase.png)

## About This Fork

Hello! I have modified this project according to my needs and kind of renamed it to Brighty from Sora as I like to call it.

### Modifications:

1. I wanted to get larger responses from AI which were getting ignored in the original bot, and they were producing errors in the console. I have tried three different ideas to catch large messages (messages larger than 2000 characters) as Discord has a message character limit of 2000 characters, and the best one I found is to split the messages into smaller chunks and send them one by one. To implement this, I had to make some of the functions asynchronous, so I did that.

2. I have changed the default model to a free model so that it doesn't burn up any credits at the initial launch.

3. After making the changes, I tried to add documentation and comments, but that wasn't enough, so I used AI to add comments and regenerated the README file, where there might be some mistakes (as it is AI-generated).

4. **Realization**: I realized that I made the code even messier, so I tried to clean up as much as I could. For now, this is working and doesn't look that messy if you look carefully. But if there are any bugs or anything like that, feel free to open issues.

5. I fixed the login screen text.

6. I want to thank the original creator for making this project, as it would have taken me so long to do this from scratch. Here is the link to the original repo: [Original Repo](https://github.com/mintsuku/sora)

## Key Features

- **Conversation Continuity**  
  Multi-turn context tracking with automatic history management
- **Model Flexibility**  
  Supports 50+ OpenRouter models with per-user preferences
- **Admin Controls**  
  Channel restrictions, model whitelisting, and usage analytics
- **Error Resiliency**  
  Automatic retries, timeouts, and error handling
- **Message Splitting**  
  Smart text chunking preserving markdown formatting

![Brighty in Action](/images/showcase.png)

## Project Structure

```
Brighty/
├── api/
│   ├── openrouter.py       # OpenRouter API client with async/sync support
│   └── context_manager.py  # User context and preferences storage
├── bot/
│   ├── sora.py             # Main bot implementation
│   └── ui.py               # Embed builders and interface components
├── config/
│   └── default_settings.py # Configuration constants
└── main.py                 # Entry point
```

## Installation

### 1. Clone repo & create virtual environment

It is **recommended** to create a virtual environment using Python 3.11.9 or lower, as the bot does not work properly on Python 3.12.

```bash
git clone https://github.com/TheBrightSoul/Brighty.git
cd sora
python -m venv venv  # Create virtual environment
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
```ini
DISCORD_TOKEN=your_bot_token
OPENROUTER_KEY=your_api_key
DEFAULT_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
LOG_LEVEL=INFO
```

### 4. Start the bot
```bash
python main.py
```

![Bot Startup](/images/startup.png)

## Command Reference

### User Commands
| Command | Description | Example |
|---------|-------------|---------|
| `/chat [message]` | Start/maintain conversation | `/chat What's quantum computing?` |
| `/models` | Browse available AI models | `/models` |
| `/model set [id]` | Change your AI model | `/model set meta-llama/llama-3-70b-instruct:nitro` |
| `/context clear` | Reset conversation history | `/context clear` |

### Admin Commands
| Command | Description | Parameters |
|---------|-------------|------------|
| `/admin set_default_model` | Set server-wide default model | `model_id` |
| `/admin toggle_model_access` | Enable/disable model switching | `[true/false]` |
| `/admin set_timeout` | Configure response timeout | `seconds` |
| `/admin usage_stats` | Show interaction analytics | `[user_id]` |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

