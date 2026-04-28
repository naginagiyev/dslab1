import os
import json
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
        with open(promptsDir / "codexfixprompt.md", "r", encoding="utf-8") as f:
            self._fix_prompt = f.read()

    def code(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._code_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content.strip()

    def fixCode(self, code: str, problem: str) -> str:
        user_message = f"### Original Code\n{code}\n\n### Problem\n{problem}"
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._fix_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return completion.choices[0].message.content.strip()

    def reason(self, systemPrompt: str, userContent: str) -> ReasoningResult:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userContent},
            ],
            response_format=ReasoningResult,
        )
        return completion.choices[0].message.parsed
    
    def enhance(self, systemPrompt: str, userContent: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userContent},
            ],
        )
        return completion.choices[0].message.content
    
    def tuneParameters(self, currentCode: str, changes: str) -> str:
        prompt = (
            f"{self._code_prompt}\n\n"
            "Additional constraints:\n"
            "1. Return the full updated Python code.\n"
            "2. Only change parameter values in the existing training pipeline.\n"
            "3. Do not change model architecture, imports, data flow, preprocessing steps, function definitions, or file structure.\n"
            "4. Keep all non-parameter code exactly as is.\n"
        )
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": currentCode},
                {"role": "user", "content": changes},
            ],
        )
        return completion.choices[0].message.content

    def suggestParameters(self, systemPrompt: str, userContent: str) -> dict:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userContent},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(completion.choices[0].message.content)