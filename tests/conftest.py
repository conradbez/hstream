import os
import threading
from time import sleep


def write_py_script(contents):
    open("./tests/file_to_run.py", "w").write(contents)


def run_command():
    open("./tests/file_to_run.py", "w").write(" ")
    os.system("python -m hstream run ./tests/file_to_run.py")
    sleep(2)


def pytest_sessionstart(session):
    print("All tests are about to start. Starting server")
    thread = threading.Thread(target=run_command)
    thread.start()
    return


def pytest_sessionfinish(session, exitstatus):
    os.system("kill -9 $(lsof -t -i:8000)")
    print("All tests are finished. Stopping server")
