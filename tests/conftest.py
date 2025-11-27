import os
import threading
from time import sleep
import subprocess
import tempfile


def write_py_script(contents):
    open("./tests/file_to_run.py", "w").write(contents)


def kill_server():
    try:
        os.system("kill -9 $(lsof -t -i:9000)")
    except Exception as e:
        print("tried to but could not kill server process")
        print(e)


server_process = None
server_log_file = None


def run_command():
    kill_server()
    open("./tests/file_to_run.py", "w").write(" ")
    global server_process, server_log_file
    os.environ["PORT"] = "9000"
    
    # Create a temporary file to capture server output
    server_log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    
    server_process = subprocess.Popen(
        [
            "python",
            "-m",
            "hstream",
            "run",
            "./tests/file_to_run.py",
        ],
        stdout=server_log_file,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )
    sleep(5)  # Increased wait time


def get_server_logs():
    """Read and return server logs from the temporary file."""
    global server_log_file
    if server_log_file:
        # Force flush of subprocess output
        server_log_file.flush()
        # Also sync the filesystem
        os.fsync(server_log_file.fileno())
        with open(server_log_file.name, 'r') as f:
            return f.read()
    return ""


def pytest_sessionstart(session):
    print("All tests are about to start. Starting server")
    # Clean up test log file
    try:
        os.remove('test_strategy_logs.txt')
    except FileNotFoundError:
        pass
    thread = threading.Thread(target=run_command)
    thread.start()
    # Give the thread time to start the server
    sleep(5)


def pytest_sessionfinish(session, exitstatus):
    global server_process, server_log_file
    print("All tests are finished. Stopping server")
    if server_process is not None:
        server_process.terminate()
    if server_log_file:
        server_log_file.close()
        os.unlink(server_log_file.name)
    kill_server()
    os.remove("./tests/file_to_run.py")
