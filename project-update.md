# Project Update

*CS 5620 final project*

## What Has Been Achieved So Far

When I originally submitted the project proposal, I figured I could fairly easily implement a Bash wrapper using Python's `subprocess` package.
Turns out, the module is not nearly as capable or feature-rich as I'd originally supposed.

After performing extensive research into potential alternatives (viable ones of which I found none), I returned to my original idea to make a Python wrapper myself.
Of course, I recognize that I lack the time necessary to create a truly "safe" wrapper, but I at least wanted something that would prevent the user from navigating outside or making any changes beyond the given workspace.

So what I've been able to create thus far is that exact wrapper, plus a basic task reader.

### Bash Wrapper

A couple of Python classes and functions dictate the entire process.

In essence, the wrapper takes user input (as a list of strings, a single Bash command), ensures it doesn't impact anything outside the given workspace directory (through very simple path checking), adds an extra `pwd` call to the end, and executes the process as a submodule.

I've even equipped the system to hash an entire directory or other file system to determine what, if anything, has been changed, meaning that `rm` or similar tasks should also be possible.
The system then uses the last line of output (thanks to `pwd`) to determine the new current working directory, returning all relevant data, including file systems, stdout/stderr, the exact commands executed thus far, etc.

The system is admittedly very limited.
For example, as it is now, it doesn't prevent things like `$(pwd)/..` to prevent the user from going outside the workspace scope&mdash;in fact, it doesn't check for any variables or subprocesses.  
However, as a basic implementation for a proof of concept, it does its job.

### Task Manager

A couple of related Python classes handle tasks.

Using Python's `json` and `dataclass` modules, the object reads in a JSON file (formatted as a list of "task" objects), converting each object therein to a `Task` dataclass instance.
These tasks could then be categorized by the skills they report to teach (based on their JSON data).

Eventually, the idea is for the task manager to determine *what* tasks to assign based on student knowledge modeling (e.g., via Bayesian knowledge tracing), but that goes beyond the scope of my proposed project (which focuses more on constraint-based tutoring), so I elected not to implement the skill categorization or selection; rather, skills are selected at random.

## What Has Changed from the Proposal

Not a whole lot has changed from my original proposal, except for the scope.

Originally, trying to keep the scope limited, I had a list of about 10 basic Bash features that I wanted to feature.
Depending on how well my system works (it's entirely untested\*), I may still manage to implement several of those, but I'm now only trying to focus on ensuring `cd` and `ls` work correctly; everything else can wait.

> \* I have a bad habit of coding for hours, then remembering suddenly that it's entirely untested.
> Fortunately, I'm a good enough programmer that this approach almost always works with minimal (if any) debugging, but it also means that (for example, in this case) I have hundreds of lines of code that I haven't tested.  
> I refuse to use generative AI to write any of my code, which I believe heavily contributes to the reliability and accuracy of my code.

## What is Left To Do

The biggest things left to do are to test the system and ensure it can handle task selection correctly.

I will also add some keyword commands, such as `exit`, `hint`, and `help` that the user can input to give up, get the next-level hint, or see a list of possible commands (or even a list of commands the system knows about, such as `ls`, that the user may have forgotten).
This, to me, is likely going to be the most "tutory" part of the system.

I also would like to add checks to ensure (for example) unknown variables or subprocesses are not used (this can likely be easily implemented via `$` bans).

Finally, I want to generate a few tasks with an LLM just to see how well those can hold up.
In theory, my app is built to handle *any* task with the appropriate JSON schema, provided it includes a "correct" solution, so this should be perfect for an LLM to generate, especially for the most basic of Bash tasks.
