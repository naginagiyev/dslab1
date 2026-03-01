import os
from openai import OpenAI
from dotenv import load_dotenv

class GenerationModel:
    def __init__(self, system_prompt: str, model: str = "gpt-4.1-mini"):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = system_prompt
        self.model = model

    def generate(self, query: str, history: list = None, structure=None):
        messages = [{"role": "system", "content": self.system_prompt}]

        if history:
            for item in history:
                messages.append({"role": "user", "content": item["user"]})
                messages.append({"role": "assistant", "content": item["assistant"]})

        messages.append({"role": "user", "content": query})

        if structure is not None:
            completion = self.client.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=structure,
            )
            return completion.choices[0].message.parsed
        else:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return completion.choices[0].message.content