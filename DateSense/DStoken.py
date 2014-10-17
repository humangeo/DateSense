'''Contains DStoken class for DateSense package.'''



# Used by the parser for keeping track of what goes where, and what can possibly go where
class DStoken(object):
    '''DStoken objects are used by the parser for keeping track of what
    goes where in tokenized date strings, and what can possibly go where
    in format strings as determined by a DSoptions options.
    In the context of tokenized date strings: each DStoken object
    contains information on what's actually there in the string.
    In the context of DSoptions allowed lists: each DStoken object
    contains information on what directives (or non-directive strings)
    are allowed to go where, and how likely the parser thinks each must
    be. (The higher a DStoken's score, the more likely it's considered
    to be.)
    '''
    
    
    # Consts for the different kinds of tokens recognized
    KIND_DECORATOR = 0
    KIND_NUMBER = 1
    KIND_WORD = 2
    KIND_TIMEZONE = 3
    
    # Const for number of characters timezone offset numbers are expected to be, e.g. +0100 or -0300 (You definitely want this value to be 4.)
    TIMEZONE_LENGTH = 4


    
    # Constructors
    
    def __init__(self, kind, text, option=None):
        '''Constructs a DStoken object.
        You probably want to be using the kind-specific constructors
        instead of this one: create_decorator, create_number,
        create_word, and create_timezone.
        Returns the DStoken object.
        
        :param kind: The DStoken kind, which should be one of
            DStoken.KIND_DECORATOR, DStoken.KIND_NUMBER,
             DStoken.KIND_WORD, DStoken.KIND_TIMEZONE.
        :param text: A string to associate with this this object.
        :param option: (optional) A NumOption or WordOption object to
            associate with this object. Defaults to None.
        '''
        self.kind = kind
        self.text = text
        self.option = option
        if option:
            self.score = option.common
        else:
            self.score = 0
    
    @staticmethod
    def create_decorator(text):
        '''Constructs a DStoken object for a decorator token.
        Decorator token possibilities are those which correspond to
        no directive. For example, the ':' characters in '%H:%M:%S'.
        Returns the DStoken object.
        
        :param text: A string to associate with this this object.
        '''
        return DStoken(DStoken.KIND_DECORATOR, text, None)
    
    @staticmethod
    def create_number(option):
        '''Constructs a DStoken object for a numeric token.
        Returns the DStoken object.
        
        :param option: A directive option to associate with this this
            object and to derive its text attribute from. Should be a
            NumOption object.
        '''
        return DStoken(DStoken.KIND_NUMBER, option.directive, option)
    
    @staticmethod
    def create_word(option):
        '''Constructs a DStoken object for an alphabetical token.
        Returns the DStoken object.
        
        :param option: A directive option to associate with this this
            object and to derive its text attribute from. Should be a
            WordOption object.
        '''
        return DStoken(DStoken.KIND_WORD, option.directive, option)
    
    @staticmethod
    def create_timezone(directive):
        '''Constructs a DStoken object for a timezone offset token.
        Returns the DStoken object.
        
        :param directive: A string to associate with this this object.
            (You probably want this to be '%z'.)
        '''
        return DStoken(DStoken.KIND_TIMEZONE, directive, None)
        
        
            
    # Get a string representation
    
    def __str__(self):
        kinds = "dec", "num", "word", "tz"
        return kinds[self.kind] + ":'" + self.text + "'(" + str(self.score) + ")"
        
    def __repr__(self):
        return self.__str__()
        
        
        
    # Simple methods for checking whether the token is a specific kind
    
    def is_decorator(self):
        '''Returns true if the DStoken is for a decorator, false otherwise.'''
        return self.kind == DStoken.KIND_DECORATOR
        
    def is_number(self):
        '''Returns true if the DStoken is for a numeric directive, false otherwise.'''
        return self.kind == DStoken.KIND_NUMBER
        
    def is_word(self):
        '''Returns true if the DStoken is for an alphabetical directive, false otherwise.'''
        return self.kind == DStoken.KIND_WORD
        
    def is_timezone(self):
        '''Returns true if the DStoken is for a timezone offset directive, false otherwise.'''
        return self.kind == DStoken.KIND_TIMEZONE
        
        
        
    @staticmethod
    def tokenize_date(date_string):
        '''Tokenizes a date string.
        Tokens are divided on the basis of whether each character is
        a letter, a digit, or neither. (With some special handling to
        combine tokens like '+' and '0100' or '-' and '0300' into one
        timezone offset token.) For example, the string '12 34Abc?+1000'
        would be tokenized like so: '12', ' ', '34', 'Abc', '?', '+1000'.
        Returns a list of DStoken objects.
        
        :param date_string: The date string to be tokenized.
        '''
        
        current_text = ''
        current_kind = -1
        tokens = []
        
        # Iterate through characters in the date string, divide into tokens and assign token kinds.
        # Digits become number tokens, letters become word tokens, four-digit numbers preceded by '+' or '-' become timezone tokens. Everything else becomes decorator tokens.
        for char in date_string:
            asc = ord(char)
            is_digit = (asc>=48 and asc<=57)                            # 0-9
            is_alpha = (asc>=97 and asc<=122) or (asc>=65 and asc<=90)  # a-zA-Z
            is_tzoff = (asc==43 or asc==45)                             # +|-
            tokkind = DStoken.KIND_NUMBER*is_digit + DStoken.KIND_WORD*is_alpha + DStoken.KIND_TIMEZONE*is_tzoff
            if tokkind == current_kind and current_kind != DStoken.KIND_TIMEZONE:
                current_text += char
            else:
                if current_text:
                    tokens.append(DStoken(current_kind, current_text))
                current_kind = tokkind
                current_text = char
        if current_text:
            tokens.append(DStoken(current_kind, current_text))
            
        # Additional pass for handling timezone tokens
        rettokens = []
        skip = False
        tokens_count = len(tokens)
        for i in range(0,tokens_count):
            if skip:
                skip = False
            else:
                tok = tokens[i]
                if tok.is_timezone():
                    tokprev = tokens[i-1] if (i > 0) else None
                    toknext = tokens[i+1] if (i < tokens_count-1) else None
                    check_prev = (not tokprev) or not (tokprev.is_number() or tokprev.is_timezone())
                    check_next = toknext and toknext.is_number() and (len(toknext.text) == DStoken.TIMEZONE_LENGTH)
                    if check_prev and check_next:
                        tok.text += toknext.text
                        skip = True
                    else:
                        tok.kind = DStoken.KIND_DECORATOR
                rettokens.append(tok)
                    
        # All done!
        return rettokens
        
        
        
    # Convenience functions for doing useful operations on sets of token possibilities  
        
    @staticmethod
    def get_token_with_text(toklist, text):
        '''Returns the first token in a set matching the specified text.
        
        :param toklist: A list of DStoken objects.
        :param text: The text to search for.
        '''
        for tok in toklist:
            if tok.text in text:
                return tok
        return None
        
    @staticmethod
    def get_max_score(toklist):
        '''Returns the highest-scoring token in a set.
        In case of a tie, the lowest-index token will be returned.
        
        :param toklist: A list of DStoken objects.
        '''
        high = None
        for tok in toklist:
            if (not high) or tok.score > high.score:
                high = tok
        return high
        
    @staticmethod
    def get_all_max_score(toklist):
        '''Returns a list of the highest-scoring tokens in a set.'''
        high = []
        for tok in toklist:
            if (not high) or tok.score > high[0].score:
                high = [tok]
            elif tok.score == high[0].score:
                high.append(tok)
        return high




