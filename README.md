# script-launcher
Shell script orchestration in an optional terminal user interface

Script Launcher is a terminal application with an optional terminal user interface (TUI) to execute a list of shell scripts. Scripts are listed in any number of JSON files that are fed as input to Script Launcher.

Script Launcher may be run with a terminal user interface to allow full control of execution and error handling during development, then run in noninteractive (headless) mode for production use to immediately execute all scripts in order.

Why?
====

Developers often collect a large amount of shell scripts to support software projects. Good scripts are reusable components that do one or at most just a few things, so Script Launcher provides a framework to collect them into project files that implement task-specific pipelines.

Usage
=====

Running `script-launcher.py -h` or `script-launcher --help` will show the usage information, as shown in Figure 1.

![Script Launcher help message](images/script-launcher-help.png?raw=true)
__Figure 1__ Script Launcher usage information

Providing a JSON file on the command line is _mandatory_. The provided example file `script-launcher.json` is the default JSON file. You will need to either create you own on the command line via the `-j` or `--json` options, or locate `script-launcher.json` in the current working directory.

Script Launcher will present a terminal user interface by default. Each script will be represented as buttons in the left sidebar. The scripts may be executed in _any order_ by pressing the buttons. An example of this behaviour is show in Figure 2.

If you want to see more or less information about your scripts' execution, try the `q` or `--quiet` flag to reduce noise and the `-v` or `--verbose` flag to present debugging information.

![Script Launcher partial execution](images/script-launcher-partial-exec.png?raw=true)
__Figure 2__ Script Launcher showing execution of a single script out of order

Script Launcher will show any errors that occur during execution, as shown in Figure 3.

![Script Launcher error](images/script-launcher-error.png?raw=true)
__Figure 3__ Script Launcher showing the result of a script execution with an error

Menu items at the bottom of the terminal user interface provide additional functionality. Figure 4 shows the results of the "Show steps" command (accessed by selecting the `s` key). The steps come from the JSON file selected by the user.

![Script Launcher show steps](images/script-launcher-show-steps.png?raw=true)
__Figure 4__ Script Launcher showing the "Show steps" command and result

Alternatively to executing each script in sequence, Script Launcher will immediately execute all scripts in order when the `-e` or `--execute` flag is provided on startup. Figure 5 shows the state immediately after launch when immediate execution has been requested.

![Script Launcher immediate execution](images/script-launcher-immediate-exec.png?raw=true)
__Figure 5__ Script Launcher terminal user interface after immediate script execution.

Finally, Script Launcher may be launched with the `-n` or `--noninteractive` flag to skip the terminal user interface entirely. Doing so immediately executes all scripts in order. That is, the `-n` flag infers the `-e` flag. This mode is intended for headless use, e.g., on a server, when no human is present. It is useful for production use once any bugs have been addressed. 

Figure 6 shows the noninteractive mode in action.

![Script Launcher noninteractive mode](images/script-launcher-noninteractive.png?raw=true)
__Figure 6__ Script Launcher in noninteractive mode