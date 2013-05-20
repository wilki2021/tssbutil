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
tssbutil.test.testutil

Utility methods for the unit test infrastructure
'''

import re

def file_compare(file1, file2):
    """Compares the two files with handling for variable substitution,
    wildcarding, and truncation versus the reference file.
    
    @param file1 - the reference file with potential variables to be substituted
    @param file2 - target file
    
    Variables following an environment style syntax ($VARIABLE) listed in
    the subs array are substituted.
    
    Any * character found in the reference file is transferred over to the
    target before comparison
    
    If a ^ is present in the reference file, the target is truncated at that
    point prior to comparison
    """    
    subs = []
    
    linect = 0
    f1 = open(file1)
    f2 = open(file2)
    for line1 in f1:
        linect += 1
        line2 = f2.readline()
        
        # apply all substitutions on the reference file
        for sub in subs:
            line1 = re.sub(sub[0], sub[1], line1)
            
        # look for the wildcard character and transfer to the target            
        for i in range(0, len(line1)):
            if line1[i] == '*':
                line2 = line2[0:i] + '*' + line2[i+1:]
                
        # look for a terminate character
        for i in range(0, len(line1)):
            if line1[i] == '^':
                line2 = line2[0:i] + '^\n'
        
        if line1 != line2:
            print "at line %d, *%s* != *%s*" % (linect, line1, line2)
            return False

    line2 = f2.readline() 
    if line2:
        print "Extra lines in target at line %d: *%s*" % (linect+1, line2)
        return False
        
    return True

