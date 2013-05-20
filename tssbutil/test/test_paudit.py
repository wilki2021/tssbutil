'''
Created on May 16, 2013

@author: bwilkinson
'''
import unittest
from tssbutil.paudit import AuditParser
import os
import math

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testAudit1(self):
        tlog = '%s/test_audit1.log' % os.path.dirname(__file__)
        aud = AuditParser(tlog)

        wfmstats = aud.tssbrun().walkforward_summ()
        self.assertEqual(len(wfmstats), 5)
        self.assertTrue(wfmstats.has_key('FILTLONG5'))

        # this was a somewhat special case where 0 trades were
        # below the low threshold.  This changes the output format
        # a bit
        comm6 = wfmstats['FILTLONG5']

        self.assertEqual(comm6.target_grand_mean, -0.0141)
        self.assertEqual(comm6.total_cases, 16)
        self.assertEqual(comm6.num_above_high, 9)
        self.assertEqual(comm6.num_below_low, 0)
        self.assertEqual(comm6.mean_above_high, -0.16248)
        self.assertEqual(comm6.mean_below_low, 0.0)
        self.assertEqual(comm6.roc_area, 0.24178)
        self.assertEqual(comm6.long_profit_fac, 0.531)
        self.assertEqual(comm6.long_only_imp, 0.560)
        self.assertTrue(math.isnan(comm6.short_profit_fac))
        self.assertTrue(math.isnan(comm6.short_only_imp))
        self.assertEqual(comm6.long_total_ret, -1.46)
        self.assertEqual(comm6.long_maxdd, 2.59)
        self.assertEqual(comm6.short_total_ret, 0.0)
        self.assertEqual(comm6.short_maxdd, 0.0)

        # this is a standard case
        filtlog4 = wfmstats['FILTLONG4']

        self.assertEqual(filtlog4.target_grand_mean, -0.0141)
        self.assertEqual(filtlog4.total_cases, 16)
        self.assertEqual(filtlog4.num_above_high, 3)
        self.assertEqual(filtlog4.num_below_low, 5)
        self.assertEqual(filtlog4.mean_above_high, -0.20522)
        self.assertEqual(filtlog4.mean_below_low, 0.06147)
        self.assertEqual(filtlog4.roc_area, 0.43103)
        self.assertEqual(filtlog4.long_profit_fac, 0.458)
        self.assertEqual(filtlog4.long_only_imp, 0.484)
        self.assertEqual(filtlog4.short_profit_fac, 0.795)
        self.assertEqual(filtlog4.short_only_imp, 0.753)
        self.assertEqual(filtlog4.long_total_ret, -0.62)
        self.assertEqual(filtlog4.long_maxdd, 1.14)
        self.assertEqual(filtlog4.short_total_ret, -0.31)
        self.assertEqual(filtlog4.short_maxdd, 1.10)
        
        # we can also test the selection count parser in this file
        selstats = aud.tssbrun().selection_stats()
        self.assertEqual(len(selstats.get_model_vars('FILTLONG1')), 16)
        self.assertEqual(len(selstats.get_model_vars('FILTLONG2')), 18)
        self.assertEqual(len(selstats.get_model_vars('FILTLONG3')), 20)
        self.assertEqual(len(selstats.get_model_vars('FILTLONG4')), 16)

        sel5 = selstats.get_model_vars('FILTLONG3')
        self.assertEqual(len(sel5), 20)
        self.assertEqual(sel5[0][0], 'IDMORLET100')
        self.assertEqual(sel5[0][1], 26.67)
        self.assertEqual(sel5[-1][0], 'LIN_ATR_50')
        self.assertEqual(sel5[-1][1], 3.33)
        
        summ = selstats.list_all_gt(5.0)
        self.assertEqual(len(summ), 7)
        self.assertEqual(summ[0][0],'IDMORLET100')
        self.assertEqual(summ[0][1],18.668)
        self.assertEqual(summ[1][0],'INT_50')
        self.assertEqual(summ[1][1],9.998)
        pass

    def testAudit2(self):
        # this is a log from FIND GROUPS
        tlog = '%s/test_audit2.log' % os.path.dirname(__file__)
        aud = AuditParser(tlog)

        self.assertEqual(len(aud.tssbrun().folds()),1)
        fgps = aud.tssbrun().folds()[0].models()
        self.assertEqual(len(fgps), 5)
        defn = fgps['1'].defn()
        self.assertEqual(len(defn.get_factors()), 2)
        self.assertEqual(defn.get_factors()[0][0],'DINT_50')
        self.assertEqual(defn.get_factors()[0][1],0.005927)
        self.assertEqual(defn.get_factors()[1][0],'CONSTANT')
        self.assertEqual(defn.get_factors()[1][1],0.171395)

        defn = fgps['5'].defn()
        self.assertEqual(len(defn.get_factors()), 2)
        self.assertEqual(defn.get_factors()[0][0],'RDMORLET100')
        self.assertEqual(defn.get_factors()[0][1],0.009905)
        self.assertEqual(defn.get_factors()[1][0],'CONSTANT')
        self.assertEqual(defn.get_factors()[1][1],0.225174)

    def testAudit3(self):
        # this is a log with quadratic models and a combination of committees and models
        tlog = '%s/test_audit3.log' % os.path.dirname(__file__)
        aud = AuditParser(tlog)

        wfmstats = aud.tssbrun().walkforward_summ()
        self.assertEqual(len(wfmstats), 11)
        self.assertTrue(wfmstats.has_key('COMM6'))

        # this was a somewhat special case where 0 trades were
        # below the low threshold.  This changes the output format
        # a bit
        comm6 = wfmstats['COMM6']

        self.assertEqual(comm6.target_grand_mean, 0.19829)
        self.assertEqual(comm6.total_cases, 828)
        self.assertEqual(comm6.num_above_high, 263)
        self.assertEqual(comm6.num_below_low, 282)
        self.assertEqual(comm6.mean_above_high, 0.31200)
        self.assertEqual(comm6.mean_below_low, 0.13514)
        self.assertEqual(comm6.roc_area, 0.55449)
        self.assertEqual(comm6.long_only_imp, 1.396)
        self.assertEqual(comm6.short_only_imp, 1.221)
        self.assertEqual(comm6.long_total_ret, 82.06)
        self.assertEqual(comm6.long_maxdd, 2.86)
        self.assertEqual(comm6.short_total_ret, -38.11)
        self.assertEqual(comm6.short_maxdd, 50.22)

    def testAudit1_b(self):
        # reuse audit1.log again, but now look for walk-forward folds

        tlog = '%s/test_audit1.log' % os.path.dirname(__file__)
        aud = AuditParser(tlog)

        tssbrun = aud.tssbrun()
        self.assertEqual(len(tssbrun.folds()), 1)
        self.assertEqual(tssbrun.folds()[0].name(), '2013')
        f4 = tssbrun.folds()[0].models()['FILTLONG4']
        defn = f4.defn()        
        self.assertEqual(len(defn.get_factors()),3)
        facs = sorted(defn.get_factors())
        self.assertEqual(facs[0],('CONSTANT',0.138695,1))
        self.assertEqual(facs[1],('QUAD_ATR_100',-0.135129,2))
        self.assertEqual(facs[2],('REAC_50',0.137624,1))
        
        # now spot check in- and out-of-sample stats
        insamp = f4.insample_stats()
        self.assertEqual(insamp.num_above_high,223)
        self.assertEqual(insamp.long_only_imp,1.501)

        outsamp = f4.oosample_stats()
        self.assertEqual(outsamp.num_below_low,5)
        self.assertEqual(outsamp.mean_below_low,0.06147)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()