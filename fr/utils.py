import subprocess


class Info(dict):
    'Dict that acts like an object.'
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


def run(cmd, shell=True, debug=False):
    'Run a command and return the output.'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=shell)
    (out, _) = proc.communicate()  # no need for stderr
    if debug:
        print cmd
        print out
    return out


