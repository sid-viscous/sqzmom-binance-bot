import sys
from wenmoon.main import main



# main()
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard interrupt event")
        sys.exit(0)
