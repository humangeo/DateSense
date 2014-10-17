'''Unit tests for DateSense package'''



#from DateSense.DSoptions import DSoptions
import DateSense
from datetime import datetime
import unittest



class Datetest(object):
    '''Class for testing various formats'''
    
    defaultData = datetime(2013, 4, 15, 14, 4, 11), datetime(2013, 10, 25, 10, 50, 13), datetime(2014, 1, 1, 2, 0, 0)

    def __init__(self, case=None, expected=None, data=None):
        '''Constructor'''
        self.case = case
        self.expected = expected if expected!=None else case
        
        if data:
            self.data = data
        elif case:
            self.data = Datetest.gendata(Datetest.defaultData, case)
        else:
            self.data = None
            
        self.options = None
        self.formatstr = None

    @staticmethod
    def gendata(dates, dateformat):
        '''Make date strings from a collection of datetime objects'''
        data = []
        for date in dates:
            datestr = datetime.strftime(date, dateformat)
            data.append(datestr)
        return data

    def run(self):
        '''Run the test, returns true if passed and false if failed.'''
        self.options = DateSense.DSoptions.detect_format(self.data)
        self.formatstr = self.options.get_format_string()
        success = (self.formatstr == self.expected)
        
        if success:
            casestr = " From: '" + (self.case if self.case else str(self.data)) + "'"
            print "GOOD: Got: '" + self.formatstr + "'" + casestr
            
        else:
            print "FAIL: Got: '" + self.formatstr + "' Expected: '" + self.expected + "'"
            print self.options.get_long_debug_string()
            
        return success
        


class TestDateSense(unittest.TestCase):
    '''Class contains tests'''
    
    def test_01(self):
        '''Check case retention for non-directive parts of date strings'''
        assert Datetest( case="i I %Y" ).run()

    def test_02(self):
        '''Check standard format'''
        assert Datetest( case="%m/%d/%y %H:%M" ).run()

    def test_03(self):
        '''Check nonstandard format'''
        assert Datetest( case="%a %b %d %H:%M:%S %Y" ).run()

    def test_04(self):
        '''Check standard format'''
        assert Datetest( case="%Y-%m-%d %H:%M:%S" ).run()

    def test_05(self):
        '''Check nonstandard format'''
        assert Datetest( case="%Y, %b %d" ).run()

    def test_06(self):
        '''Check nonstandard format'''
        assert Datetest( case="%A, %d. %B %Y %I:%M%p" ).run()

    def test_07(self):
        '''Check verbose format'''
        assert Datetest( case="The day is %d, the month is %B, the time is %I:%M%p" ).run()

    def test_08(self):
        '''Check standard format'''
        assert Datetest( case="%Y-%m-%dT%H:%M:%S" ).run()

    def test_09(self):
        '''Don't use '/' or '-' as date delimiters'''
        assert Datetest( case="%d.%m.%Y" ).run()

    def test_10(self):
        '''Lots of word directives'''
        assert Datetest( case="%b %B %a %A %p" ).run()

    def test_11(self):
        '''Lots of duplicate word directives'''
        assert Datetest( case="%b %B %a %A %A %A %p" ).run()
        
    def test_12(self):
        '''Check radically nonstandard format'''
        assert Datetest( case="%Y %I %M %d %p %B" ).run()

    def test_13(self):
        '''ISO 8601 date'''
        assert Datetest( case="%G-W%V" ).run()

    def test_14(self):
        '''ISO 8601 date with week number'''
        assert Datetest( case="%G-W%V-%u" ).run()

    def test_15(self):
        '''ISO 8601 ordinal date'''
        assert Datetest( case="%G-%j" ).run()
    
    def test_16(self):
        '''Check nonstandard format'''
        assert Datetest( case="%A, %d. %B %Y %I:%M%p" ).run()
        
    def test_17(self):
        '''Make sure it doesn't choke on having just one string as input'''
        assert Datetest( data="16 Oct 2014", expected="%d %b %Y" ).run()
    
    def test_18(self):
        '''Expect the parser to spit out the most sensible assumption instead of the actual format'''
        assert Datetest( case="Mon Sep %p", expected="%a %b %p" ).run()

    def test_19(self):
        '''Not equipped to handle this sort of nonsense, make sure a blank string is returned'''
        assert Datetest( case="%Y%m%d", expected="" ).run()
        
    def test_20(self):
        '''Walter Sobchak is not a date, make sure a blank string is returned'''
        assert Datetest( data="Do you see what happens when you find a stranger in the Alps?", expected="" ).run()
        
    def test_21(self):
        '''Movies are not dates, make sure a blank string is returned'''
        assert Datetest( data=("2001: A Space Odyssey", "2010: The Year We Make Contact") , expected="" ).run()
    
    
    
if __name__ == '__main__':
    print "DateSense version: " + DateSense.__version__
    unittest.main()
    
    
    
    
            
    
    
    
    
