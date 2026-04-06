import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI
from dotenv import load_dotenv
from path import promptsDir

class CodexModel:
    def __init__(self, model: str = "gpt-4.1-mini"):
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open(promptsDir / "codecodeprompt.md", "r", encoding="utf-8") as f:
            self._code_prompt = f.read()
        with open(promptsDir / "codexreasoningprompt.md", "r", encoding="utf-8") as f:
            self._reason_prompt = f.read()

    def code(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._code_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content.strip()

    def reason(self, error_output: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._reason_prompt},
                {"role": "user", "content": error_output},
            ],
        )
        return completion.choices[0].message.content.strip()