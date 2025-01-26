import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import pad_sequences
from tensorflow.keras.models import Sequential, load_model as keras_load_model
from tensorflow.keras.layers import Embedding, LSTM, Dense
import pickle
import os
import zipfile

class WordCraft:
    def __init__(self):
        self.tokenizer = None
        self.vocab_size = None
        self.max_seq_length = None
        self.model = None
        self.text_data = None

    def load_data(self, file_path):
        """Loads the dataset from a .txt file."""
        with open(file_path, "r") as f:
            self.text_data = f.read().splitlines()

    def preprocess_data(self):
        """Tokenizes and prepares input-output pairs for language modeling."""
        if not self.text_data:
            raise ValueError("Data not loaded. Please call load_data() first.")

        # Tokenize text
        self.tokenizer = Tokenizer()
        self.tokenizer.fit_on_texts(self.text_data)

        # Convert text to sequences of integers
        sequences = self.tokenizer.texts_to_sequences(self.text_data)
        self.vocab_size = len(self.tokenizer.word_index) + 1

        # Prepare input-output pairs for language modeling
        input_sequences = []
        for seq in sequences:
            for i in range(1, len(seq)):
                n_gram_sequence = seq[:i+1]
                input_sequences.append(n_gram_sequence)

        # Pad sequences
        self.max_seq_length = max(len(seq) for seq in input_sequences)
        input_sequences = pad_sequences(input_sequences, maxlen=self.max_seq_length, padding="pre")

        # Split into inputs (X) and outputs (y)
        self.X = input_sequences[:, :-1]
        y = input_sequences[:, -1]

        # Convert targets to categorical
        self.y = tf.keras.utils.to_categorical(y, num_classes=self.vocab_size)

    def build_model(self, embedding_dim=128, lstm_units=256):
        """Defines and compiles the language model."""
        if self.model is not None:
            print("Model is already built.")
            return

        self.model = Sequential([
            Embedding(input_dim=self.vocab_size, output_dim=embedding_dim, input_length=self.max_seq_length-1),
            LSTM(units=lstm_units),
            Dense(units=self.vocab_size, activation="softmax")
        ])

        self.model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    def train(self, epochs=10, batch_size=32):
        """Trains the language model."""
        if self.text_data is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

        self.preprocess_data()
        if self.model is None:
            self.build_model()

        self.model.fit(self.X, self.y, batch_size=batch_size, epochs=epochs, verbose=1)

    def save_model(self, base_name):
        """Saves the trained model and tokenizer to a zip file."""
        if self.model is None:
            raise ValueError("Model is not built. Please call build_model() and train the model first.")

        model_path = base_name + ".h5"
        tokenizer_path = base_name + "_tokenizer.pkl"

        # Save the model
        self.model.save(model_path)
        print(f"Model saved to {model_path}")

        # Save the tokenizer
        with open(tokenizer_path, "wb") as f:
            pickle.dump(self.tokenizer, f)
        print(f"Tokenizer saved to {tokenizer_path}")

        # Create a zip file containing the model and tokenizer
        with zipfile.ZipFile(base_name + ".zip", 'w') as zipf:
            zipf.write(model_path, os.path.basename(model_path))
            zipf.write(tokenizer_path, os.path.basename(tokenizer_path))

        # Remove the saved model and tokenizer files after zipping
        os.remove(model_path)
        os.remove(tokenizer_path)
        print(f"Model and tokenizer zipped and saved as {base_name}.zip")

    def load_model(self, base_name):
        """Loads a trained model and tokenizer from a zip file."""
        zip_path = base_name + ".zip"

        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Zip file not found at {zip_path}")

        # Unzip the files into a directory named `base_name`
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(base_name)

        model_path = os.path.join(base_name, base_name + ".h5")
        tokenizer_path = os.path.join(base_name, base_name + "_tokenizer.pkl")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        if not os.path.exists(tokenizer_path):
            raise FileNotFoundError(f"Tokenizer file not found at {tokenizer_path}")

        # Load the model
        self.model = keras_load_model(model_path)
        print(f"Model loaded from {model_path}")

        # Load the tokenizer
        with open(tokenizer_path, "rb") as f:
            self.tokenizer = pickle.load(f)
        print(f"Tokenizer loaded from {tokenizer_path}")

        # Clean up extracted files
        os.remove(model_path)
        os.remove(tokenizer_path)

    def generate_text(self, seed_text, max_length=10):
        """Generates text using the trained model."""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model or tokenizer not loaded. Please call load_model() first.")

        for _ in range(max_length):
            # Tokenize the seed text
            token_list = self.tokenizer.texts_to_sequences([seed_text])[0]
            token_list = pad_sequences([token_list], maxlen=self.max_seq_length-1, padding="pre")

            # Predict the next word
            predicted_probs = self.model.predict(token_list, verbose=0)
            predicted_index = np.argmax(predicted_probs[0])

            # Convert predicted index to word
            output_word = self.tokenizer.index_word.get(predicted_index, "")
            if not output_word:  # Stop if no valid word is predicted
                break

            # Append the predicted word to the seed text
            seed_text += " " + output_word

        return seed_text
