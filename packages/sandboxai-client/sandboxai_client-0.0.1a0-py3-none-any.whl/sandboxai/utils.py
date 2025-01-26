import sys
import shutil
import subprocess
import logging


def launch_sandboxd() -> int:
    """
    Launches the sandboxd binary and returns the process ID.
    """
    if not shutil.which("docker"):
        raise RuntimeError("docker not found on the system.")

    # Check if sandboxd binary is on the system.
    # TODO automatically download sandboxd binary if not present.
    if not shutil.which("sandboxd"):
        raise RuntimeError("sandboxd binary not found on the system.")

    # Launch the sandboxd binary in the background
    process = subprocess.Popen(
        ["sandboxd"],
        # TODO(nstogner): Log to disk.
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True,
    )

    # Check if the process started successfully
    if process.poll() is None:
        logging.info("sandboxd started successfully with PID: %d", process.pid)
        return process.pid
    else:
        raise RuntimeError("Failed to launch sandboxd")
