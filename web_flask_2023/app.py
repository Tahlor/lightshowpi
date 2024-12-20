import sys
from flask import Flask, request, render_template, redirect, url_for, flash
import os
import subprocess
import logging
from time import sleep
import shlex
from subprocess import Popen

app = Flask(__name__)

app.secret_key = 'DSAREYUIY%$#$%^TREWSRYU876543'

# Configure Logger
logger = logging.getLogger("lightshowpi")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set environment variables
HOME = os.environ.get('SYNCHRONIZED_LIGHTS_HOME', '/home/pi/lightshow2022')
BROADLINK = os.environ.get('BROADLINK', '/home/pi/Projects/broadlink')
ON_OFF_SCRIPT=f"{HOME}/py/hardware_controller.py"
ON_OFF_SCRIPT=f"{HOME}/py/on_or_off.py"
ENV = os.environ.copy()
ENV['SYNCHRONIZED_LIGHTS_HOME'] = HOME  # Ensure this env var is set

# Importing send_commands module (Adjust the path as per your environment)
sys.path.append(BROADLINK)
import send_commands

def connect():
    try:
        connection = send_commands.connect("localhost", port=39554)
        logger.info("Connected to local relay server")
        return connection
    except Exception as e:
        logger.warning(f"Couldn't connect to server: {e}")
        return False

@app.route('/')
def root():
    return redirect(url_for('index'))


@app.route('/lightshowpi/', methods=['GET', 'POST'])
@app.route('/lightshowpi', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message')
        execute_command(message)
        # Redirect to the external URL
        flash(f'Command "{message}" executed successfully!', 'success')  # Send a flash message
        return redirect(url_for('index', _external=True))

    # For GET request or initial load
    return render_template('index.html')

def execute_command(command):
    connection = connect()

    if command == "On":
        kill_processes()
        Popen([sys.executable, ON_OFF_SCRIPT, "--state=on"],
              env=ENV, cwd=HOME)
    elif command == "Off":
        kill_processes()
        Popen([sys.executable, ON_OFF_SCRIPT, "--state=off"],
              env=ENV, cwd=HOME)
    elif command == "Next":
        kill_processes()
        sleep(1)
    elif command == "Speakers On":
        if connection:
            send_commands.send_command_server(connection, "Speakers", "on", confirm=False)
    elif command == "Speakers Off":
        if connection:
            send_commands.send_command_server(connection, "Speakers", "off", confirm=False)
    elif command == "System Off":
        if connection:
            send_commands.send_command_server(connection, "Speakers", "off", confirm=False)
        kill_processes()
    elif command == "Start":
        connection = connect()
        if connection:
            send_commands.send_command_server(connection, "Speakers", "on", confirm=False)
            logger.info("Sent command to turn on speakers (part of Start)")

        # Kill existing processes
        kill_processes()

        # Start new processes in background with full path expansion
        Popen(['/bin/bash', f"{HOME}/bin/play_sms"], env=ENV, cwd=HOME)
        Popen(['/bin/bash', f"{HOME}/bin/check_sms"], env=ENV, cwd=HOME)

def kill_processes():
    try:
        # Use sudo to kill processes. Requires passwordless sudo for these specific commands
        Popen(['sudo', 'pkill', '-f', f'bash.*{HOME}/bin'], env=ENV, cwd=HOME)
        Popen(['sudo', 'pkill', '-f', f'python.*{HOME}/py'], env=ENV, cwd=HOME)
        sleep(0.5)  # Give processes time to clean up
    except Exception as e:
        logger.error(f"Error during kill process: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8283)
