# Final Project

*for CS 5620, AI in Education, at Utah State University.*

## Getting Started

For this demo, you will need:

* [Python](https://www.python.org/downloads/) (must be at least 3.12; recommended just use the latest version)
* [Git](https://git-scm.com/install/)
* A common shell (such as Git Bash, which is installed alongside Git for Windows)
  * For convenience, ensure "Open Git Bash here" is enabled during Git installation.

The demo has been configured to work without any additional Python packages.

## Running the Tool

1. Open Bash into a working directory, such as your `Downloads` folder.
   1. If on Windows with Git Bash, you should be able to right-click the folder in your file explorer and select **Open Git Bash here**.
   1. If on Linux, you should be able to right-click the folder in your file explorer and select **Open in Terminal**.
1. Paste in the following command using **Shift**+**Enter**:
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
