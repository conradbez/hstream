import os
import threading
from time import sleep
import subprocess


def write_py_script(contents):
    open("./tests/file_to_run.py", "w").write(contents)


def kill_server():
    try:
        os.system("kill -9 $(lsof -t -i:9000)")
    except Exception as e:
        print("tried to but could not kill server process")
        print(e)


server_process = None


def run_command():
    kill_server()
    open("./tests/file_to_run.py", "w").write(" ")
    global server_process
    os.environ["PORT"] = "9000"
    server_process = subprocess.Popen(
        [
            "python",
            "-m",
            "hstream",
            "run",
            "./tests/file_to_run.py",
        ]
    )
    sleep(2)


def pytest_sessionstart(session):
    print("All tests are about to start. Starting server")
    thread = threading.Thread(target=run_command)
    thread.start()


def pytest_sessionfinish(session, exitstatus):
    global server_process
    print("All tests are finished. Stopping server")
    if server_process is not None:
        server_process.terminate()
    kill_server()
    os.remove("./tests/file_to_run.py")
