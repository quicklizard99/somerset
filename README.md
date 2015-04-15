# Somerset

Simple scientific pipelines.

* stages can be written using any tool or language
* output files are made read-only when stages complete
* stages cannot be accidentally run again
* `stdout` and `stderr` are both printed to the console and written to a log file
* log files will contain
    * local datetimes that the staged started and completed
    * version number of the binary used to run the stage
    * host name
    * OS name

## Installation

Install the current release of Python 3, run `pip install --upgrade pip` and
then do one of the following

* To install a release

```
pip install <file you downloaded>
```

or

```
pip install https://github.com/NaturalHistoryMuseum/somerset/archive/v0.1.1.zip
```

* To install the current source


```
pip install git+https://github.com/quicklizard99/somerset@master
```

* To clone this repo

```
git clone https://github.com/NaturalHistoryMuseum/somerset.git
cd somerset
./setup.py install
```

## Define stages

Create `stages.py` that tells somerset about each of the stages in your pipeline.
For example, stage 1 might be a Python 2 script, and stage 2 an R script:

    python = '/home/lawh/Envs/dig279/bin/python'
    R = '/home/lawh/local/R-3.1.3/bin/Rscript'

    STAGES = [ ('1', python, '-u', '1_analyse.py'),
               ('2', R,            '2_results.R'),
             ]

If the same pipeline will be run on different machines, you might want to
define the locations of the binaries:

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


## Run stages

The following all have effect of running both stages in the pipeline

    somerset.py 1 2
    somerset.py all
    somerset.py 1 && somerset.py 2

For each of the above forms, if stage 1 fails, stage 2 wil not be run.
`somerset` creates an output directory for each stage, named by removing the
suffix of the stage filename. For the `stages.py` given above, `1_analyse.py`
should write all its output to the directory `1_analyse`.

Once complete, your directory will look like:

    0_data
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

Remove a stage's output directory to run it again. Want to start from scratch?
The following both have the same effect

    rm -rf 1_analyse 2_results
    somerset.py --remove-all-output

## What stages do I have?

    somerset.py --list

produces

    1 ['/Users/lawh/Envs/barcode_report/bin/python', '-u', '1_analyse.py']
    2 ['/usr/bin/Rscript', '2_results.R']
    all
