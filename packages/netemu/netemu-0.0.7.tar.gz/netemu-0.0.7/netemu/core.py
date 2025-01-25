import os
import ctypes
import signal
import subprocess
from multiprocessing import Process, Pipe

libc = ctypes.CDLL(None)
CLONE_NEWNET = 0x40000000


def _node(ready):
    libc.unshare(CLONE_NEWNET)
    ready.send(True)
    while True:
        try:
            signal.pause()
        except KeyboardInterrupt:
            pass


def _runner(pid, cmds, disown):
    fd = os.open(f"/proc/{pid}/ns/net", os.O_RDONLY)
    libc.setns(fd, CLONE_NEWNET)
    os.close(fd)
    run(cmds, disown)


def run(cmds, disown=False):
    for cmd in cmds:
        if disown:
            subprocess.Popen(cmd)
        else:
            subprocess.run(cmd)


def start_node():
    ready_rcv, ready_snd = Pipe(False)
    proc = Process(target=_node, args=(ready_snd,))
    proc.start()
    assert ready_rcv.recv()
    return proc


def stop_node(proc):
    proc.terminate()
    while True:
        try:
            proc.join()
            break
        except KeyboardInterrupt:
            pass


def run_in_node(proc, cmds, disown=False):
    proc = Process(target=_runner, args=(proc.pid, cmds, disown))
    proc.start()
    while True:
        try:
            proc.join()
            break
        except KeyboardInterrupt:
            proc.terminate()
            print()
