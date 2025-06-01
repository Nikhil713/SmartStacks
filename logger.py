from datetime import datetime

LOG_FILE = "device_log.txt"  # Log file 

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "w") as f:
        f.write(entry)
    f.close()