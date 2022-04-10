'''
Matcher Library Functions
'''

# Imports
import os
import re
from difflib import SequenceMatcher

# Util Functions
def ParseEpisodeDetails(name, countDigits=-1):
    # Get the season number and episode number from episode name
    # Eg. FriendsS01E02 => {'season': 1, 'episode': 2}
    name = name.lower().strip()
    regexPattern = ""
    if countDigits == -1:
        regexPattern = "s" + "[0-9]+" + "e" + "[0-9]+"
    else:
        regexPattern = "s" + ("[0-9]" * countDigits) + "e" + ("[0-9]" * countDigits)
    SEData = re.findall(regexPattern, name)
    if SEData == []: return None, None
    SEData = SEData[0][1:] # Skip the "s"
    SEDataSplit = SEData.split("e")
    season = int(SEDataSplit[0])
    episode = int(SEDataSplit[1])
    return season, episode

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

def Matcher_WordsPartOf(name1, name2, flipMax=True):
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    if len(name1) > len(name2) and flipMax:
        name1, name2 = name2, name1
    name1 = name1.replace(".", " ").replace("_", " ")
    words = name1.split(" ")
    for w in words:
        if not (w in name2):
            return False
    return True

def Matcher_EpisodeMatch(name1, name2):
    name1 = name1.lower().strip()
    name2 = name2.lower().strip()
    s1, e1 = ParseEpisodeDetails(name1)
    s2, e2 = ParseEpisodeDetails(name2)
    if s1 == s2 and e1 == e2:
        return True
    return False

# Driver Code