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
'''
tssbutil.runtssb

Contains:
   run_tssb()
'''
from pywinauto import application
import pywinauto
import time
import traceback
import sys
import os

def get_process_list():
    ret = set()
    hand = os.popen("wmic process get description")
    for line in hand.readlines():
        line = line.strip()
        if len(line):
            ret.add(line)
    hand.close()
    return ret
     
def run_tssb(script, tssb_path='tssb64.exe'):
    '''
    run_tssb performs a run of TSSB for the specified script file.  If the
    function returns without exception then it can be assumed that there is 
    an AUDIT.LOG file with run results in the same directory where the script
    file is 
        
    :param string script: script file to run.  Should always be an absolute 
                          Windows-format path.
    :param string tssb_path: [Optional] path to the tssb executable.  If not 
                             specified it assumes that tssb64.exe is either in 
                             the current directory or the path of whatever 
                             shell you happen to be executing from.
                             
    :returns: No return.
    :throws:  Various exceptions possible.  Primary exception conditions are:
                - Could not locate tssb64.exe executable
                - TSSB could not locate the script file
    '''
    app = application.Application.start(tssb_path)

    # step 1 - we know that there will always be a Liability Disclaimer window
    while True:
        try:
            app.window_(title="Disclaimer of Liability").Wait('ready')
            break
        except:
            # we don't really care what the exception is - we just know
            # that it has to show up at some point
            time.sleep(0.5)

    # step 2 - now make it go away
    while True:
        try:
            app.window_(title="Disclaimer of Liability").IAgree.Click()
            break
        except:
            # we don't really care what the exception is - we just know
            # that it has to show up at some point
            time.sleep(0.5)

    # step 2.5 - now we need to get the Read Script dialog open
    while len(app.windows_(title=u'Script file to read')) == 0:
        try:
            app.window_(title_re="TSSB.*").MenuSelect('File->Read Script')
        except:
            time.sleep(0.5)
            
    # step 3 - make sure we get the script into the file open box
    text = ''
    while text != script:
        try:
            read_dlg = app.window_(title="Script file to read")
            read_dlg.Wait('ready')
            read_dlg.Edit.SetEditText(script)
            text = read_dlg.Edit.TextBlock()
        except:
            tb = traceback.format_exc()
            print tb
            time.sleep(0.5)

    # step 4 - get past the file open box.  There are two possibilities-
    # either TSSB starts processing or it couldn't open the script in 
    # which case we need to detect that and bail out
    while len(app.windows_(title=u'Script file to read')) > 0:
        if len(app.windows_(title=u'Script file to read')) == 2:
            # this is what happens when tssb cannot find the specified script file
            # first close both dialogs
            while len(app.windows_(title=u'Script file to read')) > 0:
                app.windows_(title=u'Script file to read')[0].Close()
            #  now close the main window
            app.window_(title_re="TSSB.*").MenuSelect('File->Exit')
            #  finally, throw an exception so the user knows what happened 
            raise Exception('TSSB could not find script file: %s' % script)                        
        try:
            app.window_(title="Script file to read").Open.Click()
        except:
            time.sleep(0.5)
    
    # arbitrary sleep to make sure the script starts        
    time.sleep(1.0)
    
    # step 5 - monitor for completion.  If the script runs to completion
    # we'll eventually get a successful MenuSelect call for File->Exit.
    # the other possibility, however is that the script had errors.  We
    # need to detect that and bail out if it occurs
    while True:
        # this checks for the syntax error case
        if len(app.windows_(title_re='Syntax.*')):
            # oops - this means the script had some type of error.  We want
            # to close the dialog exit and throw an exception
            app.window_(title_re='Syntax.*').Close()
            #  now close the main window
            app.window_(title=script).MenuSelect('File->Exit')
            #  finally, throw an exception so the user knows what happened 
            raise Exception('TSSB found a syntax error in: %s' % script)                        
        # this checks for another error case
        if len(app.windows_(title_re='Error.*')):
            # oops - this means the script had some type of error.  We want
            # to close the dialog exit and throw an exception
            app.window_(title_re='Error.*').Close()
            #  now close the main window
            app.window_(title=script).MenuSelect('File->Exit')
            #  finally, throw an exception so the user knows what happened 
            raise Exception('TSSB found errors in: %s' % script)                        
        
        # this is the normal busy-loop check
        try:
            app.window_(title=script).MenuSelect('File->Exit')
            time.sleep(1.0)
            if 'tssb64.exe' in get_process_list():
                # this should not happen - it means the MenuSelect call went 
                # through without exception but the process is still running
                pass
            else:
                break
        except pywinauto.controls.menuwrapper.MenuItemNotEnabled:
            time.sleep(1.0)
        except pywinauto.findwindows.WindowNotFoundError:
            # this can happen in a few different cases.  Have seen this exception
            # when TSSB is still actually running so cannot blindly assume we are
            # done.  Have also see us get here because calls to File->Exit actually
            # did work but we still have a tssb64.exe process running.
            if not 'tssb64.exe' in get_process_list():
                # if window not found and process not running then we should be
                # ok to exit.
                break
            time.sleep(1.0)
        except:
            # this is an exception we don't expect.  Print it for debugging, 
            # but sleep and try again 
            tb = traceback.format_exc()
            print tb
            time.sleep(1.0) 
    
if __name__ == '__main__':
    # print get_process_list()
    # run_tssb('foobar')
    scrfile = sys.argv[1]
    run_tssb(scrfile,tssb_path="C:\\Users\\bwilkinson.Calpont\\TSSB\\tssb64.exe")