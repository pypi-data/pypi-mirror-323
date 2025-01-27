#!/usr/bin/env python
import os
import glob
import subprocess
from pantarei.parsers import parse_yaml, parse_pickle
from pantarei.core import logos, _colors
from pantarei.helpers import rmd, rmf

# Internal helper functions

def _state(path):
    job_file = os.path.join(path, 'job.yaml')
    task_file = os.path.join(path, 'task.yaml')
    state = ''
    if not os.path.exists(job_file):
        if os.path.exists(task_file):
            db = parse_yaml(task_file)
            if 'task_end' in db:
                state = 'ended'
            elif 'task_start' in db:
                state = 'running'
            elif len(db) == 0:
                state = 'unknown'
    else:
        db = parse_yaml(job_file)
        if 'job_fail' in db:
            state = 'failed'
        elif 'job_end' in db:
            state = 'ended'
        elif 'job_start' in db:
            state = 'running'
        elif 'job_queue' in db:
            state = 'queued'
        elif len(db) == 0:
            state = 'unknown'
        else:
            raise ValueError(f'wrong state {list(db.keys())} in {path}')
    return state

def _kind(path):
    job_file = os.path.join(path, 'job.yaml')
    task_file = os.path.join(path, 'task.yaml')
    if os.path.exists(job_file):
        return 'job'
    if os.path.exists(task_file):
        return 'task'
    return 'unknown'

def _duration(path):
    # TODO: refactor, code is duplicated in Job
    """Current duration of job. If job is ended, return the elapsed duration"""
    import time
    import datetime

    db = {}
    task_file = os.path.join(path, 'task.yaml')
    if not os.path.exists(task_file):
        return datetime.timedelta(seconds=0)
    db.update(parse_yaml(task_file))

    job_file = os.path.join(path, 'job.yaml')
    if os.path.exists(job_file):
        db.update(parse_yaml(job_file))

    if 'task_start' in db and 'task_end' in db:
        delta = float(db['task_end']) - float(db['task_start'])
    elif 'job_start' in db and 'job_fail' in db:
        delta = float(db['job_fail']) - float(db['job_start'])
    elif 'task_start' in db:
        delta = time.time() - float(db['task_start'])
    else:
        delta = 0
    return datetime.timedelta(seconds=int(delta))

def _split_names(path):
    root, base = os.path.split(path.rstrip('/'))
    root, func_tag = os.path.split(root.rstrip('/'))
    qn = func_tag + '/' + base
    func_tag = func_tag.split('-')
    if len(func_tag) == 1:
        func, tag = func_tag[0], ''
    else:
        func = func_tag[0]
        tag = '-'.join(func_tag[1:])
    return func, tag, qn

def _arguments(path):
    job_file = os.path.join(path, 'arguments.pkl')
    if os.path.exists(job_file):
        return parse_pickle(job_file)
    return {}

def _artifacts(path):
    if os.path.exists(os.path.join(path, 'arguments.pkl')):
        args = parse_pickle(os.path.join(path, 'arguments.pkl'))
        if "artifacts" in args:
            return args["artifacts"].format(**args)
    if os.path.exists(os.path.join(path, 'results.pkl')):
        results = parse_pickle(os.path.join(path, 'results.pkl'))
        if isinstance(results, dict) and 'artifacts' in results:
            return results['artifacts']
    return ''

def _lines(script, verbose=False):
    # TODO: better use python3
    mode = 'pantarei=timid pantarei_report=1'
    output = subprocess.check_output(f'{mode} python {script}', shell=True)
    output = output.decode().strip().split('\n')
    if verbose:
        print('\n'.join(output))
    try:
        line = output.index('# pantarei paths:')
        lines = output[line+1:]
        return lines
    except ValueError:
        return []

def _public_args(x):
    return {key: value for key, value in x.__dict__.items() if not key.startswith('_')}

def _run_command(cmd):
    # TODO: add check=True?
    results = subprocess.run(cmd, shell=True, capture_output=True)
    if results.returncode != 0:
        print(results.stderr.decode())
        raise RuntimeError(f'command failed: {cmd}')

# Internal class to recreate readonly job instances

class _Job:

    def __init__(self, path):
        self.path = path
        self._setup(path)

    def _setup(self, path):
        self.state = _state(path)
        self.duration = _duration(path)
        self.name, self.tag, self.qualified_name = _split_names(path)
        self.artifacts = _artifacts(path)
        self.logo = logos[self.state]
        self.kind = _kind(path)

        if self.state == '':
            self.kwargs = []
            self.pretty_name = f'{self.name}(...?...)'
        else:
            self.kwargs = _arguments(path)
            args = []
            for key in self.kwargs:
                # if self.task.ignore is not None:
                #     if key in self.task.ignore:
                #         continue
                if isinstance(self.kwargs[key], str):
                    args.append(f'{key}="{self.kwargs[key]}"')
                else:
                    args.append(f'{key}={self.kwargs[key]}')
            kwargs = ','.join(args)
            self.pretty_name = f'{self.name}({kwargs})'

        # if os.path.join(os.path.dirname(path), 'metadata.pkl'):
        #     func_md = parse_pickle(os.path.join(os.path.dirname(path), 'metadata.pkl'))
        # self.docstring = func_md['docstring']
        # self.signature_args = func_md['args']
        # self.signature_kwargs = func_md['kwargs']

# TODO: this is not used here, should we keep it? or move it to helpers?
def load_from_path(path):
    from pantarei.parsers import parse_yaml, parse_pickle

    if os.path.join(path, 'task.yaml'):
        task_md = parse_yaml(os.path.join(path, 'task.yaml'))
    if os.path.join(path, 'job.yaml'):
        job_md = parse_yaml(os.path.join(path, 'job.yaml'))
    if os.path.join(path, 'arguments.pkl'):
        args = parse_pickle(os.path.join(path, 'arguments.pkl'))
    if os.path.join(path, 'results.pkl'):
        results = parse_pickle(os.path.join(path, 'results.pkl'))
    if os.path.join(os.path.dirname(path), 'metadata.pkl'):
        func_md = parse_pickle(os.path.join(os.path.dirname(path), 'metadata.pkl'))
    # print(task_md)
    # print(job_md)
    # print(args)
    # print(results)

    root, base = os.path.split(path.rstrip('/'))
    root, func_tag = os.path.split(root.rstrip('/'))
    qn = func_tag + '/' + base
    func_tag = func_tag.split('-')
    if len(func_tag) == 1:
        func, tag = func_tag[0], ''
    else:
        func, tag = func_tag
    from pantarei.task import Task
    task = Task(None, name=func, tag=tag,
                qualified_name=qn,
                docstring=func_md['docstring'],
                signature_args=func_md['args'],
                signature_kwargs=func_md['kwargs'])
    # TODO: arghhhh, the qualified name takes only the non-default arguments
    # but in arguments.yaml we give all the arguments.
    # So atm we cannot reconstruct the task from the dataset... :-(

    # 1. if we stored the function, we could strip the default arguments (difficult)
    # 2. also store the explicit kwargs in a separate yaml (but careful to hide it)
    # 3. do not store the default arguments
    # 4. allow the fqn as argment in the constructor and use it in the property in case

    # We should stick to the non default args. The reason is:
    # if we add an optional argument to a function, we do not want the fqn to change!
    # We want it to be backward compatible.
    # TODO: for the artifacts we need the function... because of these
    # all_kwargs = all_actual_kwargs(self.func, *args, **kwargs)
    # kwargs = actual_kwargs(self.func, *args, **kwargs)
    # name = self.qualified_name(**kwargs)
    # I think we cannot keep Task, we need a custom artifacts accessor
    # The reason is that in Task we always look up the passed arguments
    # but doing this requires to inspect the function signature.
    # Could we bypass the above wrapping if we only pass kwargs?
    # Note we must pass all kwargs...
    # We could simply dill the function... so point 1. above.
    # Actually, it would be useful to at least have the docstring
    # we could store globally the default arguments
    # Then in the task constructor we should store the signature and / or the default arguments
    # In the other calls we would not need to store anything

    # args = {key: value for key, value in args.items()}

    print(task.name(), ':', task.doc, args, 'artifacts:', task.artifacts(**args))

# Main functions for command line interface

def _run_pantarei(cmd, mode):
    import subprocess
    # TODO: careful here, this way of calling will propagate the env
    # vars down to the very script which is submitted. So either we
    # clear them there, or they will interfere with the path report.
    # It should not matter for the job because we execute the task,
    # but still it is not good.

    if cmd[0].startswith('python'):
        # Check that the script exists
        assert os.path.exists(cmd[1])

    if len(cmd) == 1:
        # This must be the path to a script
        # If not executable, we use python3 to execute it
        assert os.path.exists(cmd[0])
        if not os.access(cmd[0], os.X_OK) or not cmd[0].startswith('./'):
            cmd = ['python3'] + list(cmd)

    cmd = ' '.join(cmd)
    output = subprocess.check_output(f'{mode} {cmd}', shell=True)
    return output

def run(cmd, dry=False, scratch=False, quiet=False):
    import sys

    if len(cmd) == 0:
        print('Provide at least one script as argument')
        sys.exit(1)

    mode = ''
    if dry:
        mode = 'pantarei=timid'
    if scratch:
        mode = 'pantarei=scratch'
    output = _run_pantarei(cmd, mode)

    if not quiet:
        # For some reason the output is b'', but decoding it
        # produces a white space that cannot be stripped.
        # So we test this case manually
        if output != b'':
            print(output.decode())

def _is_script(cmd):
    return cmd == 'python' or (os.path.exists(cmd) and cmd.endswith('.py'))

def rm(cmd, all=False, pretend=False):
    assert len(cmd) > 0
    if _is_script(cmd[0]):
        # This is a script, we rely on pantarei modes
        mode = 'pantarei=clean'
        if all:
            mode = 'pantarei=veryclean'
        _run_pantarei(cmd, mode)
    else:
        # These are job names, we scrape the database
        paths = cmd
        for path in _normalize(_paths(paths)):
            if not pretend:
                rmd(path)
            else:
                print(f'cache for "{path}" would be removed')
            # TODO: job.artifacts returns None
            if len(_artifacts(path)) > 0:
                if not pretend:
                    rmd(_artifacts(path))
                    rmf(_artifacts(path))
                else:
                    print(f'artifact "{_artifacts(path)}" for "{path}" would be removed')


# TODO: summary could show the artfiacts total size
def ls(cmd, attrs='', oneline=False, no_header=False,    
       _long=False, no_long=False, stats=False, no_stats=False, no_details_num=10,
       args='', artifacts=False, state='failed', fmt=''):
    from pantarei.core import _report, _report_oneline, _report_summary

    if state == 'all':
        # TODO: there should be no '' state
        state = ('failed', 'ended', 'queued', 'running', 'unknown', '')
    else:
        state = state.split(',')

    # Format for printing jobs attributes
    if attrs:
        fmt = [_.strip() for _ in attrs.split(',')]
        fmt = ' '.join(['{' + _ + '}' for _ in fmt])
    # It implies summary is False
    if fmt:
        no_header = True

    max_len = max(len(_ + args) for _ in cmd)
    for script in cmd:
        if _is_script(script):
            # Get the script's jobs
            lines = _lines(script + ' ' + args)
        else:
            # This should be a cache path
            no_header = True
            lines = _normalize(_paths(script))

        jobs = []
        for path in lines:
            job = _Job(path)
            jobs.append(job)

        # Disable details if there are more than no_details_num jobs
        if len(jobs) > no_details_num and not _long:
            no_long = True

        # Disable stats and details if all the jobs have ended
        if not no_stats:
            n = sum(_public_args(job)['state'] == 'ended' for job in jobs)
            if len(jobs) == n:
                if not stats:
                    no_stats = True
                if not _long:
                    no_long = True

        # Summary of script
        if not no_header:
            line = _report_oneline(jobs)
            line = line.split()
            begin, end = _colors.BOLD, _colors.END
            if len(line) == 0:
                print('  ', f'{begin}{script + " " + args:{max_len}}{end} NaN [0/0]')
                return
            print(line[0], f'{begin}{script + " " + args:{max_len}}{end}', ' '.join(line[1:]))

        # Custom job report
        if fmt:
            for job in jobs:
                kwargs = _public_args(job)
                if kwargs['state'] in state:
                    print(fmt.format(**kwargs))
            continue

        # Summary of jobs by state
        if not oneline and not no_stats:
            output = _report_summary(jobs)
            if len(output) > 0:
                print('\n'.join(output))

        # Oneline disables the individual jobs report
        # TODO: merge this with the lines above using a default fmt?
        # This is a bit cumbersome because of the handling of color/bold
        if not oneline and not no_long:
            output = _report(jobs, only=state)
            if len(output) > 0:
                print('\n'.join(output))

        # Artifacts report only
        if artifacts:
            for job in jobs:
                if job.artifacts is not None:
                    print(job.artifacts)

def _normalize(paths):
    """Add cache prefix and autocomplete cache paths"""
    path_db = '.pantarei'
    if isinstance(paths, str):
        paths = [paths]
    paths_tmp = []
    for path in paths:
        if not path.startswith(path_db):
            path = os.path.join(path_db, path)
        # If there are no globbable symbols in the path
        # it means we are just shortening the hash, like
        #  rei ls f/das12
        # Hence, we make sure the result is unique. This is
        # different from say
        #  rel ls f/*
        # where we actually want to find all entries of f
        if '*' not in path:
            path_tmp = glob.glob(path + '*')
            assert len(path_tmp) == 1
            paths_tmp += path_tmp
        else:
            paths_tmp += glob.glob(path)
    return paths_tmp


def cat(paths, attrs='output', header='\033[4m{attr_file}\033[0m', tail=0, args='',
        state='all'):
    path_db = '.pantarei'
    if state == 'all':
        # TODO: there should be no '' state
        state = ('failed', 'ended', 'queued', 'running', 'unknown', '')
    else:
        state = state.split(',')
    attrs = attrs.split(',')
    files = {
        'output': ['job.out', 'job.out.gz'],
        #'arguments': '.arguments.yaml',
        'arguments': 'arguments.pkl',
        'metadata': ['task.yaml', 'job.yaml'],
        #'results': '.results.yaml'
        'results': 'results.pkl'
    }
    if attrs == 'all':
        attrs = list(files.keys())

    # Add cache prefix and autocomplete cache paths
    # paths = _normalize(paths)

    # Now go throuh each given cache path
    # for path in _paths(paths):
    #for script in cmd:
    script = paths[0]
    if _is_script(script):
        # Get the script's jobs
        paths = _lines(script + ' ' + args)
    else:
        # This should be a cache path
        paths = _normalize(_paths(paths))
    for path in paths:
        job = _Job(path)
        kwargs = _public_args(job)
        if kwargs['state'] not in state:
            continue
        print(_colors.BOLD + path + _colors.END)

        for attr in attrs:
            attr_files = files[attr]
            if not isinstance(attr_files, list):
                attr_files = [attr_files]

            for attr_file in attr_files:
                # TODO: refactor as normalize path
                _attr_file = os.path.join(path, attr_file)
                # # Add database root path if missing
                # if not _attr_file.startswith(path_db):
                #     _attr_file = os.path.join(path_db, _attr_file)
                if not os.path.exists(_attr_file):
                    continue
                kwargs = locals()
                print(header.format(**kwargs))
                if _attr_file.endswith('.pkl'):
                    import yaml
                    import pickle
                    from .cache import _itemize
                    with open(_attr_file, 'rb') as fh:
                        content = pickle.load(fh)
                        content = yaml.dump(_itemize(content))
                else:
                    from .helpers import _PossiblyZippedFile
                    with _PossiblyZippedFile(_attr_file) as fh:
                        content = fh.read()
                content = content.strip()
                if len(content) > 0:
                    if attr_file == 'job.out':
                        print('\n'.join(content.split('\n')[-int(tail):]))
                    else:
                        print(content)
        print()

def _copy(path, dest, strip_tmp=False):
    if not os.path.exists(path):
        print(f'skipping non-existed job path: {path}')
        return

    _run_command(f'rsync -uvaR ././{path} {dest}')

    job = _Job(path)
    if job.artifacts is not None:
        source = job.artifacts
        if strip_tmp and source.startswith('/tmp/'):
            source = source[5:]

        if os.path.exists(source):
            if job.artifacts.startswith('/'):
                _run_command(f'rsync -uvaR {source} {dest}')
            else:
                _run_command(f'rsync -uvaR ././{source} {dest}')
        else:
            print(f'skipping non-existed job artifacts: {source}')
            return

def _paths(paths):
    if len(paths) == 1 and paths[0] == '-':
        import sys
        paths = [path.rstrip() for path in sys.stdin]
    return paths


def copy(paths, dest, strip_tmp=False, args=''):
    # If we pass a script, we grab the job paths
    # and then proceed
    if len(paths) == 1 and os.path.isfile(paths[0]):
        paths = _lines(paths[0] + ' ' + args)

    # We now have a list of job paths
    for path in _paths(paths):
        _copy(path, dest, strip_tmp=strip_tmp)

# Main CLI driver

def main():
    # This could be coded like this
    #
    #   import argh
    #   argh.dispatch_commands([run, ls, cp, cat, rm])
    #
    # but I'd rather not have yet another dependency for something
    # that is trivial, if somewhat verbose, to code explicitly like a
    # parser. So I just go the old argparse way. Also, argh developed
    # a tendency to backward incompatibilty and I do not want to mess
    # with that.
    import argparse

    class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                        argparse.RawDescriptionHelpFormatter
                        ):
        pass

    cmd_help = "Python script (possibly followed by command line arguments) or scripts to execute"
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    # Run command
    sub = subparser.add_parser("run",
                               formatter_class=HelpFormatter,
                               help="Run script(s) with different pantarei modes",
                               description="""\
Run a script (or multiple ones) containing pantarei tasks or jobs.
Arguments can be used to clean up the tasks' cache and/or artifacts,
or to make a dry run.

Examples:

Run a single script:
>  rei run project.py

Specify the interpreter:
> rei run python project.py

Pass arguments to the script:
> rei run project.py --verbose

Run multiple scripts one after the other:
> rei run project*.py

Pretend to run the jobs (dry run):
> rei run --dry project.py

Rerun all the jobs from scratch, cleaning up the cache:
> rei run --scratch project.py
""")
    arg = sub.add_argument
    arg("--dry", action="store_true", help="Dry run, do not run the tasks")
    arg("--scratch", action="store_true", help="Clean up all the tasks' cache and execute them from scratch")
    arg("--quiet", action="store_true", help="Do not print any output")
    arg("cmd", nargs="+", help=cmd_help)
    sub.set_defaults(func=run)

    # List command
    sub = subparser.add_parser("list",
                               aliases=["ls", "summary"],
                               formatter_class=HelpFormatter,
                               help="List the state of jobs in script(s)",
                               description="""\
List the state of jobs in one or multiple scripts.
The attributes of the jobs to dump can be selected with the --attrs argument.
The output can be customized with the  --fmt flag, parsed with grep / awk, piped into the cat subcommand.

Examples:

List jobs from a single script
> rei ls script.py

List failed jobs only from multiple scripts
> rei ls --state failed script*.py

Print one-line summaries only for multiple scripts
> rei ls --oneline script*.py

List jobs matching a (partial) hash
> rei ls f/3de5a94

List all jobs of a given function
> rei ls f/*

List all jobs of multiple functions, which may differ by tag
> rei ls f*/*

List the tasks' state and qualified name:
> rei report --attrs state,qualified_name script.py

List the jobs artifacts for ended jobs:
> rei ls --artifacts --state ended script.py
""")
    arg = sub.add_argument
    arg("--attrs", default='', help="Jobs attributes to print.\
Possible values: all, path, name, state, qualified_name, artifacts")
    arg("--oneline", action='store_true', help="One line report per job")
    arg("--no-header", "-H", action='store_true', help="Disable overall summary per script")
    arg("--no-long", action='store_true', help="Do not show details on jobs")    
    arg("--long", "-l", dest='_long', action='store_true', help="Show details on jobs")
    arg("--stats", "-s", action='store_true', help="Show stats per script")
    arg("--no-stats", "-S", action='store_true', help="Disable stats per script")
    arg("--artifacts", action='store_true', help="Print artifacts")
    arg("--state", default='all', help="Attributes of tasks/jobs to report (comma separated).\
Possible values: ended, running, queued, failed, all")
    arg("--args", default='', help="Command line arguments to pass to each script")
    arg("--fmt", default='', help="Formatting string")
    arg("cmd", nargs="+", help=cmd_help)
    sub.set_defaults(func=ls)

    # Concatenate command
    sub = subparser.add_parser("concatenate",
                               aliases=["cat"],
                               formatter_class=HelpFormatter,
                               help="Concatenate jobs' output and/or metadata",
                               description="""\
Concatenate the output and/or metadata of jobs, from the full <path> to the pantarei job.
The path can be found from the "path" job attribute, using rei ls.

Examples:

Show output of all jobs in a script
> rei cat script.py

Show output of jobs matching a (partial) hash
> rei cat f/3dsa

Show output of jobs associated to a function
> rei cat f/*

Inspect failed jobs in script piping results from rei ls:
> rei ls --attrs path --state failed script.py | xargs rei cat

Inspect all the jobs of a script:
> rei ls --attrs path script.py | xargs rei cat --attrs arguments,metadata,output

""")
    arg = sub.add_argument
    arg = sub.add_argument
    arg("--attrs", default='output', help="Jobs attributes to print")
    arg("--tail", default=0, help="Show only the last TAIL lines of output")
    arg("--state", default='all', help="Attributes of tasks/jobs to report (comma separated).\
Possible values: ended, running, queued, failed, all")
    arg("paths", nargs="+", help="Paths to jobs in pantarei cache")
    sub.set_defaults(func=cat)

    # Remove command
    sub = subparser.add_parser("remove",
                               aliases=["rm"],
                               formatter_class=HelpFormatter,
                               help="Remove cache and artifacts of jobs in script(s)",
                               description="""\
Remove the tasks' cache and/or artifacts. By default, only failed jobs are cleaned up.

Examples:

Remove the cache of failed jobs associated to a script:
> rei rm project.py

Remove all cache associated to a script:
> rei rm --all project.py
""")
    arg = sub.add_argument
    arg("--all", action="store_true", help="Clean up all tasks' cache and artifacts")
    arg("--pretend", action="store_true", help="Do not actually remove anything")
    arg("cmd", nargs="+", help=cmd_help)
    sub.set_defaults(func=rm)

    # Copy command
    sub = subparser.add_parser("copy",
                               aliases=["cp"],
                               formatter_class=HelpFormatter,
                               help="Copy tasks' cache or artifacts somewhere else",
                               description="""\
Copy tasks' cache somewhere else.
This will also copy jobs' artifacts, if present.
""")
    arg = sub.add_argument
    arg("paths", nargs="+", help="Paths to jobs in pantarei cache to be copied")
    arg("dest", help="Path (possibly a remote one) where the cache will be copied")
    arg("--strip-tmp", action='store_true')
    sub.set_defaults(func=copy)

    # Parse and run the command
    ns = parser.parse_args()
    kwargs = vars(ns)
    if 'func' in kwargs:
        func = kwargs.pop('func')
        func(**kwargs)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
