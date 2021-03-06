# Somerset

Simple scientific pipelines.

I wrote Somerset because I wanted to

* break my analyses into discrete stages
* be able to run each stage independently that can be run independently
* have the pipeline execution halt if a stage fails
* prevent myself from accidentally overwritting or deleting outputs
* record all output to a single logfile
* record the date, time and name of the computer on which the stage was run
* record the version of R, Python or whatever else I used for that stage

Somerset is a small Python script
* stages can be written using any tool or language - Python, R, Java, bash
* each stage gets it's own script file
* stages cannot be accidentally run again
* each stage's output files are written to a single directory and are made
  read-only when stages complete
* `stdout` and `stderr` are printed to the console and written to a log file
* a logfile is written per stage, containing

    * the version number of the tool used to execute the stage are recorded a log file
    * the local date and time on which the staged started and completed
    * version number of the binary used to run the stage
    * host name
    * OS name

## Installation

Install the current release of Python 3, run `pip install --upgrade pip` and
then do one of the following

* To install a release

```
pip install https://github.com/quicklizard99/somerset/archive/v0.1.7.zip
```

or if you downloaded a release file

    pip install <file you downloaded>

* To install the current source


    pip install git+https://github.com/quicklizard99/somerset@master

## Define stages

Create `stages.py` that tells somerset about each of the stages in your pipeline.
For example, stage 1 might be a Python script, and stage 2 an R script:

```python
python = '/home/lawh/Envs/dig279/bin/python'
R = '/home/lawh/local/R-3.1.3/bin/Rscript'

STAGES = [ ('1', python, '-u', '1_analyse.py'),
           ('2', R,            '2_results.R'),
         ]
```

The `'-u'` flag makes Python write unbuffered output, so you will see output
as soon as it is printed rather than when Python flushes its output buffers.

You might want to use different versions of a tool for different stages, for
example Python 3 for most bits and Python 2 that ships with ArcGIS for a GIS
analysis

```python
STAGES = [ ('1', 'C:/Python35/python.exe', '-u', '1_preprocess.py'),
           ('2', 'C:/Python27/ArcGIS10.1/python.exe,', '-u', '2_grid_cells.py'),
         ]
```

If the same pipeline will be run on different machines, you might want to
define the locations of the binaries:

```python
import socket

if 'LSCI-H922H32' == socket.gethostname():
    # My Linux desktop
    python = '/home/lawh/Envs/dig279/bin/python'
    R = '/home/lawh/local/R-3.1.3/bin/Rscript'
else:
    # Assume my MacBook Air
    python = '/Users/lawh/Envs/barcode_report/bin/python'
    R = '/usr/bin/Rscript'

STAGES = [ ('1', python, '-u', '1_analyse.py'),
           ('2', R,            '2_results.R'),
         ]
```

## Run stages

The following all have effect of running both stages in the above pipeline

    somerset.py 1 2
    somerset.py 1-2
    somerset.py all
    somerset.py 1 && somerset.py 2

For each of the above forms, if stage 1 fails, stage 2 will not be run.
`somerset` creates an output directory for each stage, named by removing the
suffix of the stage filename. For the `stages.py` given above, `1_analyse.py`
should write all its output to the directory `1_analyse`.

Once complete, your directory will look like:

    0_data/data files that are the inputs to the pipeline
    1_analyse/log.txt
    1_analyse/whatever files stage 1 created
    1_analyse.py
    2_results/log.txt
    2_results/whatever files stage 2 created
    2_results.py
    stages.py

The contents of 1_analyse and 2_results will be read-only. Any attempt to re-run
a stage results in an error message:

    Traceback (most recent call last):
      File "/Users/lawh/Envs/work/bin/somerset.py", line 5, in <module>
        pkg_resources.run_script('somerset==0.1.0', 'somerset.py')
      File "/Users/lawh/Envs/work/lib/python3.4/site-packages/pkg_resources.py", line 488, in run_script
        self.require(requires)[0].run_script(script_name, ns)
      File "/Users/lawh/Envs/work/lib/python3.4/site-packages/pkg_resources.py", line 1361, in run_script
        exec(script_code, namespace, namespace)
      File "/Users/lawh/Envs/work/lib/python3.4/site-packages/somerset-0.1.0-py3.4.egg/EGG-INFO/scripts/somerset.py", line 176, in <module>
      File "/Users/lawh/Envs/work/lib/python3.4/site-packages/somerset-0.1.0-py3.4.egg/EGG-INFO/scripts/somerset.py", line 170, in main
      File "/Users/lawh/Envs/work/lib/python3.4/site-packages/somerset-0.1.0-py3.4.egg/EGG-INFO/scripts/somerset.py", line 99, in run
      File "/Users/lawh/Envs/work/lib/python3.4/site-packages/somerset-0.1.0-py3.4.egg/EGG-INFO/scripts/somerset.py", line 67, in _prime
    __main__.StageError: Output directory [1_analyse] already exists. Has this stage already been run?

## Clearing output

Remove a stage's output directory to run it again. Want to start from scratch?
Each of the following lines removes all of the output directories:

    somerset.py --remove-all-output    # Prompts for confirmation
    somerset.py -r                     # Prompts for confirmation
    somerset.py -R                     # Does not prompt

The last of these is equivalent to running

    rm -rf 1_analyse 2_results
    rmdir /Q /S 1_analyse 2_results    # Same as the above when on Windows

## What stages do I have?

    somerset.py --list

produces

    1 ['/Users/lawh/Envs/barcode_report/bin/python', '-u', '1_analyse.py']
    2 ['/usr/bin/Rscript', '2_results.R']
    all
