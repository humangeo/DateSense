'''Contains DSrule classes for DateSense package.'''



from .DStoken import DStoken



# Rules are where the real fun happens with date format detection. Please
# feel free to implement your own! The only strictly necessary component
# of a DSrule class is that it has an apply(self, options) method
# where options is a DSoptions object.



class DSDelimiterRule(object):
    '''Delimiter rules mean that if some tokens are separated by a
    delimiter, assumptions can be made for what those tokens represent.
    DSDelimiterRule objects that are elements in the format_rules
    attribute of DSoptions objects are evaluated during parsing.
    '''
    
    def __init__(self, directives, delimiters, posscore=0, negscore=0):
        '''Constructs a DSDelimiterRule object.
        Positive reinforcement: The scores of specified possibilities that
        are adjacent to one or more tokens where any of the specified
        delimiters are a possibility are affected.
        Negative reinforcement: The scores of specified possibilities that
        are not adjacent any tokens where any of the specified delimiters
        are a possibility are affected.
        Returns the DSDelimiterRule object.
        
        :param directives: A directive or set of directives that the rule
            applies to, like ('%H','%I','%M','%S').
        :param delimiters: A delimiter or set of delimiters that the rule 
            applies to, like ':'.
        :param posscore: (optional) Increment the score of possibilities
            matching the "Positive reinforcement" condition by this much.
            Defaults to 0.
        :param negscore: (optional) Increment the score of possibilities
            matching the "Negative reinforcement" condition by this much.
            Defaults to 0.
        '''
        self.posscore = posscore
        self.negscore = negscore
        self.directives = directives
        self.delimiters = delimiters
        
    # Positive reinforcement: Specified possibilities that are adjacent to one of the specified delimiters
    # Negative reinforcement: Specified possibilities that are not adjacent to one of the specified delimiters
    def apply(self, options):
        '''Applies the rule to the provided DSoptions object by affecting token possibility scores.'''
        adjacent=[]
        # For each delimiter specified:
        for delimiter in self.delimiters:
            toklist_count = len(options.allowed)
            # Determine which date tokens are adjacent to any one that has the delimiter text as a possibility
            for i in range(0,toklist_count):
                toklist = options.allowed[i]
                delimtok=DStoken.get_token_with_text(toklist, delimiter)
                if delimtok:
                    if i > 0 and (options.allowed[i-1] not in adjacent):
                        adjacent.append(options.allowed[i-1])
                    if i < toklist_count-1 and (options.allowed[i+1] not in adjacent):
                        adjacent.append(options.allowed[i+1])
        # Affect scores of possibilities specified
        for toklist in options.allowed:
            # Positive reinforcement
            if toklist in adjacent:
                if self.posscore:
                    for tok in toklist:
                        if tok.text in self.directives:
                            tok.score += self.posscore
            # Negative reinforcement
            elif self.negscore:
                for tok in toklist:
                    if tok.text in self.directives:
                        tok.score += self.negscore
    
    

class DSLikelyRangeRule(object):
    '''Likely range rules mean that a numeric directive is most
    likely to be present for only a subset of its strictly possible
    values.
    DSLikelyRangeRule objects that are elements in the format_rules
    attribute of DSoptions objects are evaluated during parsing.
    '''
    
    def __init__(self, directives, likelyrange, posscore=0, negscore=0):
        '''Constructs a DSLikelyRangeRule object.
        Positive reinforcement: The scores of specified directives where
        the encountered values are all within the likely range are
        affected.
        Negative reinforcement: The scores of specified directives where
        any of the encountered values lie outside the likely range are
        affected.
        Returns the DSLikelyRangeRule object.
        
        :param directives: A directive or set of directives that the rule
            applies to, like '%S'.
        :param likelyrange: Min and max range that any values for the
            specified directives are likely to be within. Should be indexed -
            recommended you use a tuple, like (0, 59). The value at index 0
            will be considered the minimum and index 1 the maximum. The
            range is inclusive.
        :param posscore: (optional) Increment the score of possibilities
            matching the "Positive reinforcement" condition by this much.
            Defaults to 0.
        :param negscore: (optional) Increment the score of possibilities
            matching the "Negative reinforcement" condition by this much.
            Defaults to 0.
        '''
        self.posscore = posscore
        self.negscore = negscore
        self.directives = directives
        self.likelyrange = likelyrange
        
    # Positive reinforcement: Directives inside the likely range
    # Negative reinforcement: Directives outside the likely range
    def apply(self, options):
        '''Applies the rule to the provided DSoptions object by affecting token possibility scores.'''
        # Iterate through the token possibilities
        toklist_count = len(options.allowed)
        for i in range(0,toklist_count):
            toklist = options.allowed[i]
            for tok in toklist:
                # If the possibility is a number and matches the argument, check whether the encoutered data was all inside the likely range.
                if tok.kind == DStoken.KIND_NUMBER and tok.text in self.directives:
                    # Positive reinforcement
                    if options.numranges[i][0] >= self.likelyrange[0] and options.numranges[i][1] <= self.likelyrange[1]:
                        tok.score += self.posscore
                    # Negative reinforcement
                    else:
                        tok.score += self.negscore
    
    

class DSPatternRule(object):
    '''Pattern rules inform the parser that tokens commonly show
    up in the sequence provided. ('%m','/','%d','/',('%y','%Y'))
    would be one example of such a sequence.
    DSPatternRule objects that are elements in the format_rules
    attribute of DSoptions objects are evaluated during parsing.
    '''

    def __init__(self, sequence, maxdistance=1, minmatchscore=0, posscore=0, negscore=0):
        '''Constructs a DSPatternRule object.
        Positive reinforcement: The scores of possibilities comprising
        a complete sequence as specified are affected. Wildcard tokens
        between specified tokens in the sequence do not have their scores
        affected.
        Negative reinforcement: The scores of directive possibilities
        found in the sequence that were not found to be part of any
        instance of the sequence are affected. Scores of non-directive
        token possibilities are not affected.
        Returns the DSPatternRule object.
        
        :param sequence: A set of token possibilities, like
            ('%H',':','%M',':','%S').
        :param maxdistance: (optional) How many wildcard tokens are allowed
            to be in between those defined in the sequence. For example,
            the sequence ('%H',':','%M') with a maxdistance of 1 would
            match %H:%M but not %H.%M. The sequence ('%H','%M') with a
            maxdistance of 2 would match both. Defaults to 1.
        :param minmatchscore: (optional) The minimum score a directive
            may have to be considered a potential member of the sequence.
            (Does not apply to non-directive possibilities - those will
            count at any score.) Defaults to 0.
        :param posscore: (optional) Increment the score of possibilities
            matching the "Positive reinforcement" condition by this much.
            Defaults to 0.
        :param negscore: (optional) Increment the score of possibilities
            matching the "Negative reinforcement" condition by this much.
            Defaults to 0.
        '''
        self.posscore = posscore
        self.negscore = negscore
        self.sequence = sequence
        self.maxdistance = maxdistance
        self.minmatchscore = minmatchscore
        
    # Positive reinforcement: Possibilities comprising a complete pattern
    # Negative reinforcement: Directive possibilities in the pattern that were not found to be part of an instance of the pattern
    def apply(self, options):
        '''Applies the rule to the provided DSoptions object by affecting token possibility scores.'''
        # Which date token in the pattern are we on?
        onarg = 0
        # How many tokens have we looked over since the last one that's part of the pattern?
        counter = 0
        # What are the token possibilities we've run into so far that fit the pattern?
        ordered_toks = []
        ordered_toks_current = []
        # Iterate through the lists of token possibilities
        for toklist in options.allowed:
            # Check if we've passed over the allowed number of in-between tokens yet, if so then reset the pattern search
            if ordered_toks_current:
                counter += 1
                if counter > self.maxdistance:
                    onarg = 0
                    counter = 0
                    ordered_toks_current = []
            # Does the token here match the pattern?
            # (Only consider directives with scores greater than or equal to self.minmatchscore, and decorators of any score)
            foundtok = 0
            for tok in toklist:
                if (tok.score >= self.minmatchscore or tok.is_decorator()) and tok.text in self.sequence[onarg]:
                    ordered_toks_current.append(tok)
                    foundtok += 1
            # One or more possibilities here match the pattern! On to the next expected possibility in the pattern sequence.
            if foundtok:
                onarg += 1
                counter = 0
                # Did we hit the end of the pattern sequence? If so, let's reset so we can see if there's any more occurences.
                if onarg == len(self.sequence):
                    onarg = 0
                    ordered_toks.extend(ordered_toks_current)
        # Positive reinforcement
        if self.posscore:
            for tok in ordered_toks:
                tok.score += self.posscore
        # Negative reinforcement
        if self.negscore:
            # Iterate through all possibilities for all tokens
            for toklist in options.allowed:
                for tok in toklist:
                    # Is the possibility a directive?
                    if not tok.is_decorator():
                        # Does the possibility exist anywhere in the pattern?
                        for matchtext in self.sequence:
                            if tok.text in matchtext:
                                # Was it not a part of any found instances of the pattern? If so, whack the score.
                                if tok not in ordered_toks:
                                    tok.score += self.negscore
        


class DSMutExclusionRule(object):
    '''Mutual exclusion rules indicate that a group of directives
    probably aren't going to show up in the same date string.
    ('%H','%I') would be an example of mutually-exclusive directives.
    DSMutExclusionRule objects that are elements in the format_rules
    attribute of DSoptions objects are evaluated during parsing.
    '''
    
    def __init__(self, directives, posscore=0, negscore=0):
        '''Constructs a DSMutExclusionRule object.
        Positive reinforcement: The highest-scoring instance of any of the
        specified possibilities is found and the scores for that same
        possibility at any token where it's present is affected.
        Negative reinforcement: The highest-scoring instance of any of the
        specified possibilities is found and the scores for all the other
        specified possibilities at any token where they're present are
        affected.
        Returns the DSMutExclusionRule object.
        
        :param directives: A set of directives that the rule applies to,
            like ('%H','%I').
        :param posscore: (optional) Increment the score of possibilities
            matching the "Positive reinforcement" condition by this much.
            Defaults to 0.
        :param negscore: (optional) Increment the score of possibilities
            matching the "Negative reinforcement" condition by this much.
            Defaults to 0.
        '''
        self.posscore = posscore
        self.negscore = negscore
        self.directives = directives
        
    # Positive reinforcement: The highest-scoring instance of any of the specified possibilities specified is found and the scores of that possibility everywhere will be affected
    # Negative reinforcement: The highest-scoring instance of any of the specified possibilities specified is found and the scores of all the other possibilities will be affected
    def apply(self, options):
        '''Applies the rule to the provided DSoptions object by affecting token possibility scores.'''
        # Find the highest-scoring instance of each token possibility specified
        matchedtoks = []
        for toklist in options.allowed:
            for tok in toklist:
                for i in range(0,len(self.directives)):
                    matchedtoks.append(None)
                    matchtext = self.directives[i]
                    if tok.text in matchtext:
                        if (not matchedtoks[i]) or tok.score > matchedtoks[i].score:
                            matchedtoks[i] = tok
        # Determine which of the possibilities had the highest score
        highest_tok = None
        highest_index = 0
        for i in range(0,len(matchedtoks)):
            tok = matchedtoks[i]
            if tok and ((not highest_tok) or tok.score > highest_tok.score):
                highest_tok = tok
                highest_index = i
        # Affect scores (Ties go to the lowest-index argument.)
        if highest_tok:
            for toklist in options.allowed:
                for tok in toklist:
                    for i in range(0,len(self.directives)):
                        matchtext = self.directives[i]
                        if tok.text in matchtext:
                            # Positive reinforcement
                            if i == highest_index:
                                tok.score += self.posscore
                            # Negative reinforcement
                            else:
                                tok.score += self.negscore

            
    




