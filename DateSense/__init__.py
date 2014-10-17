'''DateSense is for determining the format of a date string, or
for a set of many identically-formatted date strings.
For a general-purpose parser that will work for most English-
language date formats, DSoptions.detect_format(dates) will return
an object that you can cast to string (or explicitly call its
get_format_string method) for a date format string for use with
datetime.strptime. For info on how you would go about customizing
the way the parser  works and what assumptions it's allowed to
make regarding the formatting of its input, take a look at the
documentation for DSoptions.py.
'''

from .DStoken import DStoken
from .DSrule import *
from .DSoptions import DSoptions

__version__ = '1.0.1'
'''DateSense version number'''

def detect_format( dates, formatRules=None, numOptions=None, wordOptions=None, tzOffsetDirective=None ):
    '''Initialize and process everything for a data set in one convenient
    method. (Recommended you use this unless you're sure of what you're
    doing.)
    Returns a DSoptions object containing date format information.
    
    :param dates: A set of identically-formatted date strings for which
        the formatting should be detected.
    :param formatRules: (optional) A set of rule objects such as those
        found in DSrule.py which inform the parser of what assumptions it
        should make regarding how input data will normally be formatted.
        Defaults to the value returned by DSoptions.get_default_rules().
    :param numOptions: (optional) A set of NumOption objects to inform the
        parser of possible numeric directives. Defaults to the value
        returned by DSoptions.get_default_numoptions().
    :param wordOptions: (optional) A set of WordOption objects to inform
        the parser of possible alphabetical directives. Defaults to the
        value returned by DSoptions.get_default_wordoptions().
    :param tzOffsetDirective: (optional) Timezone offset directives
        are a special case - this string informs the parser of what
        directive to use for them. (You probably want this to be '%z'.)
        Defaults to the value returned by
        DSoptions.get_default_tzoffsetdirective().
    '''
    return DSoptions.detect_format( dates, formatRules, numOptions, wordOptions, tzOffsetDirective )
    
    