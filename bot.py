import time
import psutil
import requests
import os
import subprocess
import yaml
from datetime import datetime

# Function to send a message to Telegram
def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send message: {e}")

# Function to get the name of the first folder in a directory
def get_first_folder_name(path):
    try:
        entries = os.listdir(path)
        folders = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
        return folders[0] if folders else None
    except Exception as e:
        print(f"Failed to get folder name: {e}")
        return None

# Function to run a command in a separate process
def run_gramaddict(folder_name):
    additional_command = f"python /data/data/com.termux/files/home/gramaddict/run.py --config /data/data/com.termux/files/home/gramaddict/accounts/{folder_name}/config.yml"
    
    # Start GramAddict in a separate process
    process = subprocess.Popen(additional_command, shell=True)
    
    # Return the process so it can be monitored
    return process

# Function to check if a process is still running by its PID
def is_process_running(pid):
    try:
        # Check if process with pid exists
        p = psutil.Process(pid)
        return p.is_running()
    except psutil.NoSuchProcess:
        return False

# Function to terminate the GramAddict process
def terminate_gramaddict_process(process, folder_name, bot_token, chat_id):
    process.terminate()  # Terminate the process
    message = f"GramAddict session for account {folder_name} has been stopped at scheduled time."
    send_telegram_message(bot_token, chat_id, message)
    print(message)

def main():
    accounts_path = "/data/data/com.termux/files/home/gramaddict/accounts/"  # Path to account folders

    # Get the first folder name
    folder_name = get_first_folder_name(accounts_path)

    if folder_name:
        # Define the path to your .yml file
        yaml_file_path = f'/data/data/com.termux/files/home/gramaddict/accounts/{folder_name}/telegram.yml'
        
        # Open and read the .yml file
        try:
            with open(yaml_file_path, 'r') as file:
                data = yaml.safe_load(file)

                # Extract Telegram API token and chat ID
                bot_token = data.get('telegram-api-token')
                chat_id = data.get('telegram-chat-id')

                # Print the parameters (for debugging)
                print(f"Bot Token: {bot_token}")
                print(f"Chat ID: {chat_id}")

        except FileNotFoundError:
            print(f"YAML file not found at {yaml_file_path}.")
            return
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return

    else:
        print("No folder found in the specified accounts directory.")
        return

    # Start the GramAddict process
    gramaddict_process = run_gramaddict(folder_name)

    # Define the scheduled times for stopping the process
    scheduled_times = ["11:03", "15:24", "21:10", "05:13"]

    check_interval_schedule = 60  # Check every 60 seconds for schedule
    check_interval_monitor = 600  # Check every 600 seconds for process status

    last_schedule_check_time = time.time()
    last_monitor_check_time = time.time()

    while True:
        current_time = datetime.now().strftime("%H:%M")
        current_time_unix = time.time()

        # Check if it's time to process the scheduled times
        if current_time_unix - last_schedule_check_time >= check_interval_schedule:
            last_schedule_check_time = current_time_unix

            if current_time in scheduled_times:
                if is_process_running(gramaddict_process.pid):
                    terminate_gramaddict_process(gramaddict_process, folder_name, bot_token, chat_id)
                    gramaddict_process = run_gramaddict(folder_name)

        # Check if it's time to monitor the process
        if current_time_unix - last_monitor_check_time >= check_interval_monitor:
            last_monitor_check_time = current_time_unix

            if not is_process_running(gramaddict_process.pid):
                message = f"GramAddict session has crashed for account {folder_name}. Restarting in 15 seconds"
                send_telegram_message(bot_token, chat_id, message)
                gramaddict_process = run_gramaddict(folder_name)
            else:
                print(f"GramAddict is running with PID: {gramaddict_process.pid}")

        # Wait for a short period before the next iteration
        time.sleep(1)

if __name__ == "__main__":
    main()
