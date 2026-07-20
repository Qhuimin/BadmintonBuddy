import sys
from tele_reader import run

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n👋 Badminton Buddy stopped by user. Goodbye!")
        sys.exit(0)