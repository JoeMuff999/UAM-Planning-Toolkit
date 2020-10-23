Repository for testing automata in Python. Uses TuLiP which can be found here : https://github.com/tulip-control/tulip-control

Main graph in file "reworked_graph.py"
TuLiP and MVP implementation in "graph_manager.py"

# Installation Instructions

### Requirements:
- Git (if on Windows, I recommend [Git Bash](https://gitforwindows.org/))
- Python3 (I used [Python 3.7.1](https://www.python.org/downloads/release/python-371/))
- pip ([**P**ython **I**nstallation **P**ackage](https://pypi.org/project/pip/) - comes included with most Python releases)

### Clone the repository from the command line:
In your terminal (on Windows this would be Git Bash, Powershell, CMD or some other CLI), run the following
```
   $ git clone https://github.com/JoeMuff999/Automata-Testing.git
```
Which will clone the repository to your local machine. 
### Install dependencies with pip:
In your terminal, run the following (**replace {OS} with linux or windows** and **if you use pip3, replace "pip" with "pip3"**):
```
   $ cd Automata-Testing
   $ pip install wheel
   $ pip install cvxopt
   $ pip install -r requirements_{OS}.txt
```
Which will install (almost) all of the dependencies.
### Install TuLiP:
You will need to install my forked implementation of tulip. To do so, run the following in your terminal (**you may need to replace "python" with "python3" depending on how your symlinks are setup** and **you may need to prepend the final command with "sudo", and you may need to run it twice**):
```
   $ git clone https://github.com/JoeMuff999/tulip-control
   $ cd tulip-control
   $ python setup.py install 
```

## Troubleshooting Installation:
Linux:
- Verify that your matplotlib installation is version 3.2.0 by running the command 
   ```
   $ pip list
   ```
- If you recieve the error "matplotlib-is-currently-using-agg-which-is-a-non-gui-backend", run the following:
   ```
   $ sudo apt-get install python3-tk
   ```
   (Credits to : https://stackoverflow.com/questions/56656777/userwarning-matplotlib-is-currently-using-agg-which-is-a-non-gui-backend-so)

