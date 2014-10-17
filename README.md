# DateSense

## Introduction

DateSense is for the detecting the format of date strings and it returns a format string that can be passed to strptime or strftime. It accepts any number of dates as input, which it will assume all share the same format. It's easy to customize the way the parser behaves by defining your own rules which tell it what to expect.

## Usage

To parse one or more date strings using the default settings, you need only two lines. Here's an example that would output the string "%d %b %Y":

    from DateSense.DSoptions import DSoptions
    print DSoptions.detect_format( ["15 Dec 2014", "9 Jan 2015"] )
    
    > %d %b %Y

## Customization

Various rule objects tell the parser what assumptions to make regarding how dates are formatted. Here's an example - this rule tells the parser how to recognize parts of date strings that look like they fit the pattern HH:MM:SS.

    rule_pattern_hms = DSPatternRule(3, 0, (('%H','%I'),':','%M',':','%S'), 1)
    
Custom cab would be useful if you have a nonstandard date format in your data that you needed to anticipate, and the parser didn't recognize using the default rules. You could add that format as a pattern rule to let the parser know what to expect when it encountered directives in that sequence.
    
There are a few other kinds of rules, thoroughly documented in DSrule.py. The default rules are all defined as attributes of the DSoptions class so that you can pick and choose as you see fit if you don't want to write your own. If you were to create a collection of rules you wanted the parser to use instead of the default, you could use this syntax:

    DSoptions.detect_format( dates, rules )

Enjoy!