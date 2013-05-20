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
tssbutil.tssbrun

Contains:
   class TSSBRun
   class TSSBFold
   class SelectionStats
   class ModelStats
   class PooledModelStats
   class ModelDefn
   class ModelIteration
'''

class TSSBRun(object):
    '''
    This is the top-level container for model of a TSSB Run.  The overall
    structure is as follows:
    
      TSSBRun
        Folds[]
            TSSBFold1-\   |ModelIteration1-\   |ModelDefn
            .          \--|  .              \--|ModelStats (in-sample)
            .             |  .                 |ModelStats (out-of-sample)
            .             |ModelIterationN
            TSSBFoldN
        
        PooledModelStats{}
            PooledModel1
            .
            .
            .
            PooledModel2
        
        SelectionStats
            ModelVars1
            .
            .
            .
            ModelVarsN        
    '''
    def __init__(self):
        '''Constructor.'''
        self._folds = []
        self._wfsumm = {}
        self._selstats = None
        
    def folds(self):
        '''Returns a list of TSSBFold instances.'''
        return self._folds
    
    def walkforward_summ(self):
        '''
        Returns a dictionary of PooledModelStats instances for the pooled 
        out-of-sample resuts reported by TSSB
        '''
        return self._wfsumm
    
    def selection_stats(self):
        '''Returns a SelectionStats instance or None.'''
        return self._selstats
    
    def add_fold(self, fold):
        '''Adds a new fold.'''
        self._folds.append(fold)
        
    def add_pooled_summ(self, model, stats):
        '''Adds a new PooledModelStats instance to the walk-forward summary.'''
        self._wfsumm[model] = stats
        
    def add_selection_stats(self, selstats):
        '''Adds a SelectionStats instance.'''
        self._selstats = selstats


class TSSBFold(object):
    '''
    TSSBFold represents the entirety of one walk-forward or find groups
    fold.  It is always identified by a name and contains zero or more
    ModelIterations
    '''
    def __init__(self, name):
        '''
        Constructor.
        
        :param string name: name of the fold
        '''
        self._name = name
        self._models = {}
        
    def name(self):
        '''Returns the name.'''
        return self._name
    
    def models(self):
        '''Returns a dictionary of ModelIteration instances.'''
        return self._models
    
    def add_model(self, model):
        '''Adds a new model to the fold.'''
        self._models[model.name()] = model        
        

class SelectionStats(object):
    '''
    SelectionStats is used to represent information that TSSB outputs
    when 'SHOW SELECTION COUNT' is present in the definition of one
    or more models 
    '''
    def __init__(self):
        '''Constructor.'''
        self._vars = {}
        self._models = {}
        
    def get_model_vars(self, model):
        '''
        Returns the list of variables for the specified model.
        
        :returns: list of tuples where each tuple is
                      ( string <VAR_NAME>, float <PCT>)
        '''
        return self._models[model]
    
    def list_all_gt(self, threshold):
        '''
        This averages percent usage for each variable across all models
        that were found and then returns sorted (descending) list of 
        variables whose average participation is >= <threshold>
        
        :param float threshold: threshold value for return list
        
        :returns: list of tuples (see get_model_vars for tuple format)
        '''
        ret = []
        for (var,pctlist) in self._vars.iteritems():
            avg = sum(pctlist) / len(self._models) 
            if (avg >= threshold):
                ret.append((var,avg))
                
        # now we want to sort this by decreasing pct
        ret = sorted(ret, key=lambda x: x[1],reverse=True)
                
        return ret

    def add_model_variable(self,model,variable,pct):
        '''
        Used by the parser to add a variable to a model
        '''
        if not self._models.has_key(model):
            self._models[model] = []
        self._models[model].append((variable,pct))
        if not self._vars.has_key(variable):
            self._vars[variable] = []
        self._vars[variable].append(pct)
        
                    
class ModelStats(object):
    '''
    simple struct-like object to store the statistics output by TSSB.
    This base class has fields common across any in-sample or out-of-
    sample test
    '''
    
    def __init__(self):
        '''Constructor - initialize all members to 0.'''
        self.target_grand_mean = 0.0
        self.total_cases       = 0
        self.num_above_high    = 0
        self.num_below_low     = 0
        self.mean_above_high   = 0.0
        self.mean_below_low    = 0.0
        self.roc_area          = 0.0
        self.long_only_imp     = 0.0
        self.short_only_imp    = 0.0
        self.long_total_ret    = 0.0
        self.short_total_ret   = 0.0
        
    def __str__(self, *args, **kwargs):
        ret = ''
        for i in self.__dict__:
            ret = ret + '%s: %s\n' % (i, self.__dict__[i])
        return ret[:-1]


class PooledModelStats(ModelStats):
    '''
    PooledModelStats extends the ModelStats class to include fields 
    that are only present in Pooled out-of-sample stats.
    '''

    def __init__(self):
        '''Constructor - initialize all members to 0.'''
        ModelStats.__init__(self)
        self.long_maxdd        = 0.0
        self.short_maxdd       = 0.0

    
class ModelDefn(object):
    '''
    ModelDefn represents an instantiated/trained model in TSSB.  This 
    is really only useful for the linear and quadratic regression models 
    where the full model definition is in the audit log, but those are
    common model types.  A model consists of zero (really one but could
    be empty for unsupported model types) or more factors where each 
    factor consists of:
        <coefficient> <indicator> [optional-power] 
    '''
    
    def __init__(self):
        '''Constructor.'''
        self._vars = []
        
    def get_factors(self):
        '''Returns the list of factors.'''
        return self._vars
    
    def add_factor(self, var, coef, power=None):
        '''
        Adds a new variable to the model definition.  
        
        :param string var: indicator/variable name
        :param float coef: coefficient
        :param string power: optional power specification, only 'Squared' is valid
        '''
        if power == 'Squared':
            power = 2
        else:
            power = 1
        self._vars.append((var,coef,power))

        
class ModelIteration(object):
    '''
    ModelIteration represents a particular model during one training, 
    walk-forward, or find groups "fold".  It is identified by a name
    and modeltype and contains a model definition, in-sample stats,
    and out-of-sample stats (not all of which are necessarily populated
    depending on the TSSB run type).
    '''
    
    def __init__(self, modeltype, name):
        '''
        Constructor.
        
        :param string modeltype: one of ['Model','Committee','Group']
        :param string name: name of the Model/Committee/Group, should 
                            be unique for a given TSSB run/log
        '''
        self._type = modeltype
        self._name = name
        self._defn = None
        self._insample = None
        self._oosample = None
        
    def name(self):
        '''Returns the name.'''
        return self._name
    
    def modeltype(self):
        '''Returns the type.'''
        return self._type
    
    def defn(self):
        '''Returns a ModelDefn instance or None.'''
        return self._defn
    
    def insample_stats(self):
        '''Returns a ModelStats instance for the in-sample stats or None.'''
        return self._insample
    
    def oosample_stats(self):
        '''Returns a ModelStats instance for the out-of-sample stats or None.'''
        return self._oosample
    
    def set_defn(self, defn):
        '''Sets the ModelDefn.'''
        self._defn = defn
        
    def set_insample_stats(self, stats):
        '''Sets the in-sample ModelStats instance.'''
        self._insample = stats

    def set_oosample_stats(self, stats):
        '''Sets the out-of-sample ModelStats instance.'''
        self._oosample = stats
        
