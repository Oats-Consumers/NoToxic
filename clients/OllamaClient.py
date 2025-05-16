import requests
import json

from clients.PromptBuilder import PromptBuilder


class OllamaClient:
    def __init__(self, model_name="gemma3:27b", ollama_url="http://localhost:11434/api/generate"):
        """
        Initializes the OllamaClient to connect with the local Ollama server.
        :param model_name: The model you wish to use with Ollama (e.g., "gemma3:27b").
        :param ollama_url: URL to the local Ollama instance (default is localhost on port 11434).
        """
        self.model_name = model_name
        self.ollama_url = ollama_url

    def chat(self, prompt, temperature=0, top_p=0.9, n=10):
        """
        Sends a prompt to the Ollama model with specified options and receives a response.
        :param prompt: The input text you want to send to the model.
        :param temperature: Sampling temperature for randomness in output (0.0 to 1.0).
        :param max_tokens: Maximum number of tokens for the response.
        :param top_p: Top-p sampling (nucleus sampling).
        :param n: Number of responses to generate.
        :return: The model's response text.
        """

        # Send the request to Ollama API
        try:
            r = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": n,
                        "stop": ["\n"],
                    },
                },
                timeout=300,
            )
            r.raise_for_status()
            answer = r.json()["response"]
            return answer
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return None

    def check_is_english_text(self, text):
        print(f"Checking using Ollama if text is English: {text}")
        try:
            prompt = PromptBuilder.LanguageCheckPrompt().build_is_english_prompt(text)
            result = self.chat(prompt).strip().lower()
            return result.startswith("yes")
        except Exception as e:
            print(f"⚠️ Language check failed: {e}")
            return True

    def label_entry(self, entry):
        prompt = PromptBuilder.LabelDataPrompt().build_label_data_prompt(entry)
        try:
            return self.chat(prompt).strip().upper()
        except Exception as e:
            raise e
