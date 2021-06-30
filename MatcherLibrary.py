'''
Matcher Library Functions
'''

# Imports
import os
from difflib import SequenceMatcher


# Util Functions


# Matcher Main Functions
def Matcher_Direct(name1, name2):
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    return (name1 == name2)

def Matcher_PartOf(name1, name2):
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    return (name1 in name2) or (name2 in name1)

def Matcher_SoftPartOf(name1, name2, threshold=0.9):
    match = SequenceMatcher(None, name1, name2).find_longest_match(0, len(name1), 0, len(name2))
    return match.size >= (min(len(name1), len(name2)) * threshold)

# Driver Code
