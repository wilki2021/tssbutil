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