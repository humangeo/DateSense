'''Contains DSoptions class for DateSense package.
Customizing the directives the parser recognizes and altering what
assumptions it's allowed to make regarding the formatting of date
strings is easy! You can pass your own sets of directive options
and formatting rules to detect_format and other methods. See
methods like get_default_numoptions and get_default_rules and the
class attributes they reference, as well as the documentation for
the DSrule classes and NumOption and WordOption classes for some
examples and thorough descriptions of how things work.
'''



from .DStoken import DStoken
from .DSrule import *



# DSoptions object is the BMOC, this is what you'll want to use for basically everything you do,
class DSoptions(object):
    '''A DSoptions object contains the data used to track what's possible
    where in a date string and how likely it is.
    Everything you need to go from input to output should be an operation
    of or upon a DSoptions object.
    '''
    
    
    
    # Consts for NumOption and WordOption "common" attribute
    UNCOMMON = 1
    COMMON = 2 
    
    
    
    class NumOption(object):
        '''Contains data representing possible numeric directives.'''
        def __init__(self, directive, common, numrange):
            '''Constructs a NumOption object.
            Returns the NumOption object.
            
            :param directive: The directive string, like '%H' or '%y'.
            :param common: The initial score of possibilities for this directive.
                Recommended you use the DSoptions.COMMON and DSoptions.UNCOMMON
                consts.
            :param numrange: Min and max range for values corresponding to this
                directive. Should be indexed - recommended you use a tuple, like
                (1, 31). The value at index 0 will be considered the minimum and
                index 1 the maximum. The range is inclusive.
            '''
            self.directive = directive
            self.common = common
            self.numrange = numrange
            
        def includesvalue(self, value):
            '''Returns true if the value is valid for this directive, false otherwise.'''
            return value>=self.numrange[0] and value<=self.numrange[1]
    
    class WordOption(object):
        ''' Contains data representing possible alphabetical directives.'''
        def __init__(self, directive, common, words, matchlength=0):
            '''Constructs a WordOption object.
            Returns the WordOption object.
            
            :param directive: The directive string, like '%B' or '%p'.
            :param common: The initial score of possibilities for this directive.
                Recommended you use the DSoptions.COMMON and DSoptions.UNCOMMON
                consts.
            :param words: A set of possible words that should be considered matches
                for this directive, like ('am', 'pm') for the directive '%p'. These
                strings should be lower case.
            :param matchlength: (optional) If partial matches where the encountered
                word matches the start of the full word (e.g. 'mond' matching
                'monday') should be considered valid values for the directive,
                matchlength should be the minimum allowed length of those partial
                matches. If matchlength is set to 0 (which is the default) then no
                partial matches will be allowed.
            '''
            self.directive = directive
            self.common = common
            self.words = words
            self.matchlength = matchlength
            
        def includesvalue(self, value):
            '''Returns true if the value is valid for this directive, false otherwise.'''
            value_lower = value.lower()
            if self.matchlength and len(value_lower) >= self.matchlength:
                for word in self.words:
                    if word.startswith(value_lower):
                        return True
                return False
            else:
                return value_lower in self.words
    
    
    
    # These are the various directives recognized by python.
    # References:
    # http://www.tutorialspoint.com/python/time_strftime.htm
    # https://docs.python.org/2/library/time.html
    # http://pubs.opengroup.org/onlinepubs/009695399/functions/strptime.html

    # Common numeric date directives
    dir_y = NumOption('%y', COMMON, (0,99))     # 2-digit year
    dir_Y = NumOption('%Y', COMMON, (0,9999))   # 4-digit year
    dir_m = NumOption('%m', COMMON, (1,12))     # Month as a number
    dir_d = NumOption('%d', COMMON, (1,31))     # Day of the month
    # Common numeric time directives
    dir_H = NumOption('%H', COMMON, (0,23))     # 24-hour
    dir_I = NumOption('%I', COMMON, (1,12))     # 12-hour
    dir_M = NumOption('%M', COMMON, (0,59))     # Minutes
    dir_S = NumOption('%S', COMMON, (0,61))     # Seconds
    # ISO 8601 numeric date directives
    dir_g = NumOption('%g', UNCOMMON, (0,99))   # 2-digit year corresponding to ISO week number
    dir_G = NumOption('%G', UNCOMMON, (0,9999)) # 4-digit year corresponding to ISO week number
    dir_V = NumOption('%V', UNCOMMON, (1,53))   # ISO 8601 week number of the year
    dir_u = NumOption('%u', UNCOMMON, (1,7))    # Weekday as a number (1-7)
    # Uncommon numeric directives
    dir_j = NumOption('%j', UNCOMMON, (1,366))  # Day of the year
    dir_C = NumOption('%C', UNCOMMON, (0,99))   # 2-digit century
    dir_w = NumOption('%w', UNCOMMON, (0,6))    # Weekday as a number (0-6)
    dir_U = NumOption('%U', UNCOMMON, (0,53))   # Week number of the year, starting with the first Sunday
    dir_W = NumOption('%W', UNCOMMON, (0,53))   # Week number of the year, starting with the first Monday
    # Alphabetical directives
    dir_b = WordOption('%b', COMMON, ('jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'))
    dir_B = WordOption('%B', COMMON, ('january','february','march','april','may','june','july','august','september','october','november','december'))
    dir_p = WordOption('%p', COMMON, ('am','pm'))
    dir_a = WordOption('%a', UNCOMMON, ('sun','mon','tue','wed','thu','fri','sat'))
    dir_A = WordOption('%A', UNCOMMON, ('sunday','monday','tuesday','wednesday','thursday','friday','saturday'))
    dir_Z = WordOption('%Z', UNCOMMON, ('utc','gmt')) # not a complete list by any means
    # Timezone directive
    dir_z = '%z' # Special case: Time zones match tokens like +0100 and -0300
    
    # Default formatting rules, should be suitable for mostly any English-language date format
    # Format rules tell the parser what dates usually look like and how specifically to act on those assumptions.
    rule_delim_date =               DSDelimiterRule(2, 0, ('%d','%m','%y','%Y'), ('-','/'))         # Days, months, years usually delimited by '-' or '/'
    rule_delim_ISO_date =           DSDelimiterRule(2, -3, ('%G','%g','%V','%u','%j'), ('-','W'))   # ISO 8601 date directives should always be adjacent to '-' (or sometimes 'W')
    rule_delim_time =               DSDelimiterRule(2, 0, ('%H','%I','%M','%S'), ':')               # hours, minutes, seconds usually delimited by ':'
    rule_range_years =              DSLikelyRangeRule(1, -1, ('%Y','%G'), (1000,3000))              # Year is probably between 1000 and 3000
    rule_range_cent =               DSLikelyRangeRule(0, -1, '%C', (10,30))                         # Century is probably between 10 and 30
    rule_range_secs =               DSLikelyRangeRule(0, -1, '%S', (0,59))                          # Seconds CAN be 60 or 61 due to leap seconds, but that's very rare. Normally it'll be in the range (0, 59).
    rule_pattern_hms =              DSPatternRule(3, 0, (('%H','%I'),':','%M',':','%S'), 1)         # hh:mm:ss
    rule_pattern_hm =               DSPatternRule(1, 0, (('%H','%I'),':','%M'), 1)                  # hh:mm
    rule_pattern_12hr =             DSPatternRule(3, 0, ('%I','%M','%p'),4)                         # hh:mm<:ss> %p (12-hour with AM/PM)
    rule_pattern_tz =               DSPatternRule(3, 0, ('%Z','%z'), 1)                             # Timezone + offset
    rule_pattern_US_date =          DSPatternRule(4, 0, (('%m','%b','%B'),'%d',('%y','%Y')), 2)     # American - months then days then years
    rule_pattern_US_Bd =            DSPatternRule(3, 0, ('%d',('%m','%b','%B'),('%y','%Y')), 2)     # European - days then months then years
    rule_pattern_EU_date =          DSPatternRule(2, 0, (('%B','%b'),' ','%d'), 1)                  # American - word month then days
    rule_pattern_EU_dB =            DSPatternRule(2, 0, ('%d',' ',('%B','%b')), 1)                  # European - days then word month
    rule_pattern_ymd =              DSPatternRule(4, 0, ('%Y','-','%m','-','%d'), 1)                # YYYY-MM-DD
    rule_pattern_verbose_day =      DSPatternRule(1, 0, ('day','%d'), 4)                            # Word "day" typically precedes the day
    rule_pattern_verbose_month =    DSPatternRule(1, 0, ('month',('%m','%b','%B')), 4)              # Word "month" typically precedes the month
    rule_pattern_verbose_year =     DSPatternRule(1, 0, ('year',('%Y','%y')), 4)                    # Word "year" typically precedes the year
    rule_pattern_verbose_time =     DSPatternRule(1, 0, ('time',('%H','%I')), 4)                    # Word "time" typically precedes the time
    rule_pattern_ISO_W =            DSPatternRule(4, 0, ('W','%V'), 1)                              # ISO 8601 date formats often include W%V
    rule_pattern_ISO_date =         DSPatternRule(4, 0, (('%G','%g'),'-','W','%V','-','%u'), 1)     # ISO 8601 date with week number
    rule_pattern_ISO_week =         DSPatternRule(3, 0, (('%G','%g'),'-','W','%V'), 1)              # ISO 8601 week
    rule_pattern_ISO_ordinal =      DSPatternRule(2, 0, (('%G','%g'),'-','%j'), 1)                  # ISO 8601 ordinal date
    rule_mutexc_24h_12h =           DSMutExclusionRule(0, -2, ('%H',('%I','%p')))                   # 24-hour and 12-hour don't mix
    rule_mutexc_yr_digits =         DSMutExclusionRule(0, -2, ('%Y','%y','%G','%g'))                # No more than one year directive
    rule_mutexc_yr_cent =           DSMutExclusionRule(0, -2, (('%Y','%G'),'%C'))                   # no sense in both YYYY and century
    rule_mutexc_months =            DSMutExclusionRule(0, -2, ('%B','%b','%m'))                     # No more than one month directive
    rule_mutexc_wkdays =            DSMutExclusionRule(0, -2, ('%A','%a','%u','%w'))                # No more than one weekday directive
    rule_mutexc_weeks =             DSMutExclusionRule(0, -2, ('%V','%U','%W'))                     # No more than one week of year directive
    
    # These methods are for getting default parser options.
    @staticmethod
    def get_default_numoptions():
        '''Returns the default set of numeric directive options.'''
        return (
            DSoptions.dir_y, DSoptions.dir_Y, DSoptions.dir_m, DSoptions.dir_d,
            DSoptions.dir_H, DSoptions.dir_I, DSoptions.dir_M, DSoptions.dir_S,
            DSoptions.dir_g, DSoptions.dir_G, DSoptions.dir_V, DSoptions.dir_u,
            DSoptions.dir_C, DSoptions.dir_w, DSoptions.dir_j, DSoptions.dir_W, DSoptions.dir_U
        )
        
    @staticmethod
    def get_default_wordoptions():
        '''Returns the default set of alphabetical directive options.'''
        return (
            DSoptions.dir_b, DSoptions.dir_B, DSoptions.dir_p,
            DSoptions.dir_a, DSoptions.dir_A, DSoptions.dir_Z
        )
        
    @staticmethod
    def get_default_tzoffsetdirective():
        '''Returns the default timezone offset directive.'''
        return DSoptions.dir_Z
    
    @staticmethod
    def get_default_rules():
        '''Returns the default set of formatting rules.'''
        return (
            DSoptions.rule_delim_date, DSoptions.rule_delim_ISO_date, DSoptions.rule_delim_time,
            DSoptions.rule_range_years, DSoptions.rule_range_cent, DSoptions.rule_range_secs,
            DSoptions.rule_pattern_hms, DSoptions.rule_pattern_hm, DSoptions.rule_pattern_12hr, DSoptions.rule_pattern_tz,
            DSoptions.rule_pattern_US_date, DSoptions.rule_pattern_US_Bd,
            DSoptions.rule_pattern_EU_date, DSoptions.rule_pattern_EU_dB,
            DSoptions.rule_pattern_ymd,
            DSoptions.rule_pattern_verbose_day, DSoptions.rule_pattern_verbose_month,
            DSoptions.rule_pattern_verbose_year, DSoptions.rule_pattern_verbose_time,
            DSoptions.rule_pattern_ISO_W, DSoptions.rule_pattern_ISO_date,
            DSoptions.rule_pattern_ISO_week, DSoptions.rule_pattern_ISO_ordinal,
            DSoptions.rule_mutexc_24h_12h, DSoptions.rule_mutexc_yr_digits, DSoptions.rule_mutexc_yr_cent,
            DSoptions.rule_mutexc_months, DSoptions.rule_mutexc_wkdays, DSoptions.rule_mutexc_weeks
        )


    
    # Constructor
    def __init__(self, formatRules, numOptions, wordOptions, tzOffsetDirective):
        '''Constructs a DSoptions object.
        Returns the DSoptions object.
        
        :param formatRules: A set of rule objects such as those found in
            DSrule.py which inform the parser of what assumptions it should
            make regarding how input data will normally be formatted.
        :param numOptions: A set of NumOption objects to inform the parser of
            possible numeric directives.
        :param wordOptions: A set of WordOption objects to inform the parser of
            possible alphabetical directives.
        :param tzOffsetDirective: Timezone offset directives are a special
            case - this string informs the parser of what directive to use for
            them. (You probably want this to be '%z'.)
        '''
            
        self.allowed = []
        '''The allowed attribute tracks what directives are considered to be
        possible and where.
        It contains a list of lists of DStoken objects. The lists contained
        within correspond to each token in the sequence derived from the
        tokenized date string input. The DStoken objects contained within those
        lists represent each possibility being evaluated for the position the
        list corresponds to.'''
        
        self.numranges = []
        '''The numranges attribute tracks the minimum and maximum encountered
        values for numeric tokens in the date strings.
        This data is used by Likely Range rules. It's a list of lists. The lists
        contained within correspond to each token in the sequence derived from
        the tokenized date string input. Each of those lists contains two items.
        The item at index 0 is the lowest value encountered for the token and
        the item at index 1 is the highest value encountered. If the value at
        an index of numranges is None instead of a list, it indicates that no
        numeric values were encountered for the corresponding token.'''
        
        self.numoptions = numOptions
        self.wordoptions = wordOptions
        self.tzoffsetdirective = tzOffsetDirective
        self.formatrules = formatRules
        
        
        
    # These convenience methods simplify the flow of data so that in most cases you won't have to worry about putting the pieces together yourself
        
    # Initialize and process everything for a data set in one convenient method. Recommended you use this unless you're sure of what you're doing.
    @staticmethod
    def detect_format(dates, formatRules=None, numOptions=None, wordOptions=None, tzOffsetDirective=None):
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
        
        # Handle default values for various options
        formatRules = formatRules if formatRules else DSoptions.get_default_rules()
        numOptions = numOptions if numOptions else DSoptions.get_default_numoptions()
        wordOptions = wordOptions if wordOptions else DSoptions.get_default_wordoptions()
        tzOffsetDirective = tzOffsetDirective if tzOffsetDirective else DSoptions.get_default_tzoffsetdirective()
        
        # Do the format detection
        options = DSoptions(formatRules,numOptions,wordOptions,tzOffsetDirective)
        options.initialize(dates)
        options.process()
        
        # All done!
        return options
        
    def initialize(self, dates):
        '''Initialize token possibility data for a set of date strings.
        
        :param dates: A set of identically-formatted date strings for which
            the formatting should be detected.
        '''
        # If it's just one string, turn it into a collection like the methods expect
        if isinstance(dates, basestring):
            dates = [ dates ]
        # Do the initializing
        date_tokens = DStoken.tokenize_date(dates[0])
        self.init_with_date_tokens(date_tokens)
        self.cull_with_dates(dates)
    
    def process(self, dupepenalty=-2):
        '''Process token possibility data for a set of date strings by
        applying rules and checking for duplicate directives.
        Each token possibility will have a score assigned to it which
        represents how likely the parser believes it is to be the correct
        directive or string at that position, relative to the other
        possibilities at that position. (The higher the score, the better the
        fit.)
        
        :param dupepenalty: (optional) How the score of duplicate token
            possibilities should be affected, as judged by
            DSoptions.penalize_duplicates().
        '''
        self.apply_rules(self.formatrules)
        if dupepenalty:
            self.penalize_duplicates(dupepenalty)
        
    def get_format_tokens(self):
        '''Returns a list of the parser's current best guess for what matches each date token.'''
        tokens = []
        for toklist in self.allowed:
            maxtok = DStoken.get_max_score(toklist)
            if maxtok:
                tokens.append(maxtok)
        return tokens
    
    
    
    # These methods form the inner clockwork that makes the algorithm function.
    # init_with_date_tokens is what you would call first, to generate an initial list of possibilities for each token in a date string
    # cull_with_dates is what you would call next, to use a list of date strings to further inform the parser about what tokens have allowed values for which directives
    # cull_with_date_tokens is called by cull_with_dates on individual tokenized date strings in the list passed to it
    # apply_rules is what you would call after cull_with_dates, it applies a set of rules to the possibility data (Rules are assumptions the parser is allowed to make regarding how dates should be formatted)
    # penalize_duplicates is what you would call last, it attempts to handle the scenario where a single directive is considered the most likely in more than one position (It assumes that a date format ought to have no more than one of each directive)
    
    def init_with_date_tokens(self, date_tokens):
        '''Initialize token possibility data using a single tokenized date.
        The tokenized date string is used to generate a list of possible
        directives at each position, based on whether the value there is
        a possible value for each NumOption and WordOption.
        
        :param date_tokens: A list of DStoken objects returned by the
            DStoken.tokenize_date() method, where the method's argument
            is a date string.
        '''
        # build a map of what direrctives/whatever are allowed in the various places
        for date_token in date_tokens:
            numrange = None
            # add the token as a potential decorator
            allow_here = [DStoken.create_decorator(date_token.text)]
            # if token is a number
            if date_token.is_number():
                number = int(date_token.text)
                for option in self.numoptions:
                    if option.includesvalue(number):
                        allow_here.append(DStoken.create_number(option))
                        numrange = [number,number]
            # if token is a word
            elif date_token.is_word():
                for option in self.wordoptions:
                    if option.includesvalue(date_token.text):
                        allow_here.append(DStoken.create_word(option))
            # if token is a timezone
            elif date_token.is_timezone():
                tztok = DStoken.create_timezone(self.tzoffsetdirective)
                tztok.score += 1
                allow_here.append(tztok)
            # add the list of allowed directives/whatever for this token to the overall list
            self.allowed.append(allow_here)
            self.numranges.append(numrange)
            
    def cull_with_dates(self, dates):
        '''Cull token possibility data using a set of date strings. The
        values for each token in the date strings are checked against the
        possibilities for that position and if a value is found to lie
        outside the possible values for a directive, that directive is
        discarded as a possibility for the location.
        
        :param dates: A set of identically-formatted date strings.
        '''
        for date in dates:
            date_tokens = DStoken.tokenize_date(date)
            self.cull_with_date_tokens(date_tokens)
        
    def cull_with_date_tokens(self, date_tokens):
        '''Cull token possibility data using a single tokenized date. The
        value for each token in the tokenized date string os checked against
        the possibilities for that position and if a value is found to lie
        outside the possible values for a directive, that directive is
        discarded as a possibility for the location.
        
        :param date_tokens: A list of DStoken objects returned by the
            DStoken.tokenize_date() method, where the method's argument
            is a date string.
        '''
        itrrange = min(len(self.allowed),len(date_tokens))
        for i in range(0,itrrange):
            for j in xrange(len(self.allowed[i])-1,-1,-1): # iterate backwards so we can remove elements without hiccuping
                tok = self.allowed[i][j]
                # if it's not a directive, just check for equivalency
                if tok.is_decorator():
                    if tok.text != date_tokens[i].text:
                        del self.allowed[i][j]
                # if it is a directive, verify it's the same kind (number/word/timezone)
                elif tok.kind != date_tokens[i].kind:
                    del self.allowed[i][j]
                # if it is a directive and it's the right kind, make sure the data fits
                else:
                    # if it's a number, check that this is in the correct range
                    if date_tokens[i].is_number():
                        number = int(date_tokens[i].text)
                        if tok.option.includesvalue(number):
                            self.numranges[i][0] = min(number,self.numranges[i][0])
                            self.numranges[i][1] = max(number,self.numranges[i][1])
                        else:
                            del self.allowed[i][j]
                    # if it's a word, check that it meets the same requirements
                    elif date_tokens[i].is_word():
                        if not tok.option.includesvalue(date_tokens[i].text):
                            del self.allowed[i][j]

    def apply_rules(self, rules):
        '''Apply all rules in a set to token possibility data.
        Scores for token possibilities will be affected according to the
        assumptions the parser is instructed to make based on the rules
        provided.
        It's worth noting that rules will be evaluated in the order they appear.
        In most cases this won't matter but you may run into unexpected behavior
        if you're not careful about the ordering.
        Delimiter and likely range rules act completely independently of what
        the scores of the possibilities are they can apply to. Pattern rules
        only recognize directives as being eligible for the sequence if their
        score at the time of evaluation is greater than zero. (Non-directive
        strings are not limited in this way.) Mutual exclusion rules decide
        which directive to act in favor of by which has the highest-scoring
        instance.
        
        :param rules: A set of rule objects, like DSPatternRule or
            DSMutExclusionRule.
        '''
        for rule in rules:
            rule.apply(self)

    # This solution isn't perfect but if there are indeed duplicates then the
    # root of the problem probably lies with the rules being used, that they
    # would produce this sort of scenario in the first place.
    def penalize_duplicates(self, dupepenalty):
        '''Try to handle the presence of duplicate high-scoring directives,
        since there's probably no more than one of each directive in any
        given date string.
        The process is this: First, if a possibility is the only high score
        anywhere, its score is affected anywhere it's not the only high score.
        Second, if a possibility is a high score in more than one place, the
        highest-scoring instance out of those is found and the score for that
        directive is affected everywhere else.
        
        :param dupepenalty: (optional) How the score of duplicate token
            possibilities should be affected; duplicate possibilities will
            have their scores incremented by this number.
        '''
        # First: If a possibility is the only high score anywhere, reduce its score anywhere it's not the only high score
        # Find where any possibility is the solitary high score
        hightoks = []
        for toklist in self.allowed:
            high = DStoken.get_all_max_score(toklist)
            if len(high) == 1 and (not high[0].is_decorator()):
                if high[0].text not in hightoks:
                    hightoks.append(high[0].text)
        # Now reduce the scores of those possibilities everywhere else
        for toklist in self.allowed:
            high = DStoken.get_all_max_score(toklist)
            if len(high) > 1:
                for tok in toklist:
                    if tok.text in hightoks:
                        tok.score += dupepenalty
        # Second: If a possibility is a high score in more than one place:
        # Find the highest-scoring instance as a high score of each possibility (lowest index breaks ties)
        hightoks = {}
        for toklist in self.allowed:
            high = DStoken.get_all_max_score(toklist)
            for tok in high:
                gethigh = hightoks.get(tok.text, None)
                if not gethigh:
                    hightoks[tok.text] = [tok]
                else:
                    hightoks[tok.text].append(tok)
        # Affect the score of those possiblities everywhere else
        for key, value in hightoks.items():
            highest = None
            for tok in value:
                if (not highest) or tok.score > highest.score:
                    highest = tok
            for toklist in self.allowed:
                for tok in toklist:
                    if tok.text == key and tok != highest:
                        tok.score += dupepenalty
                
    
    
    
    # These are methods for returning various string representations of this object
    
    def get_format_string(self, replace_percent=True, blank_if_unrecognized=True):
        '''Returns the date format as determined by the parser.
        :param replace_percent: (optional) In python date format strings
        literal '%' characters must be represented as '%%'. If this
        argument is set to true, the method will account for stray '%'
        characters by replacing them with '%%'.
        :param blank_if_unrecognized: (optional) If True, a blank string
        will be returned if either no directives were found or if the
        parser recognized no possibilities for any token. Defaults to
        True.
        '''
        string = ''
        tokens = self.get_format_tokens()
        founddir = False
        validtokens = 0
        for tok in tokens:
            if replace_percent and tok.is_decorator():
                string += tok.text.replace('%','%%') # Literal '%' characters must be represented by '%%' in python date formats
            else:
                string += tok.text
            founddir = founddir or (not tok.is_decorator())
            validtokens += 1
        if (not blank_if_unrecognized) or (founddir and (validtokens == len(self.allowed))):
            return string
        else:
            return ''
        
    def get_short_debug_string(self, tokdelimiter=', ', posdelimiter='\n'):
        '''Returns a string representing the highest-scoring possibilities for each token.'''
        string = ''
        firstpos = True
        for toklist in self.allowed:
            if firstpos:
                firstpos = False
            else:
                string += posdelimiter
            if len(toklist):
                firsttok = True
                for tok in DStoken.get_all_max_score(toklist):
                    if firsttok:
                        firsttok = False
                    else:
                        string += tokdelimiter
                    string += str(tok)
            else:
                string += 'NONE'
        return string
        
    def get_long_debug_string(self, tokdelimiter=', ', posdelimiter='\n'):
        '''Returns a string representing all the possibilities for each token.'''
        string = ''
        firstpos = True
        for toklist in self.allowed:
            if firstpos:
                firstpos = False
            else:
                string += posdelimiter
            if len(toklist):
                firsttok = True
                toklist.sort(key = lambda DStoken: -DStoken.score) # Sort the list by descending score to make it more immediately readable
                for tok in toklist:
                    if firsttok:
                        firsttok = False
                    else:
                        string += tokdelimiter
                    string += str(tok)
            else:
                string += 'NONE'
        return string
    
    # General-purpose casting to string
    def __str__(self):
        return self.get_format_string()
    def __repr__(self):
        return self.get_long_debug_string(',', '; ')
    
        

    
