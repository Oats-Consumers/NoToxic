from datetime import datetime, timedelta, timezone
import requests

from clients.PromptBuilder import PromptBuilder
from my_secrets import OPENAI_API_KEY
from openai import OpenAI


class OpenAIClient:

    def __init__(self, api_key=OPENAI_API_KEY, model="gpt-4o"):
        self.model = model
        self.api_key = api_key
        self.__client = OpenAI(api_key=self.api_key)

    def __chat(self, prompt):
        response = self.__client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content


    def check_is_english_text(self, text):
        try:
            prompt = PromptBuilder.LanguageCheckPrompt().build_is_english_prompt(text)
            result = self.__chat(prompt).strip().lower()
            return result.startswith("yes")
        except Exception as e:
            print(f"⚠️ Language check failed: {e}")
            return True

    def label_entry(self, entry):
        prompt = PromptBuilder.LabelDataPrompt().build_label_data_prompt(entry)
        try:
            return self.__chat(prompt).strip().upper()
        except Exception as e:
            raise e
