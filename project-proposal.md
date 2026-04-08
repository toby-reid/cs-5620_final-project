# Project Proposal

*CS 5620 final project*

## Constraint-Based Bash Tutor

For this project, I plan to use the **prototype** option to develop a Bash tutor that uses constraint-based modeling to determine whether the student got the correct solution.
Below are more in-depth answers to the four given questions:

1. What is the problem you are solving?
   1. Students of Computer Science at USU really don’t get much guidance on command-line usage.
      Apart from CS 1440, which teaches only the basics of `cd` and `ls`, there aren’t any classes for efficient shell scripting and CLI navigation.
      Familiarity with this would have put me in a much better starting position at my current job, an issue I’m sure is common among beginning software engineers.
1. What will your prototype seek to teach?
   1. The prototype will seek to teach the most common Bash utilities, including `cd` and `ls`, `find` and `cat`, and `if` and `for` blocks.
      For the limited scope of this project, I hesitate to go much deeper than that; it may end up with just a few simple commands, as the constraint-based system will likely take the most time.
1. How will your prototype support the learner?
   1. The system will provide simple tasks, such as “move to this directory” or “locate a certain file”, which the student is expected to complete.
      Later tasks (if I manage to get that far) would be more complex and less direct, such as “find and delete the biggest file in this directory” (via `du` and `rm`, ideally).
      Thus, the user will (likely) learn the basics early on, then learn more applicable uses for those utilities by the end of the tutor.
1. What AI techniques will your system leverage?
   1. I was seeking an opportunity to test constraint-based modeling, something that was not explored to a high depth in this class.
      Originally, I conceived a Rubik’s Cube tutor (using third-party Python packages) to teach myself, but that didn’t fit as well as I’d hoped.
      A Bash tutor is simple enough to verify whether they got the correct answer, yet is open-ended enough to showcase the full potential of constraint-based tutoring (i.e., since there is no “correct” way to do a task, other systems would simply not work).

Of course, this all depends on the time I end up having for the complexity, but my main goal is to build a skeleton that could, in theory, be modified to add any tasks with desired outcomes, and the tutoring system will just handle it automatically.

For the sake of speed, I would use either Bash or Python to implement it.
Bash would be much easier to implement, though it does come with the potential concern of the user overriding variables.
I could make a simplified shell in Python, but that would also come with the potential concern of not allowing the user to use their own shell environment.  
The best solution, then, to my knowledge, would be to use Python’s subprocess module to execute user input and change working directories on the fly.
