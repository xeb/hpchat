# An interactive Python shell for debugging purposes only
# It basically just imports the necessary modules and starts an interactive shell
import code
import sys

# Preload the desired imports
from hpchat.db import *
from hpchat import *

# Start the interactive shell
vars_to_import = locals()  # Import all current variables into the shell
banner = "HPCHAT: Python Interactive Shell with imports\nTry connecting to the DB with: connect_to_db(), then run listall()"
code.interact(banner=banner, local=vars_to_import)
