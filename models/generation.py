import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

class GenerationModel:
    def __init__(self, systemPrompt: str | Path, model: str = "gpt-4.1-mini", responseFormat=None):
        load_dotenv()
        self.model = model
        with open(systemPrompt, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.response_format = responseFormat

    def generate(self, query: str, history: list = None):
        messages = [{"role": "system", "content": self.system_prompt}]
        if history:
            for item in history:
                messages.append({"role": "user", "content": item["user"]})
                messages.append({"role": "assistant", "content": item["assistant"]})
        messages.append({"role": "user", "content": query})
        if self.response_format is not None:
            completion = self.client.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=self.response_format,
            )
            return completion.choices[0].message.parsed
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return completion.choices[0].message.content