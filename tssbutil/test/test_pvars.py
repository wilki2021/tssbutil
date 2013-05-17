'''
Created on May 16, 2013

@author: bwilkinson
'''
import unittest
import os
from tssbutil.pvars import VarParser

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testVars1(self):
        f = '%s/test_vars1.txt' % os.path.dirname(__file__)
        parser = VarParser(f)

        vars_ = parser.vars()
        self.assertEqual(len(vars_),74)
        self.assertEqual(vars_['PRSKEW'],'PRICE SKEWNESS 50 2')
        self.assertEqual(vars_['FTI100'],'FTI FTI 100 26 50')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testVars1']
    unittest.main()