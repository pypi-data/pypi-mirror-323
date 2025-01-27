"""
Core functions
"""
import os
import glob
import atexit

# Possible modes: safe, brave, timid, clean, veryclean
mode = 'safe'
if 'PANTAREI' in os.environ:
    mode = os.environ['PANTAREI']
if 'pantarei' in os.environ:
    mode = os.environ['pantarei']

# logos = {'failed': '[*]',
#          'ended': '[X]',
#          'running': '[/]',
#          'queued': '[-]',
#          'unknown': '[?]',
#          '': '[ ]'}
logos = {'failed': '❌',
         'ended': '✅',
         'running': '⭐', # u'⚡',
         'queued': '⛔',
         'unknown': '❓',
         '': '❓'}
fmt = '{logos[job.state]} {job.qualified_name()} [{job.state}]'  # , {job.task.done(**job.kwargs)}]'

# Internal list of actual Job instances run in the current session
_jobs = []

# Fully qualified names of jobs run in the current session are stored in pantarei.jobs list
# It is meant to be a public variable, which can be reset at will.
jobs = []
_tasks = []

# Recolorize output
class _colors:
    """Dummy class for bash colors"""
    OK = '\033[92m'
    WARN = '\033[93m'
    DIM = '\033[90m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\033[97m'

# https://www.w3schools.com/charsets/ref_utf_geometric.asp
_symbol_clock = '⏱'
_symbol_done = '🟩'  # en
_symbol_fail = '🟥'  # red
_symbol_run = '🟨'  # yellow ⚡
_symbol_black = '⬛'
_symbol_white = '⬜'
_symbol_done = _colors.OK + '⬛' + _colors.END
_symbol_fail = _colors.FAIL + '⬛' + _colors.END

_block = '█'
_horiz = '█'  #'―'
_thick = '―'



def orphans(verbose=True):
    """
    Return "orphaned" jobs, which are found in cache but are not
    defined in the current session
    """
    # TODO: should be done with tasks, not jobs
    jobs = []

    # TODO: handle edge case of multiple caches?
    if len(_jobs) > 0:
        cache_path = _jobs[0].task.cache.path
    else:
        # from .cache import default_cache
        # cache_path = default_cache.path
        return []

    for job in _jobs:
        # Task does not store the kwargs...? Use job for the time being
        # print(job, job.task.qualified_name())
        jobs.append(os.path.join(cache_path, job.qualified_name()))

    paths = []
    for path in glob.glob(os.path.join(cache_path, '*', '*')):
        # We check is job.yaml exists because we only
        # look for orphaned jobs, not tasks, at the moment
        if os.path.exists(os.path.join(path, 'job.yaml')):
            paths.append(path)

    missing = sorted(set(paths) - set(jobs))
    from collections import defaultdict
    func_tags = defaultdict(int)
    for entry in missing:
        func_tags[os.path.dirname(entry)] += 1
    for entry in sorted(func_tags):
        n = func_tags[entry]
        N = len(glob.glob(os.path.join(entry, '*')))
        if verbose:
            print(f'Orphaned jobs in {entry}: {n}/{N}')

    return missing


# Job reports
def _eta(jobs):
    import datetime
    total_time, done, running = 0, 0, 0
    for job in jobs:
        if job.state in ['ended', 'failed']:
            done += 1
            total_time += job.duration.total_seconds()
        if job.state == 'running':
            running += 1
            total_time += job.duration.total_seconds()
    if (running + done) > 0 and (running + done) != len(jobs):
        seconds = total_time / (running + done) * (len(jobs) - (done + running))
        return datetime.timedelta(seconds=int(seconds)), \
            datetime.timedelta(seconds=int(total_time))
    if (running + done) == len(jobs):
        return None, datetime.timedelta(seconds=int(total_time))
    return None, datetime.timedelta(seconds=0)

def _bar(n, N, size=20):
    x = int(n / N * size)
    return '|' + '█'*x + '.'*(size - x) + '|'

def _bar_frac(n, N, size=20, symbol=_horiz):
    x = int(round(n / N * size))
    x = int(n / N * size)
    if n > 0:
        x += 1
    return symbol*x

def browse(name='', qualified_names=(), tag='', path='.pantarei'):
    """Convenience function that returns a `Dataset` of tasks' metadata

    If `qualified_names` is given, then we browse
    only the tasks corresponding to that list (or tuple) of fully
    qualified names (as returned by `~pantarei.task.Task.qualified_name()`).

    :param name: name of function to browse
    :param qualified_names: list of qualified names of cached results to browse
    :param tag: tag of task
    :param path: path of pantarei cache
    """
    from .database import Dataset
    from .parsers import parse_yaml, parse_pickle
    ds = Dataset(parsers=[(parse_yaml, '*.yaml'),
                          (parse_pickle, '*.pkl')], keep_default_parsers=False)

    if len(qualified_names) > 0:
        # We provide a specific list of tasks
        assert len(name) == 0 and len(tag) == 0

        for fqn in qualified_names:
            ds.insert(f'{path}/{fqn}/arguments.pkl')
            ds.insert(f'{path}/{fqn}/job.yaml')
            try:
                ds.insert(f'{path}/{fqn}/results.pkl')
            except TypeError:
                pass
    else:
        # Browse the full dataset
        if len(name) == 0:
            name = '*'
        if len(name) > 0 and len(tag) > 0:
            name = f'{name}-{tag}'

        # Sort paths by task start
        # TODO: but certainly safer than modification, but likely slower. How much?
        def _sorted_task(paths):
            times = []
            _paths = glob.glob(paths)
            for _path in _paths:
                t = parse_yaml(os.path.join(_path, 'task.yaml'))['task_start']
                times.append(t)
            return [y[0] for y in sorted(zip(_paths, times), key=lambda x: x[1])]

        # This first insertion of the arguments defines the order of
        # the dataset entries (according to task start)
        for _path in _sorted_task(f'{path}/{name}/*/'):
            ds.insert(os.path.join(_path, 'arguments.pkl'))
        # Insertion of job metadata and results will go into the unique
        # entry defined by the dirname of the path
        # TODO: shall we include task metadata, postprocessed to just include duration?
        # TODO: add flags to include/exclde/postprocess metadata
        ds.insert(f'{path}/{name}/*/job.yaml')
        try:
            ds.insert(f'{path}/{name}/*/results.pkl')
        except TypeError:
            print(f'WARNING: could not insert results of {path}/{name}/*/results.pkl (most likely not a dict)')

    return ds

class block:

    def __enter__(self):
        global jobs
        jobs = []

    def __exit__(self, exc_type, exc_value, exc_tb):
        global jobs
        from .scheduler import Scheduler
        Scheduler().wait(jobs)

def _report(jobs, only=()):
    from collections import defaultdict

    if len(jobs) == 0:
        return []

    lines = []
    colors = _colors
    # states = defaultdict(int)
    for state in logos:
        if state == 'failed':
            start, end = colors.BOLD + colors.FAIL, colors.END
            #start, end = colors.FAIL, colors.END
        elif state == 'running':
            start, end = colors.BOLD, colors.END
        elif state == 'ended':
            start, end = '', ''
        else:
            start, end = colors.DIM, colors.END
        for job in jobs:
            if job.state == state:
                # states[job.state] += 1
                if len(only) > 0 and job.state not in only:
                    continue
                # TODO: pretty name should only include the kwargs (no defaults ones)
                try:
                    # This would not be a property
                    name = job.pretty_name()
                except TypeError:
                    # _Job has a simple attribute
                    name = job.pretty_name

                if len(name) > 100:
                    name = name[:100 - 4] + ' ...'
                #lines.append(start + f'{logos[job.state]} {str(job.duration)} {job.qualified_name()} {name}' + end)
                lines.append('   ' + start + f'{logos[job.state]} {job.qualified_name} {str(job.duration)} {name}' + end)

    return lines

def _report_summary(jobs):
    from collections import defaultdict
    
    states = defaultdict(int)
    for state in logos:
        for job in jobs:
            if job.state == state:
                states[job.state] += 1
    lines = []
    colors = _colors
    for state in logos:
        if states[state] == 0:
            continue
        # TODO: refactor
        if state == 'failed':
            start, end = colors.BOLD + colors.FAIL, colors.END
        elif state == 'running':
            start, end = colors.BOLD, colors.END
        elif state == 'ended':
            start, end = '', ''
        else:
            start, end = colors.DIM, colors.END
        #bar = _bar(states[state], len(jobs))
        line = start + \
            f'{logos[state]} {state:7} {states[state]/len(jobs)*100:3.0f}% [{states[state]}/{len(jobs)}]' + end
        lines.append(line)
    return lines
        
    # # ETA
    # import datetime
    # started_jobs = states["ended"] + states["failed"] + states["running"]
    # eta, so_far = _eta(jobs)
    # if eta is None:
    #     eta = 'N/A'
    # if started_jobs == 0:
    #     return lines

    # mean_time = datetime.timedelta(seconds=int(so_far.total_seconds()/(started_jobs)))
    # eta, so_far, mean_time = str(eta), str(so_far), str(mean_time)
    # lines.append('')
    # for key, value in [("Total CPU time", so_far),
    #                    ("Mean CPU time per job", mean_time),
    #                    ("Wall time left", eta)]:
    #     # value = ' ' + value
    #     lines.append(f'{key:.<22}{value:.>22}')

    # return lines

def _report_oneline(jobs):
    # TODO: clean up and refactor
    from collections import defaultdict
    if len(jobs) == 0:
        return ''

    colors = _colors
    # TODO: refactor
    states = defaultdict(int)
    for state in logos:
        for job in jobs:
            if job.state == state:
                states[job.state] += 1

    #status_symbol = ' '
    if states['failed'] > 0:
        status_symbol = _symbol_fail
    elif states['ended'] == len(jobs):
        status_symbol = _symbol_done
    else:
        status_symbol = _symbol_white

    # Number of blocks of each state for the bar
    bar_size = 20
    bar_x = defaultdict(int)
    for state in logos:
        x = int(states[state] / len(jobs) * bar_size)
        if states[state] > 0:
            x += 1
        bar_x[state] = x
    delta = sum(bar_x.values()) - bar_size

    for state in logos:
        if delta == 0:
            break
        if bar_x[state] > 1:
            bar_x[state] = bar_x[state] - 1
            delta -= 1

    # Summary
    start, end = '', ''
    bar = start + '|'
    for state in logos:
        if states[state] == 0:
            continue
        if state == 'failed':
            start, end = colors.BOLD + colors.FAIL, colors.END
            symbol = _block
        elif state == 'running':
            # start, end = colors.DIM, colors.END
            start, end = colors.WHITE, colors.END
            symbol = _horiz
        elif state == 'ended':
            start, end = colors.DIM, colors.END
            symbol = _horiz
        else:
            start, end = colors.WHITE, colors.END
            symbol = _horiz
        #bar_x = _bar_frac(states[state], len(jobs), size=bar_size, symbol=symbol)
        _bar_x = bar_x[state] * symbol
        bar += f'{start}{_bar_x}{end}'
    bar += '|'

    # ETA
    eta, so_far = _eta(jobs)
    # started_jobs = states["ended"] + states["failed"] + states["running"]
    # if started_jobs == 0:
    #     return lines
    # mean_time = datetime.timedelta(seconds=int(so_far.total_seconds()/(started_jobs)))
    eta, so_far, mean_time = str(eta), str(so_far), '' #str(mean_time)
    key, value = "Total CPU time", so_far
    #line += f'{key:.<22}{value:.>22}'
    total_time = value

    perc = f'{states["ended"]/len(jobs)*100:3.0f}%'
    jobs_summary = f'{perc} [{states["ended"]}/{len(jobs)}]'
    return ' '.join([status_symbol, bar, jobs_summary, total_time])

def _report_paths(only=()):
    """Return a list with the qualified names of the jobs in this session"""
    lines = []
    for job in _jobs:
        if len(only) > 0 and job.state not in only:
            continue
        lines.append(job.path)
    return lines

def report_paths(only=()):
    """
    Print a report on the jobs in the current session

    :param only: types of jobs to include. Possible values are:
      `failed`, `running`, `ended`, `queued`. By default, all jobs are
      shown
    """
    lines = _report(_jobs, only)
    if len(lines) > 0:
        print('\n'.join(lines))

def __report():
    """
    Print a report on the jobs in the current session

    :param only: types of jobs to include. Possible values are:
      `failed`, `running`, `ended`, `queued`. By default, all jobs are
      shown
    """
    #if len(_jobs) > 0 and 'pantarei_report' in os.environ:
    if len(_tasks) > 0 and 'pantarei_report' in os.environ:
        print('# pantarei paths:')
        print('\n'.join(_tasks))

# Log at the end of scripts

# def __report():
#     report(only=('running', 'failed'))


# We should not do this during unit tests
# The jobs will be there but the cache may be gone
# This will give a spurious final line
# TODO: register these hooks somewhere else, this must not be done globally!
atexit.register(__report)
# atexit.register(__report)
# atexit.register(orphans)
