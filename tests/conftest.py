import os
import threading
from time import sleep
import subprocess


def write_py_script(contents):
    open("./tests/file_to_run.py", "w").write(contents)


server_process = None


def run_command():
    open("./tests/file_to_run.py", "w").write(" ")
    global server_process
    server_process = subprocess.Popen(
        ["python", "-m", "hstream", "run", "./tests/file_to_run.py"]
    )
    sleep(2)


def pytest_sessionstart(session):
    print("All tests are about to start. Starting server")
    thread = threading.Thread(target=run_command)
    thread.start()


def pytest_sessionfinish(session, exitstatus):
    global server_process
    if server_process is not None:
        server_process.terminate()
    print("All tests are finished. Stopping server")
    os.remove("./tests/file_to_run.py")
