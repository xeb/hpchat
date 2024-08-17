#!/usr/bin/env python3

import sys
import tiktoken

def count_tokens(file_path, model="gpt-3.5-turbo"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = len(encoding.encode(content))
        
        return num_tokens
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python token_counter.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    token_count = count_tokens(input_file)
    print(f"Number of tokens in '{input_file}': {token_count}")

if __name__ == "__main__":
    main()