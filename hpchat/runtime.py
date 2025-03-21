#!/usr/bin/env python3
import os
import llm
import fire
import yaml
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel
from hpchat import db

class Runtime():
    def __init__(self, config_file="config.yaml"):
        self.root_path = Path(__file__).parent.parent
        self.config = self.read_config(config_file)
        self.runtime_model = self.config.get("runtime_model", None)
        
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            with open(os.path.expanduser("~/.ssh/openai_api_key.txt"), "r") as f:
                openai_api_key = f.read().strip()

        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable")
        
        self.oai_client = OpenAI(api_key=openai_api_key)
        self.openai_api_key = openai_api_key

        self.sermons_path = self.root_path / "sermons"
        Path(self.sermons_path).mkdir(exist_ok=True)
        
        self.media_path = self.root_path / "media"
        Path(self.media_path).mkdir(exist_ok=True)

        self.sermon_list_path = self.sermons_path / "sermon_list.yaml"
        pass

    def read_config(self, config_file):
        """ Reads config.yaml from local path and returns it as a dictionary"""
        script_dir = self.root_path
        config_path = script_dir / 'config.yaml'
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        return config
    
    @property
    def system_prompt(self):
        return self.config.get("system_prompt", "")

    def parse_object(self, prompt: str, format: BaseModel, system_prompt: str = None):
        """Parse the object using the OpenAI API"""
        client = self.oai_client
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format=format,
        )
        return completion.choices[0].message.parsed

    @property
    def assistant_color(self):
        return self.config.get("assistant_color", "yellow")

    def create_convo(self):
        """Create a new conversation"""
        model = llm.get_model(self.runtime_model)
        model.key = self.openai_api_key
        convo = model.conversation()
        return convo
    
    def ask(self, question):
        """Ask a question and return the response"""
        model = llm.get_model(self.runtime_model)
        prompt = question
        response = model.prompt(prompt)
        return response.text().strip()
    

def main(question):
    runtime = Runtime()
    response = runtime.ask(question)
    print(response)

if __name__ == '__main__':
    fire.Fire(main)
