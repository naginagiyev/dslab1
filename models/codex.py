import os
from openai import OpenAI
from paths import promptsDir
from dotenv import load_dotenv
from schemas import ReasoningResult

class CodexModel:
    def __init__(self, model: str = "gpt-4.1-mini"):
        load_dotenv()
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open(promptsDir / "codexcodeprompt.md", "r", encoding="utf-8") as f:
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

    def reason(self, error_output: str) -> ReasoningResult:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": self._reason_prompt},
                {"role": "user", "content": error_output},
            ],
            response_format=ReasoningResult,
        )
        return completion.choices[0].message.parsed