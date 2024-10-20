#!/usr/bin/env python3
import llm
import fire
import yaml
from pathlib import Path

class Runtime():
    def __init__(self, config_file="config.yaml"):
        self.config = self.read_config(config_file)
        self.runtime_model = self.config.get("runtime_model", None)
        print(self.runtime_model)

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

    def format_system_prompt(self, menu_entry_index):
        with open(menu_entry_index, 'r', encoding='utf-8') as file:
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
