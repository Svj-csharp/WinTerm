import sys
import os
from com import TerminalCommands

class LinuxTerminal:
    def __init__(self):
        self.commands = TerminalCommands()
        self.running = True
        
    def run(self):
        """Main terminal loop"""
        print("WinTerm v1.0")
        print("Type 'help' for available commands")
        print("Type 'exit' to quit\n")
        
        while self.running:
            try:
                # Print prompt
                prompt = self.commands.print_prompt()
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Parse command and arguments
                parts = user_input.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute command
                result = self.commands.execute(command, *args)
                
                # Print result if not empty
                if result:
                    print(result)
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nExiting...")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")

def main():
    # Set up environment for better terminal experience
    os.environ['TERM'] = 'xterm-256color'
    
    # Create and run terminal
    terminal = LinuxTerminal()
    terminal.run()

if __name__ == "__main__":
    main()