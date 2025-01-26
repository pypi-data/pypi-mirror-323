import subprocess
import sys
import uv
import os

def install_langflow():
    try:
        uv_bin = uv.find_uv_bin()
        subprocess.check_call([
            uv_bin, "tool", "install", "--force", "--python", "python3.12", "langflow@latest"
        ])
        subprocess.check_call([uv_bin, "tool", "update-shell"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install langflow: {e}")
        sys.exit(1)



if __name__ == "__main__":
    install_langflow()
