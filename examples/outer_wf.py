# Copyright 2013, Bob Wilkinson
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from tssbutil.paudit import AuditParser
from tssbutil.runtssb import run_tssb
from tssbutil.sedlite import sed_lite
import getopt
import os
import shutil
import sys

def usage():
    print '''
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
'''
    
def apply_script_template(template, output, varmap):
    assert(os.path.exists(template))
    if os.path.exists(output):
        os.remove(output)
    sed_lite(template, output, varmap)
        
def run_tssb_wrapper(script, log):
    tssb = 'C:\\TSSB\\tssb64.exe'
    filepath = os.path.join(os.getcwd(), script)
    run_tssb(filepath,tssb_path=tssb)

    if not os.path.exists('AUDIT.LOG'):
        raise Exception("TSSB did not appear to write an AUDIT.log file!!")
    
    if os.path.exists(log):
        os.remove(log)
    os.rename('AUDIT.LOG',log)
    
stage1_scripts = ['stage1.txt']
stage2_scripts = ['stage2.txt']

def get_vars_from_modeldefn(defn):
    ret = ''
    for var in defn.get_factors():
        if var[0] != 'CONSTANT':
            ret = ret + ' ' + var[0]
    return ret
    
def run_iteration(year, lag):
    print 'Running iteration for year %d' % year
   
    workdir = '%s' % year
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.mkdir(workdir)
        
    os.chdir(workdir)
    
    # first instantiate our each script files
    varmap = {
        '<YEAR_START>' : '%s' % (year - lag),
        '<YEAR_END>' : '%s' % year,
        '<VAL_YEAR>' : '%s' % (year + 1),
        '<TEST_YEAR>' : '%s' % (year + 2)
        }
    for s in stage1_scripts:
        apply_script_template(os.path.join("..",s), s, varmap)

    # first run the stage 1 script to find models that perform well
    # on the test set
    log = 'stage1.log'
    run_tssb_wrapper(stage1_scripts[0],log)
    sub = AuditParser(log)
    
    # there should be exactly one fold based on stage1.txt
    assert( len(sub.tssbrun().folds()) == 1 )
    fold = sub.tssbrun().folds()[0]
    
    # now we want to rank models by performance on the test set and
    # pick the best two    
    ranked = sorted(fold.models().itervalues(), key=lambda x: x.oosample_stats().long_only_imp, reverse=True)

    # add the variables from the two best models to the map and 
    # ansert into our stage 2 script file
    varmap['<GROUP1>'] = get_vars_from_modeldefn(ranked[0].defn())
    varmap['<GROUP2>'] = get_vars_from_modeldefn(ranked[1].defn())
    apply_script_template(os.path.join("..",'stage2.txt'), 'stage2.txt', varmap)

    # Now stage 2 is our true walk-forward test
    log = 'stage2.log'
    run_tssb_wrapper(stage2_scripts[0],log)
    sub = AuditParser(log)
    
    os.chdir("..")
    return sub
        
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if True:
            # we don't support any options so anything here is a problem.
            usage()
            sys.exit(1)
                         
    if len(args) != 2:
        print 'Not enough arguments to outer_wf!'
        usage()
        sys.exit(1)
        
    yearstart = int(args[0])
    yearend = int(args[1])

    for s in stage1_scripts:
        if not os.path.exists(s):
            print 'Error: must have the script template %s in current directory' % s
    for s in stage2_scripts:
        if not os.path.exists(s):
            print 'Error: must have the script template %s in current directory' % s

    wf = open("perf.csv","w")      
    headers = False
    for y in range(yearstart, yearend+1):
        # we get back the results from 1 walk-forward year
        res = run_iteration(y, 13)

        if not headers:
            headers = True
            line = 'year'
            for (model,wfmstats) in sorted(res.tssbrun().walkforward_summ().iteritems()):
                line = line + ",%s" % model
            wf.write('%s\n' % line)

        line = '%s' % y 
        for (model,wfmstats) in sorted(res.tssbrun().walkforward_summ().iteritems()):
            line = line + ",%0.4f" % wfmstats.long_only_imp
        wf.write('%s\n' % line)
    wf.close()            
    print 'Walk-forward results written to perf.csv'