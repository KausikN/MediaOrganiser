'''
Media Organiser tool
'''

# Imports
import os
import json
import cv2

from MatcherLibrary import *

# Main Vars
VIDEO_EXTENSIONS = [".mkv", ".mp4", ".avi"]
SUBTITLE_EXTENSIONS = [".srt"]
POSTERIMAGE_EXTENSIONS = [".bmp", ".png", ".jpg", ".jpeg"]

# Main Functions
def MediaOrganise_Movies(parent_path, save_path=None):
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
        # Check for subtitle files
        for si in range(len(UnMatched_Subtitles)):
            s = UnMatched_Subtitles[si]
            if Matcher_WordsPartOf(vidFileName, s[1], False):
                match_Subtitle = '/'.join([s[0], s[1] + s[2]])
                UnMatched_Subtitles.pop(si) # 2 vids CANT have same subtitle so remove if matched
                break
        ## Posters
        for pi in range(len(UnMatched_Posters)):
            p = UnMatched_Posters[pi]
            if Matcher_WordsPartOf(vidFileName, p[1], False):
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


def MediaOrganise_Series(parent_path, save_path=None):
    # For Series, it searches for any episode video files and corresponding subtitle files with similar name in parent path recursively

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
            seasonName = seriesName
        else:
            seriesName = None
            seasonName = seriesName
        for f in files:
            ext = os.path.splitext(f)[-1].lower()
            fileName = '.'.join(os.path.splitext(f)[:-1])
            if seriesName is None:
                seriesName = fileName
                seasonName = seriesName
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
        ## Subtitles - match the season and episode numbers or name words with vid file name
        for si in range(len(UnMatched_Subtitles)):
            s = UnMatched_Subtitles[si]
            if Matcher_Direct(seriesName, s[1]) and Matcher_Direct(seasonName, s[2]):
                if Matcher_EpisodeMatch(vidFileName, s[3]) or Matcher_WordsPartOf(vidFileName, s[3], False):
                    match_Subtitle = '/'.join([s[0], s[3] + s[4]])
                    UnMatched_Subtitles.pop(si) # 2 vids CANT have same subtitle so remove if matched
                    break
        ## Posters - Check if direct match available
        for pi in range(len(UnMatched_Posters)):
            p = UnMatched_Posters[pi]
            if Matcher_Direct(seriesName, p[1]) and Matcher_Direct(seasonName, p[2]):
                if Matcher_EpisodeMatch(vidFileName, p[3]) or Matcher_WordsPartOf(vidFileName, p[3], False):
                    match_Poster = '/'.join([p[0], p[3] + p[4]])
                    UnMatched_Posters.pop(pi)
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
        backupSeasonPoster = None
        backupEpisodePoster = None
        # Check for series posters
        seriesPosterPath = None
        for pi in range(len(UnMatched_Posters)):
            p = UnMatched_Posters[pi]
            if Matcher_Direct(series, p[2]) or Matcher_WordsPartOf(p[3], series, False):
                seriesPosterPath = '/'.join([p[0], p[3] + p[4]])
                break

        for season in OrganisedSeriesData_Dict[series].keys():
            # Check for season posters
            posterPath = None
            for pi in range(len(UnMatched_Posters)):
                p = UnMatched_Posters[pi]
                if Matcher_Direct(series, p[1]) and Matcher_Direct(season, p[2]) or Matcher_WordsPartOf(series + " " + season, p[3]):
                    posterPath = '/'.join([p[0], p[3] + p[4]])
                    if backupSeasonPoster is None: backupSeasonPoster = posterPath
                    break
            if posterPath is None:
                # Check for any episode posters as season poster not available
                for ep in OrganisedSeriesData_Dict[series][season]:
                    if ep["posterPath"] is not None:
                        posterPath = ep["posterPath"]
                        if backupEpisodePoster is None: backupEpisodePoster = posterPath
                        break
            # Add Data
            seasonData = {
                "name": season,
                "posterPath": posterPath,
                "episodes": OrganisedSeriesData_Dict[series][season]
            }
            seasonsData.append(seasonData)

        if seriesPosterPath is None:
            seriesPosterPath = backupSeasonPoster if backupSeasonPoster is not None else backupEpisodePoster

        seriesData = {
            "name": series,
            "posterPath": seriesPosterPath,
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

def GenerateMoviePoster(vid_path, savePath=None, framePos=0.5):
    # Fetch Video File Details
    vid = cv2.VideoCapture(vid_path)
    FRAMES_COUNT = vid.get(cv2.CAP_PROP_FRAME_COUNT)
    FPS = int(vid.get(cv2.CAP_PROP_FPS))
    DURATION = (FRAMES_COUNT / FPS)*1000
    CHOICE_TIME = DURATION*framePos

    # Set to time and retrieve frame
    vid.set(cv2.CAP_PROP_POS_MSEC, CHOICE_TIME)
    success, Poster = vid.read()
    vid.release()

    # Save
    pathSplit = os.path.split(vid_path)
    mainPath = pathSplit[0]
    vidName = os.path.splitext(pathSplit[-1])[0]
    savePath = (mainPath + "/" + vidName + ".jpg") if savePath is None else savePath
    cv2.imwrite(savePath, Poster)

# Driver Code