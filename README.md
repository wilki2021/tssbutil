tssbutil
========

This is an automation framework for Trading System Synthesis and Boosting 
(TSSB).  TSSB is nice package available here from 
|Hood River Research](http://www.tssbsoftware.com/) for the 
development of predictive model-based trading systems, but right now it is
GUI only and the output is in verbose log files.  The tssbutil framework uses
[pywinauto](http://code.google.com/p/pywinauto/) to enable a user to run a
TSSB script via a Python function invocation.  It also provides a parser that
converts TSSB output to an intuitive hierarchical data model.

## Installation

tssbutil depends on Python and the pywinauto package.  As TSSB is a windows-
only package, it is assumed that the installation and usage will occur on
a Windows platform (although parsers are cross-platform and should work in 
any environment).

tssbutil is known to work with 32-bit Python 2.7 - it likely also works with 
Python 3.X but that has not been tested.  Standard pywinauto is 32-bit specific
at this point - there are several forks that purport to make it work with 
64-bit Python but I could not make any of those work and 32-bit Python +
pywinauto worked fine on my 64-bit Windows 7 installation and 64-bit TSSB
executable. 

The Python download page is 
[here](http://www.python.org/getit/).  I recommend the 2.7.x non-64-bit 
Windows installer.  Install to a directory of your choice and add the Python
directory to your PATH for convenience.

Then, download the pywinauto package from 
[here](http://code.google.com/p/pywinauto/).  Installation instructions are
[here](http://pywinauto.googlecode.com/hg/pywinauto/docs/index.html#installation). 

Next, you need to clone this repository.  If you are a cygwin user like me, you
can install and use git from the cygwin shell:
  
    git clone git@github.com:wilki2021/tssbutil.git
  
Alternatively, there is a Windows version of git available 
[here](http://code.google.com/p/msysgit/downloads/list?q=full+installer+official+git).

Note that when choosing a directory to clone to, it is better to choose a path
without a '.' in it if you want to be able to use the example as-is (ex. 
C:\users\john.doe\workspace would not work).  This is due to a TSSB limitation 
and its `READ MARKET HISTORIES` command.

Once you have successfully cloned the tssbutil repository, run the following.

    python.exe setup.py install
  
## Using the example

There is an example that uses the main components of tssbutil to implement an 
"outer" walk-forward loop.  The example is entirely self-contained within the
tssbutil, so running is as simple as:

    python.exe examples/outer_wf.py
  
With no arguments, this will display the usage screen:

    C:\tssbutil\examples>python outer_wf.py
    Not enough arguments to outer_wf!
  
    usage: outer_wf.py <year-start> <year-end>
  
    Performs an "outer" walk-forward analysis loop across a series of
    years per the command-line arguments.  Each "inner" walk-forward 
    is used to select models that perform well on an out-of-sample data
    set which thin feeds the "outer" walk-forward loop to get unbaised
    estimation of future performance

    Parameters:
        <year-start>  - integer, year to start the outer walk forward.
                        NOTE - for any given walk-forward year, that
                        year is included in the training set, year+1
                        is the validation year used for model selection,
                        and year+2 is the test year for unbiased walk-
                        forward performance.
        <year-end>    - integer, year to end the outer walk forward.  See
                        notes above - in general this will always need to
                        be two less than the current year.
    Options:  None

Before we run the example, here is more detail on what will actually
happen.  The model is predicting next day return for IBM.  `stage1.txt`
is the "inner" walk-forward loop - it creates three 2-input linear
regression models using stepwise selection (in an exclusion group to prevent 
redundant input usage) and then walks forward by 10 years for a single year 
(the *validation* year). 

Then the output of 'stage1.txt' is examined to determine which models
performed best in the out-of-sample period (i.e. the *validation* year).
The two best 2-input models are input into `stage2.txt`, the "outer"
walk-forward loop, where they are run independently as will as inputs
into two different COMMITTEEs.  Then 'stage2.txt' trains an one 11 year 
period (the original training set plus the validation year) and tests 
one walk-forward period (the *test* year).  The performance in the *test*
year should be an unbiased estimate of future performance of this model.  

This process is repeated once per year between <year-start> and <year-end>
specified on the command-line.  The example outputs a .csv file `perf.csv`
with long profit factor improvement ratios for the out-of-sample periods
of each model and committee from `stage2.txt`.  Note that by convention,
the years specified on the command-line and reported in `perf.csv` are the
last year in the training set.  Thus for year 2002, the *validation* year
is 2003 and the *test* year is 2004 - this means the performance reported 
in `perf.csv` for 2002 is the out-of-sample results for 2004.

Here's output from an example run:

    C:\tssbutil\examples>python.exe outer_wf.py 2002 2003
    Running iteration for year 2002
    Running iteration for year 2003
    Walk-forward results written to perf.csv

And the contents of perf.csv:

    year,BEST1,BEST2,COMM1,COMM2
    2002,1.2210,1.4100,1.4100,2.1950
    2003,4.3100,1.1930,1.1930,1.4740

Note that there are likely many more measurements than just the long
profit factor improvement ration that are desirable from the outer walk-forward 
loop.  These are easily obtainable from data model produced by the parser 
for the `stage2.txt` run.  This is left as an exercise for others based on 
their particular use case.

## Troubleshooting & Misc.

While creating tssbutil, the behavior of pywinauto was seen to be be highly
non-deterministic, especially in computationally intensive TSSB runs and also very
short TSSB runs.  I believe the current run_tssb() to be generally usable, 
but doubtless other issues will arise.  The code depends on certain arbitrary
delays and various different checks that should otherwise be redundant.

Finally, note there is guaranteed to be much AUDIT.LOG output that the AuditParser
does not support.  It currently works for standard training/walk-forward with 
models and committees, as well as a `FIND GROUPS` run.  TSSB has many, many other
options - future parse support for these will be added as needed. 