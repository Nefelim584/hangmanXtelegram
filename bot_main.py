from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import os
from dotenv import load_dotenv
from hangsman_botV import HangmanGame, generate_words_from_mistral  # Import from hangsman_botV

load_dotenv()

# Define states for the conversation
ROUNDS, PLAYING = range(2)

# Start command handler
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Welcome to Hangman! How many rounds do you want to play?"
    )
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
    generated_words = generate_words_from_mistral(rounds)
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
            await update.message.reply_text(f"Game over! Final Score: {game.score}")
            return ConversationHandler.END

    return PLAYING

# Cancel command handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Game canceled.")
    return ConversationHandler.END

def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add conversation handler with the states ROUNDS and PLAYING
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ROUNDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, rounds)],
            PLAYING: [MessageHandler(filters.TEXT & ~filters.COMMAND, playing)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()