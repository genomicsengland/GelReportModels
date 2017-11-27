import subprocess
import logging
import os
import errno


def run_command(command, fail_if_error=True, cwd=None):
    """
    Runs a given command
    :param command:
    :return:
    """
    if cwd is not None:
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    else:
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = sp.communicate()
    if stdout is not None and stdout != "":
        logging.info(stdout)
    if stderr is not None and stderr != "":
        logging.error(stderr)
    # raise an error if sort return code is other than 0
    if sp.returncode:
        error_message = 'Command [{0}] returned error code [{1}]'.format(command, str(sp.returncode))
        logging.error(error_message)
        if fail_if_error:
            raise ValueError(error_message)

def makedir(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise