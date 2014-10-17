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
