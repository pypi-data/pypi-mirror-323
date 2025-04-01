import time
import subprocess
import threading
import os
import json
import sys

SETTINGS_FILE = "roblox_bot_settings.json"
ROBLOX_PACKAGE_NAME = "com.roblox.client"
restarting = False
paused = False
running = True  # New variable to track if the bot should keep running
pause_condition = threading.Condition()

def save_settings(private_server_url, restart_interval):
    settings = {
        "private_server_url": private_server_url,
        "restart_interval": restart_interval
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return None

def join_private_server(private_server_url):
    print("Attempting to join the private server...")
    subprocess.run([
        'am', 'start', '-a', 'android.intent.action.VIEW', '-d', private_server_url
    ])
    print("Joined the private server!")

def close_roblox():
    print("Closing Roblox...")
    subprocess.run(['su', '-c', 'pkill -f ' + ROBLOX_PACKAGE_NAME])
    print("Roblox has been closed.")

def is_roblox_running():
    try:
        subprocess.run(['pidof', ROBLOX_PACKAGE_NAME], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def restart_roblox_cycle(private_server_url, restart_interval):
    global restarting, paused, running
    last_restart_time = time.time()

    while running:  # Continue only while the bot is running
        with pause_condition:
            if paused:
                print("Bot is paused. Waiting for resume...")
                pause_condition.wait()

        current_time = time.time()
        if current_time - last_restart_time >= restart_interval:
            restarting = True
            print(f"Restarting Roblox after {restart_interval} seconds...")
            close_roblox()
            time.sleep(5)
            join_private_server(private_server_url)
            restarting = False
            last_restart_time = current_time

        if not restarting and not is_roblox_running():
            print("Roblox crashed or was closed. Restarting...")
            time.sleep(5)
            join_private_server(private_server_url)

        time.sleep(10)

    print("Bot has been stopped.")

def handle_commands():
    global paused, running
    while running:
        command = input().strip().lower()
        if command == "pause":
            with pause_condition:
                paused = True
                print("Bot paused.")
        elif command == "resume":
            with pause_condition:
                paused = False
                pause_condition.notify()
                print("Bot resumed.")
        elif command == "stop":
            print("Stopping the bot...")
            running = False  # Stop the bot loop
            with pause_condition:
                paused = False
                pause_condition.notify()  # Resume the bot loop to terminate gracefully

if __name__ == "__main__":
    previous_settings = load_settings()
    if previous_settings:
        print("Found previous settings:")
        print(f"Private Server URL: {previous_settings['private_server_url']}")
        print(f"Restart Interval: {previous_settings['restart_interval']} seconds")
        choice = input("Do you want to reload these settings? (yes/no): ").strip().lower()
        if choice == "yes":
            private_server_url = previous_settings["private_server_url"]
            restart_interval = previous_settings["restart_interval"]
        else:
            private_server_url = input("Enter your Roblox private server link: ")
            restart_interval = int(input("Enter the restart interval in seconds (e.g., 3600 for 1 hour): "))
            save_settings(private_server_url, restart_interval)
    else:
        private_server_url = input("Enter your Roblox private server link: ")
        restart_interval = int(input("Enter the restart interval in seconds (e.g., 3600 for 1 hour): "))
        save_settings(private_server_url, restart_interval)

    print(f"Private server link set to: {private_server_url}")
    print(f"Restart interval set to: {restart_interval} seconds")
    print("Commands: 'pause', 'resume', 'stop'")

    # Start a separate thread to handle commands
    command_thread = threading.Thread(target=handle_commands, daemon=True)
    command_thread.start()

    # Start the main bot cycle
    restart_roblox_cycle(private_server_url, restart_interval)