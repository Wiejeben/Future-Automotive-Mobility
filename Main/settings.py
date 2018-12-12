from datetime import datetime
import sys
from dotenv import load_dotenv

load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Overwrite Python output to add timestamps
old_out = sys.stdout

class StampedOutput:
    def __init__(self):
        self.nl = True

    def write(self, x):
        """Write function overloaded."""

        if x == '\n':
            old_out.write(x)
            self.nl = True
        elif self.nl:
            old_out.write('%s: %s' % (str(datetime.now()), x))
            self.nl = False
        else:
            old_out.write(x)


sys.stdout = StampedOutput()
