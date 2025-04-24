from clients.PromptBuilder import PromptBuilder
from my_secrets import OPENAI_API_KEY
from openai import OpenAI


class OpenAIClient:
    __api_key = ""
    model = ""

    def __init__(self, api_key = OPENAI_API_KEY, model = "gpt-4o"):
        self.model = model
        self.api_key = api_key


    __client = OpenAI(api_key=OPENAI_API_KEY)

    def check_is_english_text(self, text):
        try:
            prompt = PromptBuilder.LanguageCheckPrompt().build_is_english_prompt(text)
            response = self.__client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            result = response.choices[0].message.content.strip().lower()
            return result.startswith("yes")
        except Exception as e:
            print(f"⚠️ Language check failed: {e}")
            return True

    def label_entry(self, entry):
        prompt = PromptBuilder.LabelDataPrompt().build_label_data_prompt(entry)
        response = self.__client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip().upper()
