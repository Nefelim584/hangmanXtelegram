from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import os
import json
from dotenv import load_dotenv
from hangsman_botV import HangmanGame, generate_words_from_mistral  # Import from hangsman_botV

load_dotenv()

# Define states for the conversation
DIFFICULTY, ROUNDS, PLAYING, ASK_RESTART = range(4)

LEADERBOARD_FILE = "leaderboard.json"

# Function to read the leaderboard from the JSON file
def read_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to write the leaderboard to the JSON file
def write_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file)

# Start command handler
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [
            InlineKeyboardButton("Easy", callback_data='easy'),
            InlineKeyboardButton("Medium", callback_data='medium'),
            InlineKeyboardButton("Hard", callback_data='hard')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a difficulty level:", reply_markup=reply_markup)
    return DIFFICULTY

# Difficulty handler
async def difficulty(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    difficulty_level = query.data
    context.user_data['difficulty'] = difficulty_level

    await query.edit_message_text("How many rounds do you want to play?")
    return ROUNDS

# Rounds handler
async def rounds(update: Update, context: CallbackContext) -> int:
    rounds_input = update.message.text
    try:
        rounds = int(rounds_input)
    except ValueError:
        rounds = 1

    context.user_data['rounds'] = rounds

    # Generate words for the game
    generated_words = generate_words_from_mistral(50)  # Request more words at once
    if generated_words:
        word_list = generated_words
    else:
        word_list = [
            # Technology
            "python", "programming", "algorithm", "compiler", "debugging", "encryption", "server", "cloud", "network", "database",
            # Nature
            "forest", "ocean", "mountain", "desert", "volcano", "rainforest", "glacier", "river", "canyon", "waterfall",
            # History
            "revolution", "empire", "renaissance", "medieval", "civilization", "pharaoh", "dynasty", "treaty", "invasion", "monarchy",
            # Sports
            "soccer", "basketball", "tennis", "cricket", "baseball", "hockey", "golf", "rugby", "swimming", "cycling",
            # Food
            "pizza", "sushi", "burger", "pasta", "salad", "steak", "curry", "taco", "dumpling", "sandwich",
            # Art
            "painting", "sculpture", "theater", "cinema", "dance", "music", "literature", "poetry", "photography", "architecture",
            # Science
            "physics", "chemistry", "biology", "astronomy", "geology", "ecology", "evolution", "genetics", "robotics", "quantum",
            # Miscellaneous
            "philosophy", "economics", "psychology", "sociology", "law", "education", "medicine", "innovation", "strategy", "venture"
        ]

    difficulty = context.user_data['difficulty']
    if difficulty == 'easy':
        word_list = [word for word in word_list if len(word) <= 6]
    elif difficulty == 'medium':
        word_list = [word for word in word_list if len(word) <= 10]
    elif difficulty == 'hard':
        word_list = [word for word in word_list if len(word) <= 15]

    context.user_data['game'] = HangmanGame(word_list)
    context.user_data['current_round'] = 0

    await update.message.reply_text(f"Starting the game with {rounds} rounds. Let's begin!")
    await update.message.reply_text(context.user_data['game'].start_new_round())
    return PLAYING

# Playing handler
async def playing(update: Update, context: CallbackContext) -> int:
    game = context.user_data['game']
    user_input = update.message.text.strip()

    response = game.handle_guess(user_input)
    await update.message.reply_text(response)

    if game.current_round.is_won() or game.current_round.is_lost():
        context.user_data['current_round'] += 1
        if context.user_data['current_round'] < context.user_data['rounds']:
            await update.message.reply_text(game.start_new_round())
        else:
            user = update.message.from_user
            leaderboard = read_leaderboard()
            leaderboard[user.username] = max(leaderboard.get(user.username, 0), game.score)
            write_leaderboard(leaderboard)

            keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data='yes'),
                    InlineKeyboardButton("No", callback_data='no')
                ],
                [
                    InlineKeyboardButton("View Leaderboard", callback_data='leaderboard')
                ],
                [
                    InlineKeyboardButton("Change Difficulty", callback_data='change_difficulty')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Game over! Final Score: {game.score}\nDo you want to start a new game?", reply_markup=reply_markup)
            return ASK_RESTART

    return PLAYING

# Ask restart handler
async def ask_restart(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_input = query.data

    if user_input == 'yes':
        await query.edit_message_text("How many rounds do you want to play?")
        return ROUNDS
    elif user_input == 'leaderboard':
        leaderboard = read_leaderboard()
        if not leaderboard:
            await query.edit_message_text("No scores yet.")
            return ConversationHandler.END

        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        leaderboard_text = "\n".join([f"{user}: {score}" for user, score in sorted_leaderboard])
        await query.edit_message_text(f"Leaderboard:\n{leaderboard_text}")
        return ConversationHandler.END
    elif user_input == 'change_difficulty':
        keyboard = [
            [
                InlineKeyboardButton("Easy", callback_data='easy'),
                InlineKeyboardButton("Medium", callback_data='medium'),
                InlineKeyboardButton("Hard", callback_data='hard')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose a difficulty level:", reply_markup=reply_markup)
        return DIFFICULTY
    else:
        await query.edit_message_text("Thank you for playing! Goodbye!")
        return ConversationHandler.END

# Cancel command handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Game canceled.")
    return ConversationHandler.END

# Leaderboard command handler
async def leaderboard(update: Update, context: CallbackContext) -> None:
    leaderboard = read_leaderboard()
    if not leaderboard:
        await update.message.reply_text("No scores yet.")
        return

    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "\n".join([f"{user}: {score}" for user, score in sorted_leaderboard])
    await update.message.reply_text(f"Leaderboard:\n{leaderboard_text}")

def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add conversation handler with the states DIFFICULTY, ROUNDS, PLAYING, and ASK_RESTART
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DIFFICULTY: [CallbackQueryHandler(difficulty)],
            ROUNDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, rounds)],
            PLAYING: [MessageHandler(filters.TEXT & ~filters.COMMAND, playing)],
            ASK_RESTART: [CallbackQueryHandler(ask_restart)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('leaderboard', leaderboard))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()