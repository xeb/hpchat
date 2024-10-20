#!/usr/bin/env python3
import os
import llm
import fire
import yaml
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel

class Runtime():
    def __init__(self, config_file="config.yaml"):
        self.config = self.read_config(config_file)
        self.runtime_model = self.config.get("runtime_model", None)
        
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            with open(os.path.expanduser("~/.ssh/openai_api_key.txt"), "r") as f:
                openai_api_key = f.read().strip()

        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable")
        
        self.oai_client = OpenAI(api_key=openai_api_key)
        llm.configure_openai(api_key=openai_api_key)
        # print(self.runtime_model)

    @property
    def root_path(self):
        return Path(__file__).parent.parent

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

    def get_sermons(self):
        """Presents a menu of the sermon to select"""
        return [
            {
                "url_slug": "gods_invitation",
                "title": "Come Home: An Invitation to Return to God's Embrace",
                "file_path": "/Users/xeb/projects/hpchat/output/June 16, 2024 ｜ Jeff Maguire ｜ Harbor Point Church-segment.txt"
             },
             {
                 "url_slug": "naming_anxiety",
                 "title": "Naming Anxiety: Finding Authority and Peace in Christ",
                 "file_path": "Users/xeb/projects/hpchat/output/August 11, 2024 ｜ Harbor Point 10AM-segment.txt"
             }
        ]

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

    def format_system_prompt(self, full_sermon_path):
        with open(full_sermon_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        return self.system_prompt.format(sermon=content)

    @property
    def assistant_color(self):
        return self.config.get("assistant_color", "yellow")

    def create_convo(self):
        """Create a new conversation"""
        model = llm.get_model(self.runtime_model)
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
