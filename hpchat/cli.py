import sys
import fire
import readline
from hpchat.runtime import Runtime
import pyfiglet
from termcolor import colored
from simple_term_menu import TerminalMenu
from pathlib import Path
from hpchat import db

def select_text_file(title=None, runtime: Runtime = None):
    file_names, txt_files = runtime.get_sermons()
    menu = TerminalMenu(file_names, title=title)
    selected_index = menu.show()    
    if selected_index is None:
        print("No file selected.")
        return None

    selected_file = txt_files[selected_index]    
    return str(selected_file.resolve())

def chatloop(runtime: Runtime = None, system: str = None):
    convo = runtime.create_convo()
    history_file = "/tmp/hpchat_history"
    try:                                
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass   

    while True:
        try:
            user_input = input(colored("You: ", "white"))
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        if user_input.lower() == "exit":
            print("\nExiting...")
            break
        
        readline.add_history(user_input)
        response = convo.prompt(user_input, system=system, stream=True)
        # Write "System:" to stdout without a line break
        sys.stdout.write(colored("System: ", "yellow"))
        
        for chunk in response:
            sys.stdout.write(colored(chunk, "yellow"))
            sys.stdout.flush()
        sys.stdout.write("\n")
        sys.stdout.flush()
        pass

    readline.write_history_file(history_file)
    return


def main():
    """Primary CLI entrypoint"""
    runtime = Runtime()
    welcome_message = pyfiglet.figlet_format("HPChat")
    print(colored(welcome_message, color='blue'))
    print(colored("Using the following system_prompt:", color='green'))
    print(colored(runtime.system_prompt, color='white'))
    print("--------------------------------")
    print("Please select a sermon you would like to discuss and hit ENTER:\nType '" + colored("exit", "red") + "' to exit.\n\n")
    menu_entry_index = select_text_file(runtime=runtime)
    print(f'You selected option {menu_entry_index}')

    formatted_system_prompt = runtime.format_system_prompt(menu_entry_index)
    chatloop(runtime, system=formatted_system_prompt)

if __name__ == '__main__':
    fire.Fire(main)
