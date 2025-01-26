# WordCraft - Language Model Training Library

**WordCraft** is a Python library designed to train language models using LSTM (Long Short-Term Memory) networks. It provides utilities to load text data, preprocess it for training, build and train a model, and generate text based on trained models. The library also supports saving and loading models and tokenizers in a zip format.

## Features

- **Data Loading**: Load text data from a file.
- **Preprocessing** (Optional): Preprocess the data by tokenizing and preparing it for training.
- **Model Building** (Optional): Build a customizable LSTM-based language model.
- **Training**: Train the model using the processed data.
- **Text Generation**: Generate text from a trained model based on a seed text.
- **Model Saving & Loading**: Save and load the trained model and tokenizer in a zip file for easy distribution.

## Installation

To use **WordCraft**, install the package via **pip**:

```bash
pip install wordcraft
```

## Usage

### 1. Initialize the Library

```python
from wordcraft import WordCraft

# Create an instance of the WordCraft class
wc = WordCraft()

# Load your text data
wc.load_data("your_text_file.txt")
```

### 2. Optional: Preprocess Data and Build the Model

You can optionally preprocess the data and customize the model architecture before training.

#### Preprocess Data (Optional)
Preprocessing prepares the text data for training by tokenizing it into input-output pairs.

```python
# Optional: Preprocess data and prepare it for training
wc.preprocess_data()
```

#### Build the Model (Optional)
The model can be customized with the following parameters:
- `embedding_dim`: The dimension of the embedding layer.
- `lstm_units`: The number of LSTM units in the model.

You can either use the default model or customize the architecture.

```python
# Optional: Build the model (default or customizable)
wc.build_model(embedding_dim=128, lstm_units=256)
```

### 3. Train the Model

Once the model is built, you can train it on the preprocessed data. Specify the number of epochs and batch size as needed.

```python
# Train the model
wc.train(epochs=10, batch_size=32)
```

### 4. Generate Text

After training the model, you can generate text using a seed phrase.

```python
# Generate text based on a seed text
generated_text = wc.generate_text("Once upon a time", max_length=50)
print(generated_text)
```

### 5. Save and Load the Model

#### Save the Model
You can save the trained model and tokenizer to a zip file.

```python
# Save the model and tokenizer to a zip file
wc.save_model("my_language_model")
```

#### Load the Model
You can load the saved model and tokenizer for further use or text generation.

```python
# Load the saved model and tokenizer from a zip file
wc.load_model("my_language_model")

# Use the model to generate text
generated_text = wc.generate_text("Once upon a time", max_length=50)
print(generated_text)
```

## Example Usage

### 1. Example: Without Preprocessing and Custom Model Building

In this example, we load the data, train the model, and generate text without preprocessing or customizing the model architecture.

```python
from wordcraft import WordCraft

# Create an instance of the WordCraft class
wc = WordCraft()

# Load the text data
wc.load_data("your_text_file.txt")

# Train the model without preprocessing or custom model building
wc.train(epochs=10, batch_size=32)

# Generate text based on a seed
generated_text = wc.generate_text("Once upon a time", max_length=50)
print(generated_text)
```

### 2. Example: With Preprocessing and Custom Model Building

In this example, we preprocess the data, build a custom model, train it, and generate text.

```python
from wordcraft import WordCraft

# Create an instance of the WordCraft class
wc = WordCraft()

# Load the text data
wc.load_data("your_text_file.txt")

# Optional: Preprocess data
wc.preprocess_data()

# Optional: Build the custom model (using different embedding dimensions and LSTM units)
wc.build_model(embedding_dim=256, lstm_units=512)

# Train the model
wc.train(epochs=10, batch_size=32)

# Generate text based on a seed
generated_text = wc.generate_text("In a faraway land", max_length=100)
print(generated_text)
```

## Dataset File Structure

The text file used for training (e.g., `your_text_file.txt`) should contain raw text data. Each line in the file represents a portion of text that the model will learn to predict.

**Example Dataset File Structure**:

```
Once upon a time, in a land far away,
There was a brave knight who ventured into the forest.
The sun was setting, and the sky was painted in hues of orange and pink.
...
```

The library will read the entire text file, split it into tokens (words), and prepare them for training. Ensure that your dataset is large enough to train a meaningful model.

## Requirements

- **Python 3.x**
- **TensorFlow 2.x**
- **NumPy**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to fork the repository and submit pull requests. If you find any bugs or have feature requests, please open an issue.

## Contact

For questions or suggestions, contact me at [bandinvisible8@gmail.com].
