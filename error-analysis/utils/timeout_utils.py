import os
import signal
from subprocess import Popen, PIPE
from threading import Timer


def kill_proc(proc):
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


def run_command(command, timeout_sec=1500):
    """
    Run a shell command with a timeout. If the command takes longer than the timeout, it will be killed.
    
    Parameters:
        command (str): the execution command
        timeout_sec (int): timeout duration in seconds
        
    """

    proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True, preexec_fn=os.setsid)

    timer = Timer(timeout_sec, kill_proc, args=(proc,))
    try:
        timer.start()
        stdout, stderr = proc.communicate()
    finally:
        timer.cancel()
