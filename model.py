import csv
import os
import random
import json
import logging
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# File Paths
csv_filename = "messages.csv"
model_filename = "word_model.json"

# Store word relationships (bigrams and unigrams)
word_following = defaultdict(lambda: defaultdict(int))
single_word_following = defaultdict(lambda: defaultdict(int))

def save_model():
    """Save word relationships to JSON."""
    try:
        with open(model_filename, "w", encoding="utf-8") as f:
            json.dump({
                "bigrams": {k: dict(v) for k, v in word_following.items()},
                "unigrams": {k: dict(v) for k, v in single_word_following.items()}
            }, f)
        logging.info("Model saved successfully.")
    except Exception as e:
        logging.error(f"Error saving model: {e}")

def load_model():
    """Load word relationships from JSON."""
    global word_following, single_word_following
    if os.path.exists(model_filename):
        try:
            with open(model_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                word_following = defaultdict(lambda: defaultdict(int), {k: defaultdict(int, v) for k, v in data.get("bigrams", {})})
                single_word_following = defaultdict(lambda: defaultdict(int), {k: defaultdict(int, v) for k, v in data.get("unigrams", {})})
            logging.info("Model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model: {e}")

def update_pairs():
    """Update word relationships from messages.csv."""
    if not os.path.exists(csv_filename):
        return

    try:
        with open(csv_filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header if present
            for row in reader:
                if row:
                    words = row[0].lower().split()
                    for i in range(len(words) - 2):  # Bigrams
                        pair = f"{words[i]} {words[i + 1]}"
                        word_following[pair][words[i + 2]] += 1
                    for i in range(len(words) - 1):  # Unigrams
                        single_word_following[words[i]][words[i + 1]] += 1
        save_model()
    except Exception as e:
        logging.error(f"Error updating word pairs: {e}")

def likely_next(content):
    """Predict the next word using bigrams first, then unigrams as a fallback."""
    words = content.lower().split()

    # Use Bigram model if enough context exists
    if len(words) >= 2:
        last_pair = f"{words[-2]} {words[-1]}"
        if last_pair in word_following:
            next_word_choices = word_following[last_pair]
            if next_word_choices:
                next_words = list(next_word_choices.keys())
                weights = list(next_word_choices.values())
                return random.choices(next_words, weights=weights, k=1)[0]

    # Fallback to Unigram model
    if words[-1] in single_word_following:
        next_word_choices = single_word_following[words[-1]]
        if next_word_choices:
            next_words = list(next_word_choices.keys())
            weights = list(next_word_choices.values())
            return random.choices(next_words, weights=weights, k=1)[0]

    return None

def generate_sentence(start_text, depth=12):
    """Recursively generate a phrase using bigrams with unigram fallback."""
    for _ in range(depth):
        next_word = likely_next(start_text)
        if not next_word:
            break
        start_text += f" {next_word}"

        # 30% chance to stop early for more variation
        if next_word.endswith((".", "!", "?")) and random.random() < 0.3:
            break

    return start_text

def update_model(content):
    """if new messages are made, add them to the csv file"""
    try:
        with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([content])

        words = content.lower().split()
        for i in range(len(words) - 2):  # Store bigram pairs
            pair = f"{words[i]} {words[i + 1]}"
            word_following[pair][words[i + 2]] += 1
        for i in range(len(words) - 1):  # Store unigram pairs
            single_word_following[words[i]][words[i + 1]] += 1
        save_model()
    except Exception as e:
        logging.error(f"Error processing message: {e}")
