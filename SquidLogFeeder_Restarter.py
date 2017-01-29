#!/usr/bin/python

# Make all the necessary `MODULE` imports here.
import subprocess, re, os, signal

# Below is the `GREP` operation we need to perform.
# root 28869 28868   0 04:41:32 ?           0:03 tail -f /opt/squid/log/access.log
TAIL_PATTERN = 'root\s+[0-9]+\s+[0-9]+\s+0\s+([0-9]+:[0-9]+:[0-9]+|[A-Za-z]+\s+[0-9]+)\s+\?\s+[0-9]+:[0-9]+\s+' +\
               'tail\s-f\s/opt/squid/log/access.log'

# Get hold of all the current running processes.
# We will filter out the tail process for the corresponding `SQUID_SYS` script.
def grep_tail():
    ps_pipe = subprocess.Popen(['ps -ef'], shell=True, stdout=subprocess.PIPE)
    ps_out  = ps_pipe.communicate()[0]
    return re.search(TAIL_PATTERN, ps_out).group(0)

try:
    # `GREP` the `TAIL` process.
    executing_tail = grep_tail()

    # Get the PID and PPID for the `SQUID_SYS` and `TAIL` processes.
    get_pid_ppid = re.compile('\d+')
    tail_extract = get_pid_ppid.findall(executing_tail)
    pid, ppid =  tail_extract[0], tail_extract[1]
    print '--> Killing PID:', pid, '& PPID:', ppid

    # Delete the list created from the `TAIL` grep operation.
    # It's good to use the system memory wisely.
    del tail_extract

    # Kill the current `SQUID_SYS` and `TAIL` processes.
    os.kill(int(ppid), signal.SIGKILL)
    os.kill(int(pid), signal.SIGKILL)

    # Re-verify by calling `GREP`.
    # The Regular-Expression should return <None>.
    try:
        tail_still_executing = grep_tail()
    except AttributeError, e:
        tail_still_executing = None
    if tail_still_executing is None:
        print '--> Successfully Killed `SQUID_SYS` and `TAIL`'
    else:
        raise OSError

    try:
        # Re-Invoke the `SQUID_SYS` utility.
        # We want to spawn it as a seperate/independent process
        # Re-direct `STDOUT` & `STDERR` streams to `NULL_DEVICE`
        devnull = open(os.devnull, 'wb')
        subprocess.Popen(['nohup', '/etc/init.d/squid_sys.sh', '&'], stdout=devnull,stderr=devnull)
    except subprocess.CalledProcessError, e:
        print '--> SQUID_SYS::STARTUP::FAILED', e

except (subprocess.CalledProcessError, OSError), e:
    print '--> SQUID_SYS::CLEANUP::FAILED::', e
