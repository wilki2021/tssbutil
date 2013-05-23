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

class ZombieException(Exception):
    pass

class TSSBException(Exception):
    pass

def kill_tssb(retry_cnt=3):
    print 'Attempting to kill any running tssb64.exe processes...'
    tries = 0
    while tries < retry_cnt:
        tries = tries + 1
        cmd = 'wmic process where name="tssb64.exe" Call Terminate'
        os.system(cmd)
        if not 'tssb64.exe' in get_process_list():
            print 'Successfully killed tssb64.exe.' 
            return
        else:
            print 'Kill tssb64.exe failed, trying %d more times...' % (retry_cnt - tries)
            # oops, something went wrong - will retry next time through
    raise Exception('ERROR - unable to kill tssb64.exe')
    
def get_process_list():
    ret = set()
    hand = os.popen("wmic process get description")
    for line in hand.readlines():
        line = line.strip()
        if len(line):
            ret.add(line)
    hand.close()
    return ret
     
def check_for_last_cmd(script, log):
    # first we have to figure out the last command in the script file
    f = open(script)
    last_cmd = ''
    nested = False
    for l in f.readlines():
        l = l.strip()
        if not nested and l.find(';') != -1:
            last_cmd = l[:l.find(';')]
        elif l.find('[') != -1 and l.find(']') == -1:
            last_cmd = l[:l.find('[')]
            nested = True
        elif nested and l.find(';') != -1:
            nested = False
    f.close()
    
    f = open(log)        
    for l in f.readlines():
        l = l.strip()
        if l.find('COMMAND ---> %s' % last_cmd) == 0:
            f.close()            
            return True
    f.close()
    return False
    
def run_tssb(script, tssb_path='tssb64.exe', retry_cnt=3):
    # first make sure there are no tssb64.exe processes already running.  We
    # need to be the only one running those processes for run_tssb to work
    while 'tssb64.exe' in get_process_list():
        print 'Warning...tssb64.exe process already running, attempting to kill'
        kill_tssb()
        
    # arbitrary number of retries
    tries = 0
    while tries < retry_cnt:
        try:
            tries = tries + 1
            run_tssb_try(script, tssb_path)
            return        
        except ZombieException:
            print 'tssb64.exe failed with zombie process, trying %d more times...' % (retry_cnt - tries)
            kill_tssb()
            pass
    raise Exception('ERROR - unable to successfully complete tssb64.exe')

def run_tssb_try(script, tssb_path, zombie_limit=10):
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
                - Syntax and/or Script error
    '''
    runpath = os.path.split(script)[0]
    
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
            raise TSSBException('TSSB could not find script file: %s' % script)                        
        try:
            app.window_(title="Script file to read").Open.Click()
        except:
            time.sleep(0.5)
    
    # arbitrary sleep to make sure the script starts        
    time.sleep(0.5)
    
    # step 5 - monitor for completion.  Have rewritten this an unbelievable
    # number of times as there is no clean way to know when TSSB64 is really
    # done versus any other number of possible outcomes.  Currently settled
    # on a primary condition that the final command in the script file has
    # made it to the AUDIT.LOG call and then a subsequent call to the 
    # File->Exit menu option
    zombie_check = 0
    while True:
        # this is the normal busy-loop check
        
        # first see if the tssb64.exe process has exited
        if not 'tssb64.exe' in get_process_list():
            # process is gone - let's see if the log looks good
            if not check_for_last_cmd(script, os.path.join(runpath,'AUDIT.LOG')):
                raise TSSBException('TSSB exited, but AUDIT.LOG looks incomplete')
            break

        # now our zombie state check
        if zombie_check > zombie_limit:            
            raise ZombieException()
                    
        try:
            # this checks for the syntax error case
            if len(app.windows_(title_re='Syntax.*')):
                # oops - this means the script had some type of error.  We want
                # to close the dialog exit and throw an exception
                app.window_(title_re='Syntax.*').Close()
                #  now close the main window
                app.window_(title=script).MenuSelect('File->Exit')
                #  finally, throw an exception so the user knows what happened 
                raise TSSBException('TSSB found a syntax error in: %s' % script)                        

            # this checks for another error case
            if len(app.windows_(title_re='Error.*')):
                # oops - this means the script had some type of error.  We want
                # to close the dialog exit and throw an exception
                app.window_(title_re='Error.*').Close()
                #  now close the main window
                app.window_(title=script).MenuSelect('File->Exit')
                #  finally, throw an exception so the user knows what happened 
                raise TSSBException('TSSB found errors in: %s' % script)                        
        
            w1 = app.window_(title=script)

            if check_for_last_cmd(script, os.path.join(runpath,'AUDIT.LOG')):
                zombie_check = 0
                w1.MenuSelect('File->Exit')

            time.sleep(1.0)
                                
        except pywinauto.controls.menuwrapper.MenuItemNotEnabled:
            # this is theoretically possible if Menu state changes between
            # the isEnabled() call and the MenuSelect call
            zombie_check = 0
            time.sleep(1.0)
        except pywinauto.findwindows.WindowNotFoundError:
            # this can happen in a few different cases.  Have seen this exception
            # when TSSB is still actually running so cannot blindly assume we are
            # done.  Have also see us get here because calls to File->Exit actually
            # did work but we still have a tssb64.exe process running.
            zombie_check = zombie_check + 1
            print 'zombie_check increment to %d for window not found' % zombie_check
            time.sleep(1.0)
        except TSSBException:
            # we threw this so simply re-raise
            raise
        except:
            # pywin auto occasionally throws weird exceptions - treat this as "normal"
            # and continue
            # ...if need to see exception for debugging
            # tb = traceback.format_exc()
            # print tb
            time.sleep(1.0) 
    
if __name__ == '__main__':
    # print get_process_list()
    # run_tssb('foobar')
    scrfile = sys.argv[1]
    run_tssb(scrfile,tssb_path="C:\\Users\\bwilkinson.Calpont\\TSSB\\tssb64.exe")
