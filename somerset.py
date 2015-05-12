#!/usr/bin/env python
from __future__ import print_function

__version__ = '0.1.1'

import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys

from collections import OrderedDict
from datetime import datetime
from pathlib import Path

# Populated in __main__
STAGES = {}


class StageError(Exception):
    pass


class Tee(object):
    """Contect manager that duplicates stdout and stderr to a file
    """
    # http://stackoverflow.com/a/616686/1773758
    def __init__(self, path):
        self.file = path.open('w', encoding='utf8')
        self.stdout, sys.stdout = sys.stdout, self
        self.stderr, sys.stderr = sys.stderr, self

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        sys.stdout, sys.stderr = self.stdout, self.stderr
        self.file.close()

    def write(self, data):
        # Flush to ensure that data are written to disk
        self.file.write(data)
        self.file.flush()
        self.stdout.write(data)
        self.stdout.flush()


class Stage(object):
    """A stage in a pipeline
    """

    def __init__(self, stage):
        if stage not in STAGES:
            raise StageError('Stage [{0}] not recognised'.format(stage))
        else:
            self.stage = stage
            p = Path(STAGES[stage][-1])
            self.output_dir = p.parent / p.stem

    def _prime(self):
        "Creates self.output_dir. An error is raised if it already exists"
        if self.output_dir.is_dir():
            msg = ('Output directory [{0}] already exists. Has this stage '
                   'already been run?')
            raise StageError(msg.format(self.output_dir))
        else:
            self.output_dir.mkdir()
            return Tee(self.output_dir / 'log.txt')

    def _time_string(self):
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')

    def _finished(self):
        "Makes output files read only"
        for p in (p for p in self.output_dir.rglob('*') if p.is_file()):
            mode = stat.S_IMODE(p.stat().st_mode)
            p.chmod(mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

    def _cmd(self, args):
        "Runs args and waits for it to finish, printing stdout"
        s = subprocess.Popen(args, stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT)
        while True:
            line = s.stdout.readline()
            exitcode = s.poll()
            line = line[:-1]
            if not line and exitcode is not None:
                break
            elif line:
                print(line.decode())

        if exitcode:
            sys.exit(exitcode)

    def run(self):
        "Runs this stage"
        with self._prime():
            print('Stage [{0}] started at [{1}]'.format(self.stage, 
                                                        self._time_string()))
            print('Running somerset [{0}] in Python [{1}] on [{2}] [{3}]'.format(
                        __version__, sys.version, platform.node(), platform.platform()))
            args = STAGES[self.stage]
            if args[0].lower().endswith(('java', 'java.exe')):
                # Sigh...
                self._cmd( [args[0], '-version'] )
            else:
                self._cmd( [args[0], '--version'] )
            self._cmd(args)
            print('Stage [{0}] finished at [{1}]'.format(self.stage,
                                                         self._time_string()))

        self._finished()

def run_all():
    "Runs all stages"
    if not STAGES:
        raise StageError('No stages defined')
    else:
        print('Running all stages')
        for s in STAGES.keys():
            Stage(s).run()
        print('All stages completed')

def remove_all_output():
    "Removed all stage output directories"
    if not STAGES:
        raise StageError('No stages defined')
    else:
        print('Removing all output directories')
        for s in STAGES.keys():
            output_dir = Stage(s).output_dir
            if output_dir.is_dir():
                print('Removing [{0}]'.format(output_dir))
                shutil.rmtree(str(output_dir))
        print('All output directories removed')


def main():
    try:
        import stages
    except ImportError as e:
        print('Unable to import stages.py: {0}'.format(e))
    else:
        global STAGES
        STAGES = OrderedDict((stage, args) for stage, *args in stages.STAGES)

    parser = argparse.ArgumentParser(description='Simple scientific pipelines')
    parser.add_argument("stage", help='The stages to run', nargs='*')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)
    #group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("-l", '--list-stages', action='store_true',
                        help='List all stages')
    parser.add_argument('-r', '--remove-all-output', action='store_true',
                        help='Remove all stage output directories')
    args = parser.parse_args()

    if args.list_stages:
        for key, command_line in STAGES.items():
            print(key, command_line)
        print('all')
    elif args.remove_all_output:
        res = input('Are you sure you want to remove all output directories (y/N)?')
        if 'y'==res.lower():
            remove_all_output()
        else:
            print('No action taken')
    elif 1 == len(args.stage) and 'all'==args.stage[0].lower():
        run_all()
    elif args.stage:
        for stage in args.stage:
            Stage(stage).run()
    else:
        parser.print_help()


if __name__=='__main__':
    main()
