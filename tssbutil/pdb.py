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
tssbutil.pdb

Contains:
   class DbParser
'''

class DbParser(object):
    '''
    DbParser parses a TSSB database file (typically output via a WRITE
    DATABASE command).  The format is relatively simple - it contains 
    a header row and then data rows with whitespace separated values.
    The first two columns of the file must always be 'Date' and 'Market'.
    The remainder of the columns will be any combination of indictor,
    model, committee, etc. output.  For now it is assumed that the 
    combination of Day/Market is always unique - TSSB may or may not
    impose this condition on its own but regardless it is sufficient
    for now.
    '''
    
    def __init__(self, filename):
        '''
        Constructor.
        
        :param string filename: database file to parse
        
        :throws Exception: on file not found or Day/Market columns not present
        '''
        self.__filename = filename
        self.__columns = []
        self.__rows = {}
        
        self.__parse()
    
    def get_value(self, date, market, col):
        '''
        Retrieves a value from the database file.
        
        :param string date: date portion of the retrieval key
        :param string market: market portion of the retrieval key
        :param string col: column to retrieve
        
        :returns float: value for specified date, market, column
        :throws KeyError: if Date/Market not present
        :throws ValueError: if column not found in database
        '''
        key = '%s-%s' % (date, market)
        return float(self.__rows[key][self.__columns.index(col)])
    
    def __parse(self):
        '''Parses the database file (PRIVATE),'''
        f = open(self.__filename)
        
        # get the columns
        line = f.readline()
        self.__columns = line.strip().split()
        
        if self.__columns[0] != 'Date' or self.__columns[1] != 'Market':
            raise Exception('Error-first two columns must be Date and Market, not %s and %s' % (self.__columns[0],self.__columns[1]))
        
        for line in f.readlines():
            line = line.strip()
            if len(line):
                values = line.split()
                assert( len(values) == len(self.__columns) )
                key = '%s-%s' % (values[0], values[1])
                self.__rows[key] = values
                
        f.close()