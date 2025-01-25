from netemu.cli import start
import os
import sys
import shutil

def main():
    if os.geteuid() != 0:
        unshare = shutil.which("unshare")
        os.execv(
            unshare, [unshare, "-Urn", sys.executable, "-m", "netemu"] + sys.argv[1:]
        )
    start()

if __name__ == "__main__":
    main()
