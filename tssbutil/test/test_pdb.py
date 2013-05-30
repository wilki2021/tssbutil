'''
Created on May 30, 2013

@author: bwilkinson
'''

import unittest
from tssbutil.pdb import DbParser
import os

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDb1(self):
        dbfile = '%s/test_db1.dat' % os.path.dirname(__file__)
        db = DbParser(dbfile)
        
        self.assertEqual(db.get_value('20130301', 'TU2', 'COMM5'), 0.17936447)
        
        with self.assertRaises(KeyError):
            db.get_value('20131201', 'TU2', 'COMM5')
            
        with self.assertRaises(ValueError):
            db.get_value('20130301', 'TU2', 'COMM99')            