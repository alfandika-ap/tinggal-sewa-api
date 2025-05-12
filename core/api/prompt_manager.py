import os

from dotenv import load_dotenv
from openai import OpenAI

import json

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=API_KEY)


class PromptManager:
    def __init__(self, model="gpt-4o-mini", messages=[]):
        self.model = model
        self.messages = messages

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def add_messages(self, messages):
        self.messages.extend(messages)

    def set_messages(selft, messages):
        selft.messages = messages

    def get_prompt(self):
        return {"model": self.model, "messages": self.messages}

    def generate(self, stream=False):
        response = openai_client.chat.completions.create(
            model=self.model, messages=self.messages, stream=stream
        )

        if stream:
            return response
        else:
            content = response.choices[0].message.content
            return content

    def generate_structured(self, schema):
        response = openai_client.beta.chat.completions.parse(
            model=self.model, messages=self.messages, response_format=schema
        )

        result = response.choices[0].message.model_dump()
        content = json.loads(result["content"])
        return content
