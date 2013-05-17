'''
Created on May 16, 2013

@author: bwilkinson
'''
import unittest
from tssbutil.sedlite import sed_lite
import os
import testutil

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBasic(self):
        f1 = '%s/test_sedin.txt' % os.path.dirname(__file__)
        f2 = '%s/test_sedout.txt' % os.path.dirname(__file__)
        f3 = '%s/ref_sedout.txt' % os.path.dirname(__file__)
        
        sed_lite(f1, f2, {'<YEAR_START>' : '1990', 
                          '<YEAR_MAX>' : '2000',
                          '<VAR_LIST>' : 'testlist',
                          '<DB_NAME>' : 'foobar'})
        
        self.assertTrue(testutil.file_compare(f2,f3))
        os.remove(f2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()