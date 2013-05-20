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
tssbutil.sedlite

Contains:
  sed_lite()
'''
import re

def sed_lite(src, targ, varmap):
    '''
    sed_lite performs a simple sed-like operation on a source file and
    writes the output to a target file.
    
    :param string src: source file - must be a readable file
    :param string targ: target file - must be a file that can be opened
                                      for writing
    :param dict varmap: substitutions to perform.  Each Key->Value pair 
                        in the dictionary is treated as a <from>,<to>
                        pattern.  the re.sub() function is used so regular
                        expression syntax may be present in either key
                        or value.
                        
    :throws: various file-related exceptions possible if any errors 
             opening or writing to source and target files respectively.
    '''
    f1 = open(src)
    f2 = open(targ,'w')
    for line in f1.readlines():
        for (from_,to) in varmap.iteritems():
            line = re.sub(from_, to, line)
        f2.write(line)
    f1.close()
    f2.close()