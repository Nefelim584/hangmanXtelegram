import random
import os
import requests
from dotenv import load_dotenv
import json
from mistralai import Mistral

load_dotenv()

# This class shows the hangman pictures.
class HangmanDisplay:
    def __init__(self):
        self.stages = [
            "  _______\n |/      |\n |\n |\n |\n |\n |\n_|___",
            "  _______\n |/      |\n |      (_)\n |\n |\n |\n |\n_|___",
            "  _______\n |/      |\n |      (_)\n |       |\n |       |\n |\n |\n_|___",
            "  _______\n |/      |\n |      (_)\n |      \\|\n |       |\n |\n |\n_|___",
            "  _______\n |/      |\n |      (_)\n |      \\|/\n |       |\n |\n |\n_|___",
            "  _______\n |/      |\n |      (_)\n |      \\|/\n |       |\n |      /\n |\n_|___",
            "  _______\n |/      |\n |      (_)\n |      \\|/\n |       |\n |      / \\\n |\n_|___"
        ]

    def get_stage(self, attempts_left, max_attempts):
        index = max_attempts - attempts_left
        if index >= len(self.stages):
            index = len(self.stages) - 1
        return self.stages[index]

# This class handles one round of Hangman.
class HangmanRound:
    def __init__(self, secret_word, max_attempts, display):
        self.secret_word = secret_word.lower()
        self.max_attempts = max_attempts
        self.attempts_left = max_attempts
        self.guessed_letters = []
        self.wrong_guesses = []
        self.display = display

    # Show the word with "_" for letters not guessed.
    def display_word(self):
        return " ".join(letter if letter in self.guessed_letters else "_" for letter in self.secret_word)

    # Guess one letter.
    def guess_letter(self, letter):
        letter = letter.lower()
        if letter in self.guessed_letters or letter in self.wrong_guesses:
            print("You already guessed that letter.")
            return False

        if letter in self.secret_word:
            self.guessed_letters.append(letter)
            print("Good guess!")
            return True
        else:
            self.wrong_guesses.append(letter)
            self.attempts_left -= 1
            print("Wrong guess!")
            return False

    # Try to guess the whole word.
    def guess_full_word(self, guess):
        guess = guess.lower()
        if guess == self.secret_word:
            self.guessed_letters = list(set(self.secret_word))
            return True
        else:
            self.attempts_left -= 1
            print("Incorrect guess for the whole word!")
            return False

    # Check if the player has guessed all letters.
    def is_won(self):
        return all(letter in self.guessed_letters for letter in self.secret_word)

    # Check if no attempts left.
    def is_lost(self):
        return self.attempts_left <= 0

    # Show the current status.
    def get_status(self):
        art = self.display.get_stage(self.attempts_left, self.max_attempts)
        word_prog = self.display_word()
        wrongs = " ".join(self.wrong_guesses)
        return f"{art}\nWord: {word_prog}\nWrong: {wrongs}\nAttempts left: {self.attempts_left}\n"


# This class manages the whole game with many rounds.
class HangmanGame:
    def __init__(self, word_list):
        self.word_list = word_list[:]  # make a copy of the word list
        self.remaining_words = list(self.word_list)  # words not used yet
        self.score = 0
        self.display = HangmanDisplay()

    # Play one round of Hangman.
    def play_round(self):
        if not self.remaining_words:
            print("No more words left!")
            return False

        secret_word = random.choice(self.remaining_words)
        self.remaining_words.remove(secret_word)

        # Calculate attempts based on the number of different letters.
        attempts_for_round = max(6, len(set(secret_word)) + 2)

        round_game = HangmanRound(secret_word, attempts_for_round, self.display)
        print("\n--- New Round ---")
        while not round_game.is_won() and not round_game.is_lost():
            print(round_game.get_status())
            user_input = input("Enter a letter or type 'guess' for full word: ").strip()
            if user_input.lower() == "guess":
                full_guess = input("Enter your guess for the word: ").strip()
                if round_game.guess_full_word(full_guess):
                    print("Correct! You guessed the word!")
                    break
                else:
                    print("Wrong guess!")
            elif len(user_input) == 1 and user_input.isalpha():
                round_game.guess_letter(user_input)
            else:
                print("Invalid input.")

        if round_game.is_won():
            bonus = round_game.attempts_left * 10
            self.score += bonus
            print(f"\nYou won! The word was: {round_game.secret_word}")
            print(f"You get {bonus} bonus points.")
        else:
            print(round_game.get_status())
            print(f"\nYou lost! The word was: {round_game.secret_word}")
        print(f"Total Score: {self.score}\n")
        return True

    # Start the game with many rounds.
    def play(self):
        global rounds
        print("Welcome to Hangman!")
        rounds_input = input("How many rounds do you want to play? ")
        try:
            rounds = int(rounds_input)
        except ValueError:
            rounds = 1

        for i in range(rounds):
            print(f"\nRound {i+1}")
            if not self.play_round():
                break

        print(f"Final Score: {self.score}")
        print("Thanks for playing!")



def generate_words_from_mistral(num_words):
    """
    Generate a list of words using the Mistral 7B API.
    The function uses the MISTRAL_API_KEY environment variable.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Mistral API key not set. Falling back to default words.")
        return []

    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides words for a Hangman game."},
        {"role": "user", "content": f"Generate exactly {num_words} unique, lower-case, single words, separated by commas. Respond only with the words and nothing more. Do not include any additional text."}
    ]

    try:
        chat_response = client.chat.complete(model=model, messages=messages)
        content = chat_response.choices[0].message.content.strip()
        print("API Response Content:", content)  # Debugging line

        # Extract words and filter out any non-word content
        words = [word.strip() for word in content.split(",") if word.strip().isalpha()]
        words = words[:num_words]  # Limit to the requested number of words
        print("Parsed Words:", words, num_words, len(words))  # Debugging line

        # if len(words) != num_words:
        #     print("Unexpected number of words generated. Using default words.")
        #     return []
        return words
    except Exception as e:
        print("Error generating words from Mistral:", e)
        return []

def main():
    # Try to generate a list of words with Mistral
    generated_words = generate_words_from_mistral(50)  # Request more words at once
    if generated_words:
        word_list = generated_words
    # else:
    #     # Fallback: hard-coded word list.
    #     word_list = [
    #         # Technology
    #         "python", "programming", "algorithm", "compiler", "debugging", "encryption", "server", "cloud", "network", "database",
    #         # Nature
    #         "forest", "ocean", "mountain", "desert", "volcano", "rainforest", "glacier", "river", "canyon", "waterfall",
    #         # History
    #         "revolution", "empire", "renaissance", "medieval", "civilization", "pharaoh", "dynasty", "treaty", "invasion", "monarchy",
    #         # Sports
    #         "soccer", "basketball", "tennis", "cricket", "baseball", "hockey", "golf", "rugby", "swimming", "cycling",
    #         # Food
    #         "pizza", "sushi", "burger", "pasta", "salad", "steak", "curry", "taco", "dumpling", "sandwich",
    #         # Art
    #         "painting", "sculpture", "theater", "cinema", "dance", "music", "literature", "poetry", "photography", "architecture",
    #         # Science
    #         "physics", "chemistry", "biology", "astronomy", "geology", "ecology", "evolution", "genetics", "robotics", "quantum",
    #         # Miscellaneous
    #         "philosophy", "economics", "psychology", "sociology", "law", "education", "medicine", "innovation", "strategy", "venture"
    #     ]

    game = HangmanGame(word_list)
    game.play()

if __name__ == "__main__":
    main()