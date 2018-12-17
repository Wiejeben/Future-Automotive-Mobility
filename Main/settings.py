from datetime import datetime
import sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# OR, the same with increased verbosity:
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


# Overwrite Python output to add timestamps
class StampedOutput:
    def __init__(self):
        self.nl = True
        self.out = sys.stdout

    def write(self, x):
        """Write function overloaded."""

        if x == '\n':
            self.out.write(x)
            self.nl = True
        elif self.nl:
            self.out.write('%s: %s' % (str(datetime.now()), x))
            self.nl = False
        else:
            self.out.write(x)

    def flush(self):
        pass


sys.stdout = StampedOutput()
