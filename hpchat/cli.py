import sys
import fire
import readline
from hpchat.runtime import Runtime
import pyfiglet
from termcolor import colored
from simple_term_menu import TerminalMenu
from pathlib import Path

def select_text_file(title=None):
    """Presents a menu of the sermon to select"""
    parent_dir = Path(__file__).parent.parent
    output_dir = parent_dir / 'output'
    txt_files = list(output_dir.glob('*.txt'))
    
    if not txt_files:
        print("No text files found in the output directory.")
        return None
    
    file_names = [file.name for file in txt_files]
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
            user_input = input(colored("You: ", "grey"))
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

def format_system_prompt(system_prompt, menu_entry_index):
    with open(menu_entry_index, 'r', encoding='utf-8') as file:
        content = file.read()
    
    return system_prompt.format(sermon=content)

def main():
    """Primary CLI entrypoint"""
    runtime = Runtime()
    welcome_message = pyfiglet.figlet_format("HPChat")
    print(colored(welcome_message, color='blue'))
    print(colored("Using the following system_prompt:", color='green'))
    print(colored(runtime.system_prompt, color='grey'))
    print("--------------------------------")
    print("Please select a sermon you would like to discuss and hit ENTER:\nType '" + colored("exit", "red") + "' to exit.\n\n")
    menu_entry_index = select_text_file()
    print(f'You selected option {menu_entry_index}')

    formatted_system_prompt = format_system_prompt(runtime.system_prompt, menu_entry_index)
    chatloop(runtime, system=formatted_system_prompt)

if __name__ == '__main__':
    fire.Fire(main)
