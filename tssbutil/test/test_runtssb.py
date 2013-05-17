'''
Created on May 16, 2013

@author: bwilkinson
'''
import unittest
import os
from tssbutil.runtssb import run_tssb
import testutil
import pywinauto

def tssbtest_path(fname):
    return '%s/tssb/%s' % (os.path.dirname(__file__),fname)
    
class Test(unittest.TestCase):


    def setUp(self):
        if os.path.exists(tssbtest_path('AUDIT.LOG')):
            os.remove(tssbtest_path('AUDIT.LOG'))


    def tearDown(self):
        # clean up
        if os.path.exists(tssbtest_path('AUDIT.LOG')):
            os.remove(tssbtest_path('AUDIT.LOG'))
        if os.path.exists(tssbtest_path('MEM.LOG')):
            os.remove(tssbtest_path('MEM.LOG'))
        if os.path.exists(tssbtest_path('REPORT.LOG')):
            os.remove(tssbtest_path('REPORT.LOG'))
        

    def testSuccess(self):
        script = tssbtest_path('simple.txt')
        script = script.replace('/','\\')
        run_tssb(script,tssb_path='C:\\Users\\bwilkinson.Calpont\\TSSB\\tssb64.exe')
        
        ref = tssbtest_path('ref_audit.log')
        targ = tssbtest_path('AUDIT.LOG')
        self.assertTrue(testutil.file_compare(ref, targ))
                
    def testTSSBNotFound(self):
        script = tssbtest_path('simple.txt')
        script = script.replace('/','\\')
        with self.assertRaises(pywinauto.application.AppStartError):
            run_tssb(script)

    def testScriptNotFound(self):
        script = tssbtest_path('foobar')
        script = script.replace('/','\\')
        with self.assertRaisesRegexp(Exception,'TSSB could not find script file'):
            run_tssb(script,tssb_path='C:\\Users\\bwilkinson.Calpont\\TSSB\\tssb64.exe')

    def testSyntaxError(self):
        script = tssbtest_path('error.txt')
        script = script.replace('/','\\')
        with self.assertRaisesRegexp(Exception,'TSSB found a syntax error in'):
            run_tssb(script,tssb_path='C:\\Users\\bwilkinson.Calpont\\TSSB\\tssb64.exe')

    def testOtherError(self):
        script = tssbtest_path('error2.txt')
        script = script.replace('/','\\')
        with self.assertRaisesRegexp(Exception,'TSSB found errors in'):
            run_tssb(script,tssb_path='C:\\Users\\bwilkinson.Calpont\\TSSB\\tssb64.exe')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()