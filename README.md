# Bash Tutor

*Final project for CS 5620, AI in Education, at Utah State University.*

This is a proof of concept for a constraint-based Bash tutor, based in Python.

> [!Caution]
> As it turns out, even when invoked from Git Bash, Windows machines will still run Python subprocesses from its native command line.
> Thus, **this tool is not available for Windows machines**.
>
> One alternative is to use a Windows Subsystem for Linux (WSL) distribution to run the tool.

## Getting Started

For this demo, you will need:

* Python 3, at least version 3.11
* Git
  * For Windows, the Git distribution also provides a Bash-compliant shell.
* A standard Unix-like shell, such as Bash
  * This comes as the "Terminal" app in most Linux distributions.

The demo has been configured to work without any additional Python packages.

## Running the Tool

1. Open a shell into a working directory, such as your `Downloads` folder.
   1. If on Windows with Git Bash, you should be able to right-click the folder in your file explorer and select **Open Git Bash here**.
   1. If on Linux, you should be able to right-click the folder in your file explorer and select **Open in Terminal**.
1. Clone this Git repository (paste in this command using **Shift**+**Enter** on the keyboard):
   ```bash
   git clone https://github.com/toby-reid/cs-5620_final-project.git
   ```
1. Move into the cloned repository folder:
   ```bash
   cd cs-5620_final-project
   ```
1. Start the application:
   ```bash
   python3 -m bash_tutor
   ```
   1. If you get a "command not found" error on Windows, try using `py` or `python` in place of `python3`.
