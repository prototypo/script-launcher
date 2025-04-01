from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, Static, RichLog, Button
from textual import events
from textual.reactive import reactive
import subprocess
from rich.text import Text
import simplejson as json
import os
import sys
import argparse

title = "Script Launcher"
subtitle = "Shell script orchestration in an optional terminal user interface"

class StepList(Static):
    """Widget to display steps as buttons with status indicators."""

    def __init__(self, descriptions: list[str], app, **kwargs):
        super().__init__(**kwargs)
        self.descriptions = descriptions
        self.status = ""  # eventually either "success", or "failure" icons

    def compose(self) -> ComposeResult:
        for i, description in enumerate(self.descriptions):
            self.label = reactive("")
            self.label = f'{i}. {self.status} {description}'
            yield Button(label=f'{self.label}', id=f"step-{i}", variant="default")

    def update_status(self, index: int, status: str):
        self.status = status
        self.btnid = f"#step-{index}"
        self.query_one(self.btnid).label=f'{index}. {self.status} {self.descriptions[index]}'
        self.query_one(self.btnid).refresh()
        self.refresh()

class TUIScriptRunnerApp(App):
    """Textual TUI application for executing shell scripts."""

    CSS = """
    Horizontal {
        height: 1fr;
    }
    StepList {
        width: 30%;
    }
    RichLog {
        width: 70%;
    }
    Button {
        align: left middle;
        min-width: 40;
        text-align: left;
    }
    """
    
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "dump_steps()", "Show steps"),
        ("ctrl+q", "quit", "Quit")
    ]

    def __init__(self, steps: list[dict], **kwargs):
        super().__init__(**kwargs)
        self.steps = steps
        
        # Make lists of the labels and commands
        self.labels = list()
        self.cmds = list()
        for step in self.steps: # Each step is a dict
            self.labels.append(step['label'])
            self.cmds.append(step['cmd'])
        
        self.step_list = StepList(self.labels, app=self)
        self.output_log = RichLog()
        if verbosity > 0:
            self.output_log.write(f"Welcome to {title}. {len(self.steps)} scripts are available for execution.\n")
            self.output_log.write(f'Project name: {project_name}')
            self.output_log.write(f'Project description: {project_description}\n')
        if verbosity > 1:
            # Print command line arguments
            self.output_log.write(f'Command line arguments: {args}')

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Horizontal(self.step_list, self.output_log)
    
    def on_mount(self) -> None:
            self.title = title
            self.sub_title = subtitle
            
            if execute > 0:
                # TODO complete
                # Immediate execution has been requested.
                # There are as many buttons as there are commands so
                # loop through the list of commands and simulate a
                # press of each button.
                index = 0
                for cmd in self.cmds:
                    btnid = f"#step-{index}"
                    self.query_one(btnid).action_press()
                    index += 1
        
    async def action_dump_steps(self):
        self.output_log.write("These steps are configured for execution:\n")
        self.output_log.write(json.dumps(self.steps, sort_keys=True, indent=4 * ' '))

    async def execute_script(self, index: int):
        """Execute a shell script and update UI based on result."""
        description = self.labels[index]
        script = self.cmds[index]
        
        if verbosity > 0:
            self.output_log.write(f"{description}\n")
            self.output_log.write(f"Executing: {script}\n")
            
        try:
            result = subprocess.run(
                script, shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                self.step_list.update_status(index, "✅")
                self.output_log.write(f"Result:\n{result.stdout}\n✅ Success\n")
            else:
                self.step_list.update_status(index, "❌")
                self.output_log.write(f"{result.stderr}\n❌ ERROR\n")
        except Exception as e:
            self.step_list.update_status(index, "🚩")
            self.output_log.write(f"🚩 Error: {str(e)}\n")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        if button_id and button_id.startswith("step-"):
            index = int(button_id.split("-")[1])
            await self.execute_script(index)
            
def main() -> None:
    """Main method."""
    
    # TODO:
    # MAYBE:
    #       - Accept JSON on STDIN instead of file?
    parser = argparse.ArgumentParser(description="Run shell scripts named in a JSON file.")

    # Set verbosity. The -v and -q options are mutually exclusive so only one may be set at a time.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help=f'more explanatory output than the default; conflicts with -q', action="store_true")
    group.add_argument("-q", "--quiet", help=f'less explanatory output than the default; conflicts with -v', action="store_true")
    
    # Allow override of the default JSON file containing scripts to run.
    default_json = "script-launcher.json"
    parser.add_argument("-j", "--json", help=f'name a JSON file containing scripts to run (default is {default_json})',
                        type=str, default=f'{default_json}')
    
    # Allow immediate execution of all scripts. This may be used headless or with the TUI.
    parser.add_argument("-e", "--execute", help="execute all scripts immediately",
                        action="store_true")
    
    # Allow headless execution of all scripts. This infers -i, immediate execution.
    parser.add_argument("-n", "--noninteractive", help="run without a user interface; infers -e",
                        action="store_true")
    
    # Process command line arguments
    global args
    args = parser.parse_args()
    
    # Set verbosity level
    global verbosity
    if args.quiet:
        verbosity = 0 # -q
    elif args.verbose:
        verbosity = 2 # -v
    else:
        verbosity = 1 # default

    # Process the designated JSON file
    if args.json:
        try:
            with open(args.json) as json_data:
                data = json.load(json_data)
                global project_name
                project_name = data['project_name']
                global project_description
                project_description = data['description']
                steps = data['steps']
        except Exception as e:
            print(f"🚩 Error in JSON file {args.json}: {str(e)}\nTry {__file__} -h for help", file=sys.stderr)
            sys.exit(1)
    
    # Execute scripts either immediately or wait for human engagement
    global execute
    if args.execute:
        execute = 1 # immediate execution
    else:
        execute = 0 # wait for human

    # Show no TUI if in noninteractive mode
    # This infers immediate execution of all scripts
    if args.noninteractive:
        
        # Noninteractive mode infers immediate execution
        execute = 1 # immediate execution
        args.execute = True # Inferred by -n
        
        if verbosity > 0:
            print("Running headless")
            print(f'Using JSON file: {args.json}')
            print(f'Project name: {project_name}')
            print(f'Project description: {project_description}\n')
            
        
        if verbosity > 1:        
            # Print command line arguments
            print(f'Command line arguments: {args}')
            # Note that we are immediately executing all scripts
            print(f'Immediately executing all scripts\n')
            
            # DBG info
            print(f'Steps: {steps}')
            print(type(steps))
            for step in steps:
                print("----------")
                print(f'Step: {step}')
                print(f'Type: {type(step)}')
                print(f'Label: {step['label']}')
                print(f'Command: {step['cmd']}')
                
        # Since we are in noninteractive mode, execute each command
        for step in steps:
            try:
                label = step['label']
                script = step['cmd']
                print(f'Running: {label}', file=sys.stderr)
                result = subprocess.run(
                    script, shell=True, capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"Result:\n{result.stdout}\n✅ Success\n", file=sys.stderr)
                else:
                    print(f"{result.stderr}\n❌ ERROR\n", file=sys.stderr)
            except Exception as e:
                print(f"🚩 Error: {str(e)}\n", file=sys.stderr)
                
    else:
        # Run the TUI if not headless
        app = TUIScriptRunnerApp(steps)
        app.run()
                        
    # Exit cleanly when finished
    if verbosity > 1:
        print(f"✅ Successful execution")
    sys.exit(0)
    
if __name__ == "__main__":
    main()

