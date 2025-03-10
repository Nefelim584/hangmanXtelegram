# Hangman Telegram Bot

A Telegram bot that lets users play the classic Hangman game. The bot is built using Python and the `python-telegram-bot` library, also it uses Mistral API for words generation.
Bot is availible in Telegram messenger by the name - @Hangman_Ai_Bot. 
## Features
- Play the classic Hangman game directly in Telegram.
- Supports different difficulty levels.
- Tracks user scores and maintains a leaderboard.
- Interactive bot using inline keyboards.
- Asynchronous execution for efficient performance.


## File Structure
- `hangman.py` - Pure console game.
- `hangman_botV.py` - Version of the game updated for integration with Telegram API.
- `bot_main.py` - Telegram Bot.
- `leaderbord.json` - Example of leaderboard.

## How It Works

### `hangman_botV.py` 
- Implements the **HangmanGame** class.
- Works with Mistral API for words generation.

### `bot_main.py` (Telegram Bot)
- Uses the `python-telegram-bot` library to handle user interactions.
- Listens for commands like `/start` or `/leaderboard`.
- Stores user progress using `context.user_data`.

#### Bot logic
![bot_execution_flow](https://github.com/user-attachments/assets/392ac35f-d272-40f8-8b9f-64eb919f55a7)



## Contributing
Pull requests are welcome! Feel free to suggest improvements or new features.

## License
This project is licensed under the MIT License.

