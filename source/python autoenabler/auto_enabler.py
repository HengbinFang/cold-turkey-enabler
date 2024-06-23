import sqlite3
import json
import time
import logging
import configparser
import psutil
import sys
import os

base = os.path.dirname(os.path.abspath(sys.argv[0]))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(base + "\\debug.log"),
        logging.StreamHandler()
    ]
)

# Load configurations from config.ini
config = configparser.ConfigParser()
config.read(base + '\\ConfigColdTurkey.ini')

# Database configuration
DB_PATH = config['Database']['DB_PATH']

# Block configuration
block_name = config['Block']['block_name']

# Timing configuration (convert to integers)
delay_to_turn_off = int(config['Timing']['delay_to_turn_off'])
error_wait = int(config['Timing']['error_wait'])


def get_connection():
    """Establish a database connection with a timeout and handle exceptions."""
    try:
        return sqlite3.connect(DB_PATH, timeout=10)  # Set a timeout for the connection
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def settings_data(cursor):
    """Fetch settings data from the database."""
    try:
        data = cursor.execute("SELECT * FROM settings").fetchall()
        return data
    except sqlite3.Error as e:
        logging.error(f"Error fetching settings: {e}")
        return None

def switch(cursor, block_name, on=True, data=None):
    """Update the settings to turn a block on or off."""
    try:
        data = data or settings_data(cursor)  # Get settings if not provided
        if not data:
            return
        json_data = json.loads(data[0][1])  # Get settings in JSON
        json_data["blocks"][block_name]["enabled"] = json.dumps(on)  # Adjust
        new_data = json.dumps(json_data, separators=(',', ':'))
        cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (new_data, data[0][0]))
    except (sqlite3.Error, json.JSONDecodeError) as e:
        logging.error(f"Error updating settings: {e}")

def kill_turkey(process_name="Cold Turkey Blocker.exe"):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.terminate()
            logging.warning(f"Terminated {proc.info['name']} (PID: {proc.pid})")
            return True
    return False

def watch(block_name):
    """Watch and update the block settings."""
    while True:
        conn = get_connection() # If getting connection fails.
        if not conn:
            time.sleep(error_wait)  # Wait before retrying connection
            continue
        
        cursor = conn.cursor()
        try:
            data = settings_data(cursor)
            if not data: # Catch Error
                time.sleep(error_wait)
                continue

            all_blocks = json.loads(data[0][1])["blocks"] # JSON -> DICT -> BLOCKS
            if not all_blocks.get(block_name):
                logging.error(f"Block `{block_name}` does not exist. Only exists {list(all_blocks.keys())}. Exiting application...")
                break
            elif all_blocks[block_name]["enabled"] == "false":
                logging.warning(f"Block `{block_name}` detected is OFF!")
                time.sleep(delay_to_turn_off)
                switch(cursor, block_name, on=True, data=data)
                conn.commit()  # Commit the changes after switch
                logging.warning(f"Block `{block_name}` turned back ON after waiting {delay_to_turn_off}s!")
                kill_turkey()
            else:
                logging.info("Block is currently ON!")

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            time.sleep(error_wait)

        conn.close()
        break

if __name__ == "__main__":
    watch(block_name)