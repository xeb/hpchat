#!/usr/bin/env python3
import llm
import fire
import yaml
from llm_gemini import GeminiPro
from pathlib import Path

@llm.hookimpl
def register_models(register):
    register(GeminiPro("gemini-1.5-pro-exp-0801"))

class Runtime():
    def __init__(self, config_file="config.yaml"):
        self.config = self.read_config(config_file)
        self.runtime_model = self.config.get("runtime_model", "claude-3-5-sonnet-20240620")

    def read_config(self, config_file):
        """ Reads config.yaml from local path and returns it as a dictionary"""
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / 'config.yaml'
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)

        return config
    
    @property
    def system_prompt(self):
        return self.config.get("system_prompt", "")

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
