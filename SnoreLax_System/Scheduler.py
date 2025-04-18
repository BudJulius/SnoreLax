import schedule
import time
import subprocess
import os
import signal
import sys
from datetime import datetime

    # Global variable that keeps track and stores the current process
current_process = None

    # Starts the Listener.py script, which is responsible for recording audio
def start_listener():
    """Start the sound listener program"""
    global current_process
    print(f"[{datetime.now()}] Starting sound listener...")

    current_process = subprocess.Popen(["python", "Listener.py"], 
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
    
    print(f"[{datetime.now()}] Sound listener started with PID {current_process.pid}")
    
        # Writes pid to a file for later use and control
    with open("listener_pid.txt", "w") as f:
        f.write(str(current_process.pid))

    # This stops Listener.py, handles many cases to be sure that it really stops and kills all precesses
def stop_listener():
    """Stop the sound listener program"""
    global current_process
    print(f"[{datetime.now()}] Stopping sound listener...")
    
        # Since this was tested on Windows laptop and Raspberry Pi, both situations needed to be handled for easier use
    if current_process and current_process.poll() is None:
        if sys.platform == 'win32':
            current_process.terminate()
        else:
            os.kill(current_process.pid, signal.SIGTERM)
        time.sleep(2)
        
        if current_process.poll() is None:
            if sys.platform == 'win32':
                subprocess.run(["taskkill", "/F", "/PID", str(current_process.pid)], 
                               check=False)
            else:
                os.kill(current_process.pid, signal.SIGKILL)
        
        print(f"[{datetime.now()}] Sound listener stopped")
    else:
        try:
            with open("listener_pid.txt", "r") as f:
                pid = int(f.read().strip())
                
            if sys.platform == 'win32':
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                               check=False)
            else:
                os.kill(pid, signal.SIGTERM)
                
            print(f"[{datetime.now()}] Sound listener stopped (PID {pid})")
        except (FileNotFoundError, ValueError, ProcessLookupError) as e:
            print(f"[{datetime.now()}] No running listener found or error stopping: {e}")


    # Main method that controls the scheduler and its tasks
if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting scheduler...")

        # Variables for start and stop times, must be in this format: HH:MM:SS
    startTimeString = "00:30:00"
    stopTimeString = "06:00:00"
    
    # Schedule tasks
    schedule.every().day.at(startTimeString).do(start_listener)
    schedule.every().day.at(stopTimeString).do(stop_listener)

    
    print(f"[{datetime.now()}] Scheduler initialized:")
    print(f" - Start time: {startTimeString}, Stop time: {stopTimeString}")
    
        # Check if the current time is within the monitoring window,if yes, start the listener
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    start_time = 0 * 60 + 30
    stop_time = 6 * 60 + 0
    current_time = current_hour * 60 + current_minute
    
    if start_time <= current_time < stop_time:
        print(f"[{datetime.now()}] Monitoring and strarting listener...")
        start_listener()
    
        # Runs the scheduler, and checks every 10 seconds for tasks
    while True:
        schedule.run_pending()
        time.sleep(10)
