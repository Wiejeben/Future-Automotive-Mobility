# Smarterdam
Repository for Smarterdam - Minor Future Automotive Mobility - University of Applied Sciences Rotterdam.

# Installation
To install dependencies, run `pip install -r requirements.txt`.
Make sure your environmental variables are up-to-date by comparing it to the `.env.example`.

# Virtualenv
It is recommended that you install the main application in Virtualenv. To set this up, execute `virtualenv -p python3 venv`.

In order to activate Virtualenv, execute `source venv/bin/activate`.

# Pre-commit
To commit newly added dependencies, run `pip freeze > requirements.txt`.
