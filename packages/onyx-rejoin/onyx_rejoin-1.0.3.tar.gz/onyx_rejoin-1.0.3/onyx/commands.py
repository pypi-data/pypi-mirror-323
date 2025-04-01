import subprocess
import time
import os
import json
import sys

def setup():
    """Setup the dependencies and environment for the bot."""
    print("Starting setup...")

    # Install required packages
    subprocess.run(["pkg", "install", "git", "tmux", "proot", "-y"])
    print("Packages installed.")

    # Start tmux and termux-chroot
    subprocess.run(["tmux"])
    subprocess.run(["termux-chroot"])
    print("tmux and termux-chroot started.")

    print("Setup complete!")

def start():
    """Start the main bot."""
    print("Starting the main bot...")

    # Run the main.py logic here (you need to point to your actual script's path)
    script_path = "/data/data/com.termux/files/home/main.py"  # Update this with the correct path to your main.py
    subprocess.run(["python", script_path])

    print("Main bot started!")


def main():
    """This is the entry point for the 'onyx rejoin' command."""
    if len(sys.argv) < 2:
        print("Please specify 'setup' or 'start'.")
        return

    command = sys.argv[1].lower()

    if command == "setup":
        setup()
    elif command == "start":
        start()
    else:
        print(f"Unknown command: {command}")
