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
                
    def vars(self):
        return self._vars
    
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