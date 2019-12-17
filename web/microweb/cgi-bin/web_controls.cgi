#!/usr/bin/python

#
# Licensed under the BSD license.  See full license in LICENSE file.
# http://www.lightshowpi.org/
#
# Author: Ken B

import cgi
import cgitb
import os
from time import sleep
import sys
import logging

# This script is run by SUDO! Make sure sudo python has the appropriate libraries, paths, etc.
# Broadlink path set in /etc/sudoers
# Defaults        env_keep=SYNCHRONIZED_LIGHTS_HOME
# Defaults        env_keep+=BROADLINK

broadlink = os.getenv("BROADLINK")
sys.path.append(broadlink)

logger = logging.getLogger("root")
logger.info(broadlink)
logger.info(sys.version_info)

import send_commands
send_commands.logger
connection = send_commands.connect()

cgitb.enable()  # for troubleshooting
form = cgi.FieldStorage()
message = form.getvalue("message", "")

print "Content-type: text/html"
print

print """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>LightShowPi Web Controls</title>
        <meta name="description" content="A very basic web interface for LightShowPi">
        <meta name="author" content="Ken B">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" href="/favicon.png">
        <meta name="mobile-web-app-capable" content="yes">
        <link rel="icon" sizes="196x196" href="/favicon.png">
        <link rel="apple-touch-icon" sizes="152x152" href="/favicon.png">
        <link rel="stylesheet" href="/css/style.css">
    </head>
    <body>
        <center>
            <h1> LightShowPi Web Controls </h1>

            <form method="post" action="web_controls.cgi">
                <input type="hidden" name="message" value="On"/>
                <input id="on" type="submit" value="Lights ON">
            </form>
            
            <form method="post" action="web_controls.cgi">
                <input type="hidden" name="message" value="Off"/>
                <input id="off" type="submit" value="Lights OFF">
            </form>

""" 

if message:
    if message == "On":
        os.system('pkill -f "bash $SYNCHRONIZED_LIGHTS_HOME/bin"')
        os.system('pkill -f "python $SYNCHRONIZED_LIGHTS_HOME/py"')
        os.system("python ${SYNCHRONIZED_LIGHTS_HOME}/py/hardware_controller.py --state=on")
    if message == "Off":
        os.system('pkill -f "bash $SYNCHRONIZED_LIGHTS_HOME/bin"')
        os.system('pkill -f "python $SYNCHRONIZED_LIGHTS_HOME/py"')
        os.system("python ${SYNCHRONIZED_LIGHTS_HOME}/py/hardware_controller.py --state=off")
    if message == "Next":
        os.system('pkill -f "python $SYNCHRONIZED_LIGHTS_HOME/py"')
        sleep(1)
    if message == "Speakers On":
        send_commands.send_command_server(connection, "Speakers", "on")
        #os.system("python ${BROADLINK}/send_commands.py --on Speakers")
        #os.system("echo 'broadlink: ${BROADLINK}'")
        sleep(1)
    if message == "Speakers Off":
        send_commands.send_command_server(connection, "Speakers", "off")
        #os.system('python ${BROADLINK}/send_commands.py --off Speakers')
        sleep(1)
    if message == "System Off":
        #os.system('python ${BROADLINK}/send_commands.py --off Speakers')
        send_commands.send_command_server(connection, "Speakers", "off")
        os.system('pkill -f "bash $SYNCHRONIZED_LIGHTS_HOME/bin"')
        os.system('pkill -f "python $SYNCHRONIZED_LIGHTS_HOME/py"')
        os.system("python ${SYNCHRONIZED_LIGHTS_HOME}/py/hardware_controller.py --state=off")
        sleep(1)

    if message == "Start":
        send_commands.send_command_server(connection, "Speakers", "on")
        os.system('pkill -f "bash $SYNCHRONIZED_LIGHTS_HOME/bin"')
        os.system('pkill -f "python $SYNCHRONIZED_LIGHTS_HOME/py"')
        os.system("${SYNCHRONIZED_LIGHTS_HOME}/bin/play_sms &")
        os.system("${SYNCHRONIZED_LIGHTS_HOME}/bin/check_sms &")
        sleep(1)

cmd = 'pgrep -f "python $SYNCHRONIZED_LIGHTS_HOME/py/synchronized_lights.py"'
if os.system(cmd) == 0:
    print """
        <form method="post" action="web_controls.cgi">
            <input type="hidden" name="message" value="Next"/>
            <input id="next" type="submit" value="Play Next">
        </form>
"""
else:
    print """
        <form method="post" action="web_controls.cgi">
            <input type="hidden" name="message" value="Start"/>
            <input id="start" type="submit" value="START">
        </form>
"""

## Speakers
print("""
            <form method="post" action="web_controls.cgi">
                <input type="hidden" name="message" value="Speakers On"/>
                <input id="speakers_on" type="submit" value="Speakers ON">
            </form>

             <form method="post" action="web_controls.cgi">
                <input type="hidden" name="message" value="Speakers Off"/>
                <input id="speakers_off" type="submit" value="Speakers OFF">
            </form>

        <form method="post" action="web_controls.cgi">
            <input type="hidden" name="message" value="System Off"/>
            <input id="system_off" type="submit" value="OFF">
        </form>
""")

if message:
    print """<h2>Executed command: %s</h2>""" % cgi.escape(message)

print "</body></html>"
