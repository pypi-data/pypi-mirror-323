import pymel.core as pm
from cwmaya.windows import window_utils

import json
from cwmaya.helpers import const as k
from contextlib import contextmanager
import subprocess
import platform
import psutil
import time
import urllib.request
import urllib.error
import urllib.parse
 
APP_NAME = "Conductor"


def get_app_locations():
    system = platform.system()
    if system == "Darwin":  # macOS
        return [
            f"/Applications/{APP_NAME}.app",
            f"/Volumes/xhf/dev/cio/cioapp/src-tauri/target/release/bundle/macos/{APP_NAME}.app",
        ]
    elif system == "Windows":
        return [
            f"C:\\Program Files\\{APP_NAME}",
            f"C:\\Users\\{platform.node()}\\AppData\\Local\\{APP_NAME}",
        ]
    elif system == "Linux":
        return [
            f"/usr/local/bin/{APP_NAME}",
            f"/opt/{APP_NAME}",
            f"/home/{platform.node()}/.local/share/{APP_NAME}",
        ]
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")


def is_app_running():
    """Check if a given application is currently running and return its PID."""
    for proc in psutil.process_iter(["name", "pid"]):
        if proc.info["name"] == APP_NAME:
            return True, proc.info["pid"]
    return False, None

############################################### HEALTH
def health_check():
    try:
        response = request_health_check()
        data = {"status_code": response.status, "text": response.read().decode()}
    except urllib.error.URLError as err:
        data = {"error": str(err)}
    window_utils.show_data_in_window(data, title="Desktop app health check")


def request_health_check():
    url = k.DESKTOP_URLS["HEALTHZ"]
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=5)


def is_app_healthy():
    """Check if a given application is currently running"""
    try:
        response = request_health_check()
        if response.status == 200:
            return True
    except Exception as err:
        pass
    return False


##############################################


def navigate(route):
    response = request_navigate_route(route)
    if response.status == 200:
        print(f"Successfully navigated to {route}")
    else:
        pm.error(f"Error navigating to {route}: {response.read().decode()}")


def send_to_composer(node, dialog=None):
    print("send_to_composer")
    if not node:
        print("No node found")
        return

    # Open app if needed
    location, pid = open_desktop_app()
    if pid is None:
        pm.error(f"Could not open or verify {APP_NAME}")
        return

    headers = {"Content-Type": "application/json"}
    url = k.DESKTOP_URLS["COMPOSER"]
    out_attr = node.attr("output")
    print(out_attr)
    pm.dgdirty(out_attr)
    payload = out_attr.get()
    print("Got payload")
    print("Sending payload to", url)
    try:
        req = urllib.request.Request(url, data=payload.encode(), headers=headers)
        response = urllib.request.urlopen(req, timeout=5)
        print("Sent payload")
        if response.status == 200:
            print("Successfully sent payload to composer")
        else:
            pm.error("Error sending payload to composer.", response.read().decode())
    except Exception as err:
        pm.error("Error sending payload to composer.", str(err))
    return response


def request_navigate_route(route):
    if not route.startswith("/"):
        route = f"/{route}"

    url = k.DESKTOP_URLS["NAVIGATE"]
    data = json.dumps({"to": route}).encode()
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    return urllib.request.urlopen(req, timeout=5)

def open_desktop_app():
    """
    Opens the desktop application if it's not already running.
    Returns:
        tuple: (location, pid) of the opened app, or (None, pid) if already running,
               or (None, None) if failed to open
    """
    # Check if already running
    is_running, pid = is_app_running()
    if is_running:
        print(f"{APP_NAME} is already running with PID {pid}.")
        return None, pid

    # Try to open the app if it's not running
    for location in get_app_locations():
        print(f"Trying to open {location}...")
        try:
            process = subprocess.Popen(
                ["open", location],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print(f"Successfully opened {location}")
                time.sleep(2)  # Wait for app to initialize
                
                # Verify the app is healthy
                if is_app_healthy():
                    return location, process.pid
                else:
                    print(f"App opened but health check failed")
            else:
                print(f"Failed to open {location}: {stderr.decode().strip()}")
        except Exception as e:
            print(f"Exception occurred while trying to open {location}: {e}")

    # If we get here, we failed to open the app
    error_msg = f"Failed to open {APP_NAME}"
    window_utils.show_data_in_window({"error": error_msg}, title="Desktop app status")
    return None, None
