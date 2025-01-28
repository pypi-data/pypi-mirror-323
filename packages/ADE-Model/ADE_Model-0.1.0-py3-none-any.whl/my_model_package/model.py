import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import os

class ADEModel:
    def __init__(self, model_dir=None):
        """
        Initialize the ADE model with the specified directory.
        """
        # Use the default local model directory if none is provided
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), "../ade_model")
        self.model = TFAutoModelForSequenceClassification.from_pretrained(self.model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)

    def predict(self, text):
        """
        Predict if a given text mentions an Adverse Drug Event (ADE).

        Args:
            text (str): Input text.

        Returns:
            str: "Related" or "Not Related"
        """
        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="tf", truncation=True, padding=True, max_length=128)

        # Perform prediction
        logits = self.model.predict(dict(inputs)).logits
        predicted_class = tf.argmax(logits, axis=1).numpy()[0]

        # Map prediction to class labels
        labels = {0: "Not Related", 1: "Related"}
        return labels[predicted_class]


if __name__ == "__main__":
    # Create an instance of the ADEModel
    ade_model = ADEModel()

    # Example input text
    sample_text = "The patient experienced severe headaches after taking Drug X."

    # Perform prediction
    prediction = ade_model.predict(sample_text)
    print(f"Prediction: {prediction}")
