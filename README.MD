# Installation Instructions

### Prerequisites:
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
In your terminal, run the following (**replace {OS} with linux or windows** and **you may need to replace "pip" with "pip3"**):
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

## How to run:
**main_experiment.py is a good starting point - it was the script we used to create the data for our IAAI-21 submission**
main_experiment.py accepts **five** numerical command line arguments:
```
   $ python main_experiment.py {TOWER_MIN} {TOWER_MAX} {REQUEST_MIN} {REQUEST_MAX} {RUNS_PER_TOWER}
```
where:
   - TOWER_MIN and TOWER_MAX are the inclusive bounds on a uniform random distribution of towers per system
   - REQUEST_MIN and REQUEST_MAX are the inclusive bounds on a uniform random distribution of requests per tower
   - RUNS_PER_TOWER is the number of tests run per system
   
Example:
```
   $ python main_experiment.py 3 4 1 2 1
```
For reference, the IAAI-21 experiments were run with these settings:
   - TOWER_MIN = 3
   - TOWER_MAX = 10
   - REQUEST_MIN = 1
   - REQUEST_MAX = 8
   - RUNS_PER_TOWER = 5
Which took ~3 hours to run from start to finish

## Additional Info

Tested using:
- Ubuntu 20.04 & Python 3.8.6
- Windows 10 v1903 & Python 3.7.1

Full module dependency list can be found under debug/full_requirements_{OS}
