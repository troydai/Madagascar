#!/usr/bin/env python

import sys
import json
from subprocess import check_output, STDOUT, CalledProcessError


def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('len < 1')
    return sum(data) / float(n)


def sq_deviation(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    return sum((x - c)**2 for x in data)


def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('len < 2')
    ss = sq_deviation(data)
    return (ss / n) ** 0.5


def scenario(command, loop=10, user=None, host=None, venv=None):
    print('Perf run {} on {} as {}. Venv is at {}'.format(command, host, user, venv))

    test_command = 'time -p {} > /dev/null 2>&1'.format(command)
    if user and host and venv:
        test_command = test_command.replace('&', '\\&')
        test_command = 'ssh {}@{} "bash -c \'. {} && {}\'"'.format(
            user, host, venv, test_command)
    
    real = []
    user = []
    syst = []
    for i in range(loop):
        try:
            sys.stderr.write('.')
            sys.stderr.flush()

            lines = check_output(
                test_command, shell=True, stderr=STDOUT, universal_newlines=True).splitlines()
        except CalledProcessError as e:
            lines = e.output.splitlines()

        real.append(float(lines[0].split()[1]))
        user.append(float(lines[1].split()[1]))
        syst.append(float(lines[2].split()[1]))

    sys.stderr.write('\n')
    sys.stderr.flush()

    result = {
        'command': command,
        'iterations': loop,
        'data': {

            'real': {
                'mean': int(mean(real) * 1000),
                'pstdev': int(pstdev(real) * 1000)
            },
            'user': {
                'mean': int(mean(user) * 1000),
                'pstdev': int(pstdev(user) * 1000)
            },
            'sys': {
                'mean': int(mean(syst) * 1000),
                'pstdev': int(pstdev(syst) * 1000)
            }
        }
    }

    return result


if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser('run_perf')
    parser.add_argument('command', help='The command of which the performance to measure.')
    parser.add_argument('-u', help='The user name for ssh connection.', dest='user')
    parser.add_argument('-m', help='The host for ssh connection.', dest='host')
    parser.add_argument('-e', help='The path to the virtual environment on the remote machine', dest='venv')
    parser.add_argument('-l', help='The number of loop in performance.', dest='loop', default=10, type=int)

    arg = parser.parse_args()

    result = scenario(arg.command, loop=arg.loop, user=arg.user, host=arg.host, venv=arg.venv)
    print(json.dumps(result, indent='  '))

