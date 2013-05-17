'''
Created on May 16, 2013

@author: bwilkinson
'''
'''
hedgeit.test.test_util

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

