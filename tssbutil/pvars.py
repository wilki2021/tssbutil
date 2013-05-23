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
tssbutil.pvars

Contains:
   class VarParser
'''
import sys

class VarParser(object):
    '''
    VarParser parses a list of TSSB indicator definitions.  The syntax is 
    assumed as follows:
    
      ; anything after a semicolon is a comment
      <whitespace> is ignored
    any non-empty line (after stripping comments and whitespace) must be
    have exactly one colon that splits the line into an indicator name
    and the indicator definition
      <indicator name> : <indicator defn>
    '''

    def __init__(self,filename):
        '''
        Constructor
        '''
        self._fname = filename
        self._vars = {}
        self._varlist = []
        self.__parse()
        
    def __parse(self):
        '''Top-level parse method (PRIVATE).'''
        f = open(self._fname)
        for l in f.readlines():
            # first strip any comments
            if l.find(';') != -1:
                l = l[:l.find(';')]
            # now get rid of any extraneous whitespace
            l = l.strip()
            
            # Now if anything left it should be a variable of the form
            # <var name>: <var defn>
            if len(l):
                parts = l.split(':')
                if len(parts) != 2:
                    print 'Error while parsing ^%s^' % l
                varname = parts[0].strip()
                vardefn = parts[1].strip()
                self._vars[varname] = vardefn
                self._varlist.append(varname)
                
    def vars(self):
        return self._vars
    
    def varlist(self):
        return self._varlist
    
if __name__ == '__main__':
    '''
    This is just a quick-and-dirty dump of the information that was 
    parsed.  It enables this Python module to be called directly with
    the name of the variable list to pass as a command-line arg.
    '''
    if len(sys.argv) < 2:
        print 'usage: pvars.py <variable list>'
        sys.exit(1)

    v = VarParser(sys.argv[1])
    for (var,defn) in v.vars().iteritems():
        print 'var:%s,defn:%s' % (var,defn)            