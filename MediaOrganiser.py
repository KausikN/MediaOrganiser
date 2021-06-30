'''
Media Organiser tool
'''

# Imports
import os
import json

import MatcherLibrary

# Main Vars
VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.avi']
SUBTITLE_EXTENSIONS = ['.srt']
POSTERIMAGE_EXTENSIONS = ['.bmp', '.png', '.jpg', '.jpeg']

# Main Functions
def MediaOrganise_Movies(parent_path, save_path=None, MatchFunc=MatcherLibrary.Matcher_Direct):
    '''
    For Movies, it searches for any video files and corresponding subtitle files with similar name in parent path recursively
    '''

    # Walk through path and log movies and subtitle files and other files
    MoviePaths = []
    SubtitlePaths = []
    PosterPaths = []
    for dirPath, dirs, files in os.walk(parent_path):
        dirPath = dirPath.replace('\\', '/')
        dirSplit = dirPath.split('/')
        name = ""
        if len(dirSplit) > 0:
            name = dirSplit[-1]
        else:
            name = None
        for f in files:
            ext = os.path.splitext(f)[-1].lower()
            fileName = '.'.join(os.path.splitext(f)[:-1])
            if name is None:
                name = fileName
            # Check if Movie
            if ext in VIDEO_EXTENSIONS:
                MoviePaths.append([dirPath, name, fileName, ext])
            # Check if Subtitle
            elif ext in SUBTITLE_EXTENSIONS:
                SubtitlePaths.append([dirPath, fileName, ext])
            # Check if Poster
            elif ext in POSTERIMAGE_EXTENSIONS:
                PosterPaths.append([dirPath, fileName, ext])

    # Match Movie files
    OrganisedMoviesData = []
    # Match
    UnMatched_Subtitles = list(SubtitlePaths)
    UnMatched_Posters = list(PosterPaths)
    for m in MoviePaths:
        mainPath = m[0]
        movieName = m[1]
        vidFileName = m[2]
        vidExt = m[3]
        vidPath = '/'.join([mainPath, vidFileName + vidExt])

        match_Subtitle = None
        match_Poster = None
        # Match with same name - checks if subtitles or posters of similar name are there as vid file
        ## Subtitles
        for si in range(len(UnMatched_Subtitles)):
            s = UnMatched_Subtitles[si]
            if MatchFunc(vidFileName, s[1]):
                match_Subtitle = '/'.join([s[0], s[1] + s[2]])
                UnMatched_Subtitles.pop(si) # 2 vids CANT have same subtitle so remove if matched
                break
        ## Posters
        for pi in range(len(UnMatched_Posters)):
            p = UnMatched_Posters[pi]
            if MatchFunc(vidFileName, p[1]):
                match_Poster = '/'.join([p[0], p[1] + p[2]])
                # UnMatched_Posters.pop(pi) # 2 vids can have same poster so DONT remove
                break

        movieData = {
            "name": movieName,
            "vidPath": vidPath,
            "subtitlePath": match_Subtitle,
            "posterPath": match_Poster
        }
        OrganisedMoviesData.append(movieData)

    # Build Reorganised path tree
    # {MovieName}  
    # |_  {MovieName}.{VidExt}        (VideoFile)
    # |_  {MovieName}.{SubtitleExt}   (SubtitleFile)      - IF AVAILABLE
    # |_  {MovieName}.{PosterExt}     (PosterFile)        - IF AVAILABLE
    # |_  {MovieName}.{txt}           (DetailsFile)       - IF AVAILABLE

    # Save Data as JSON
    if save_path is not None:
        moviesData = {
            "path": parent_path,
            "data": OrganisedMoviesData
        }
        json.dump(moviesData, open(save_path, 'w'))

    return OrganisedMoviesData


def MediaOrganise_Series(parent_path, save_path=None, MatchFunc=MatcherLibrary.Matcher_Direct):
    '''
    For Series, it searches for any episode video files and corresponding subtitle files with similar name in parent path recursively
    '''

    # Walk through path and log videos and subtitle files and other files
    EpisodePaths = []
    SubtitlePaths = []
    PosterPaths = []
    for dirPath, dirs, files in os.walk(parent_path):
        dirPath = dirPath.replace('\\', '/')
        # EXPECTED PATH for episodes => {mainPath}/{SeriesName}/{Season #}/{EpisodeName}.{VidExt}
        dirSplit = dirPath.split('/')
        seriesName = ""
        seasonName = ""
        if len(dirSplit) > 1:
            seriesName = dirSplit[-2]
            seasonName = dirSplit[-1]
        elif len(dirSplit) == 1:
            seriesName = dirSplit[-1]
            seasonName = "Season 1"
        else:
            seriesName = None
            seasonName = "Season 1"
        for f in files:
            ext = os.path.splitext(f)[-1].lower()
            fileName = '.'.join(os.path.splitext(f)[:-1])
            if seriesName is None:
                seriesName = fileName
            # Check if episode
            if ext in VIDEO_EXTENSIONS:
                EpisodePaths.append([dirPath, seriesName, seasonName, fileName, ext])
            # Check if Subtitle
            elif ext in SUBTITLE_EXTENSIONS:
                SubtitlePaths.append([dirPath, seriesName, seasonName, fileName, ext])
            # Check if Poster
            elif ext in POSTERIMAGE_EXTENSIONS:
                PosterPaths.append([dirPath, seriesName, seasonName, fileName, ext])

    # Match Series files
    OrganisedEpisodesData = []
    # Match
    UnMatched_Subtitles = list(SubtitlePaths)
    UnMatched_Posters = list(PosterPaths)
    for e in EpisodePaths:
        mainPath = e[0]
        seriesName = e[1]
        seasonName = e[2]
        vidFileName = e[3]
        vidExt = e[4]
        vidPath = '/'.join([mainPath, vidFileName + vidExt])

        match_Subtitle = None
        match_Poster = None
        # Match with same series and season name and similar name - checks if subtitles or posters of same series and season name are there as vid file
        ## Subtitles - series, season and fileName need to match for subtitles
        for si in range(len(UnMatched_Subtitles)):
            s = UnMatched_Subtitles[si]

            if MatcherLibrary.Matcher_Direct(seriesName, s[1]) and MatcherLibrary.Matcher_Direct(seasonName, s[2]) and MatchFunc(vidFileName, s[3]):
                match_Subtitle = '/'.join([s[0], s[3] + s[4]])
                UnMatched_Subtitles.pop(si) # 2 vids CANT have same subtitle so remove if matched
                break
        ## Posters - either series and season match or fileName match needed for poster
        for pi in range(len(UnMatched_Posters)):
            p = UnMatched_Posters[pi]
            if (MatcherLibrary.Matcher_Direct(seriesName, p[1]) and MatcherLibrary.Matcher_Direct(seasonName, p[2])) or MatchFunc(vidFileName, p[3]):
                match_Poster = '/'.join([p[0], p[3] + p[4]])
                # UnMatched_Posters.pop(pi) # 2 vids can have same poster so DONT remove
                break

        episodeData = {
            "name": vidFileName,
            "seriesName": seriesName,
            "seasonName": seasonName,
            "vidPath": vidPath,
            "subtitlePath": match_Subtitle,
            "posterPath": match_Poster
        }
        OrganisedEpisodesData.append(episodeData)

    # Group Episodes into Series
    OrganisedSeriesData = []
    OrganisedSeriesData_Dict = {}
    for ep in OrganisedEpisodesData:
        # Add series to list if not there
        if ep['seriesName'] not in OrganisedSeriesData_Dict.keys():
            OrganisedSeriesData_Dict[ep['seriesName']] = {}
        # Add season name to list if not there
        if ep['seasonName'] not in OrganisedSeriesData_Dict[ep['seriesName']].keys():
            OrganisedSeriesData_Dict[ep['seriesName']][ep['seasonName']] = []
        # Add Episode
        OrganisedSeriesData_Dict[ep['seriesName']][ep['seasonName']].append(ep)
    for series in OrganisedSeriesData_Dict.keys():
        seasonsData = []
        for season in OrganisedSeriesData_Dict[series].keys():
            seasonData = {
                "name": season,
                "episodes": OrganisedSeriesData_Dict[series][season]
            }
            seasonsData.append(seasonData)
        seriesData = {
            "name": series,
            "data": seasonsData
        }
        OrganisedSeriesData.append(seriesData)

    # Build Reorganised path tree
    # {SeriesName}
    # |_  {Season 1}  
    # |   |_  {S1E1}.{VidExt}        (VideoFile)
    # |   |_  {S1E1}.{SubtitleExt}   (SubtitleFile)      - IF AVAILABLE
    # |   |_  {S1E1}.{PosterExt}     (PosterFile)        - IF AVAILABLE
    # |   |_  {S1E1}.{txt}           (DetailsFile)       - IF AVAILABLE
    # |_  {Season 2}
    #     |_  {S2E1}.{VidExt}        (VideoFile)
    #     |_  {S2E1}.{SubtitleExt}   (SubtitleFile)      - IF AVAILABLE
    #     |_  {S2E1}.{PosterExt}     (PosterFile)        - IF AVAILABLE
    #     |_  {S2E1}.{txt}           (DetailsFile)       - IF AVAILABLE

    # Save Data as JSON
    if save_path is not None:
        seriesData = {
            "path": parent_path,
            "data": OrganisedSeriesData
        }
        json.dump(seriesData, open(save_path, 'w'))

    return OrganisedSeriesData

# Driver Code
# # Params
# parentPath = 'Movies/'
# savePath = 'OrganisedData/MoviesData.json'

# MatchFunc = MatcherLibrary.Matcher_Direct
# # Params

# # RunCode
# # Data = MediaOrganise_Movies(parentPath, savePath, MatchFunc)
# Data = MediaOrganise_Series(parentPath, savePath, MatchFunc)
# for d in Data:
#     print(d)
#     print()