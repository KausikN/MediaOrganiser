"""
Stream lit GUI for hosting MediaOrganiser
"""

# Imports
import streamlit as st
import os
import cv2
import json

import MediaOrganiser

# Main Vars
config = json.load(open('./StreamLitGUI/UIConfig.json', 'r'))

# Main Functions
def main():
    # Create Sidebar
    selected_box = st.sidebar.selectbox(
    'Choose one of the following',
        tuple(
            [config['PROJECT_NAME']] + 
            config['PROJECT_MODES']
        )
    )

    # Load Cache
    LoadCacheData()
    
    if selected_box == config['PROJECT_NAME']:
        HomePage()
    else:
        correspondingFuncName = selected_box.replace(' ', '_').lower()
        if correspondingFuncName in globals().keys():
            globals()[correspondingFuncName]()
 

def HomePage():
    st.title(config['PROJECT_NAME'])
    st.markdown('Github Repo: ' + "[" + config['PROJECT_LINK'] + "](" + config['PROJECT_LINK'] + ")")
    st.markdown(config['PROJECT_DESC'])

    # st.write(open(config['PROJECT_README'], 'r').read())

#############################################################################################################################
# Repo Based Vars
SAVEPATH_MOVIEDATA = 'OrganisedData/Movies/'
SAVEPATH_SERIESDATA = 'OrganisedData/Series/'
SAVEPATH_MOVIEPOSTERS = 'StreamLitGUI/DefaultData/MoviePosters/'
SAVEPATH_SERIESPOSTERS = 'StreamLitGUI/DefaultData/SeriesPosters/'
SAVEPATH_MOVIEPREVIEWS = 'StreamLitGUI/DefaultData/MoviePreviews/'
SAVEPATH_SERIESPREVIEWS = 'StreamLitGUI/DefaultData/SeriesPreviews/'
DEFAULT_IMAGEEXT = '.jpg'

DEFAULT_PATH_POSTER = 'StreamLitGUI/DefaultData/PosterNotFound.png'
DEFAULT_PATH_LOADING = 'StreamLitGUI/DefaultData/LoadingGIF.gif'

CACHEPATH_MOVIEDIRS = "StreamLitGUI/CacheData/MovieDirs.json"
CACHEPATH_SERIESDIRS = "StreamLitGUI/CacheData/SeriesDirs.json"
CACHEPATH_SETTINGS = "StreamLitGUI/CacheData/Settings.json"

# Main Vars
DATA_MOVIES = []
DATA_SERIES = []

GEN_POSTERS = False

# Util Vars
CACHE_MOVIEDIRS = []
CACHE_SERIESDIRS = []
CACHE_SETTINGS = {}

# Util Functions
def FixPath(path):
    return path
    pathSplit = path.split("/")
    fixedPathSplit = []
    for p in pathSplit:
        if " " in p:
            fixedPathSplit.append('"' + p + '"')
        else:
            fixedPathSplit.append(p)
    return "/".join(fixedPathSplit)

def Data_Path2SaveName(path):
    print(path)
    print(path.replace(" ", "_").strip("/").replace("/", ";").replace("\\", ";"))
    print()
    return path.replace(" ", "_").strip("/").replace("/", ";").replace("\\", ";")

def LoadCacheData():
    global CACHE_MOVIEDIRS
    global CACHE_SERIESDIRS
    global CACHE_SETTINGS
    CACHE_MOVIEDIRS = json.load(open(CACHEPATH_MOVIEDIRS, 'r'))["dirs"]
    CACHE_SERIESDIRS = json.load(open(CACHEPATH_SERIESDIRS, 'r'))["dirs"]
    CACHE_SETTINGS = json.load(open(CACHEPATH_SETTINGS, 'r'))

def SaveCacheData():
    global CACHE_MOVIEDIRS
    global CACHE_SERIESDIRS
    global CACHE_SETTINGS
    json.dump({"dirs": CACHE_MOVIEDIRS}, open(CACHEPATH_MOVIEDIRS, 'w'))
    json.dump({"dirs": CACHE_SERIESDIRS}, open(CACHEPATH_SERIESDIRS, 'w'))
    json.dump(CACHE_SETTINGS, open(CACHEPATH_SETTINGS, 'w'))

def ClearPosterPreviews():
    # Deletes all poster images and preview images for movies and series
    for f in os.listdir(SAVEPATH_MOVIEPOSTERS):
        os.remove(os.path.join(SAVEPATH_MOVIEPOSTERS, f))
    for f in os.listdir(SAVEPATH_SERIESPOSTERS):
        os.remove(os.path.join(SAVEPATH_SERIESPOSTERS, f))
    for f in os.listdir(SAVEPATH_MOVIEPREVIEWS):
        os.remove(os.path.join(SAVEPATH_MOVIEPREVIEWS, f))
    for f in os.listdir(SAVEPATH_SERIESPREVIEWS):
        os.remove(os.path.join(SAVEPATH_SERIESPREVIEWS, f))

# Main Functions
def GenerateOrganisedData_Movies(paths):
    # Delete Prexisting Data
    for f in os.listdir(SAVEPATH_MOVIEDATA):
        os.remove(os.path.join(SAVEPATH_MOVIEDATA, f))
    # Generate New Data
    for i in range(len(paths)):
        path = paths[i]
        if os.path.exists(path):
            savePath = SAVEPATH_MOVIEDATA + "MoviesData_" + str(i) + ".json"
            MediaOrganiser.MediaOrganise_Movies(path, savePath)

def GenerateOrganisedData_Series(paths):
    # Delete Prexisting Data
    for f in os.listdir(SAVEPATH_SERIESDATA):
        os.remove(os.path.join(SAVEPATH_SERIESDATA, f))
    # Generate New Data
    for i in range(len(paths)):
        path = paths[i]
        if os.path.exists(path):
            savePath = SAVEPATH_SERIESDATA + "SeriesData_" + str(i) + ".json"
            MediaOrganiser.MediaOrganise_Series(path, savePath)

def LoadOrganisedData_Movies():
    global DATA_MOVIES
    # Load all files in savepath
    DATA_MOVIES = []
    for f in os.listdir(SAVEPATH_MOVIEDATA):
        DATA_MOVIES.extend(json.load(open(os.path.join(SAVEPATH_MOVIEDATA, f), 'r'))["data"])

def LoadOrganisedData_Series():
    global DATA_SERIES
    # Load all files in savepath
    DATA_SERIES = []
    for f in os.listdir(SAVEPATH_SERIESDATA):
        DATA_SERIES.extend(json.load(open(os.path.join(SAVEPATH_SERIESDATA, f), 'r'))["data"])

def GetNames(data, includes={"year": False}):
    names = []
    for d in data:
        name = d["name"]
        if includes["year"]:
            name = name + " " + d["year"]
        names.append(name)
    return names

# UI Functions
def UI_SpecifyDirPaths(dirs):
    dirsText = "\n".join(dirs)
    USERINPUT_dirsText = st.text_area("Specify Dirs in separate lines", dirsText, height=10)
    USERINPUT_dirs = USERINPUT_dirsText.split("\n")
    return USERINPUT_dirs

def UI_VideoPreview(data, saveDir, title="Movie", col=st):
    PreviewWindow = col.empty()
    USERINPUT_PreviewPart = col.slider("", 0.0, 1.0, 0.0, 0.01, key=data["vidPath"])
    PreviewWindow.image(DEFAULT_PATH_LOADING, title + " Preview", use_column_width=True)
    previewPath = saveDir + data["name"] + DEFAULT_IMAGEEXT
    MediaOrganiser.GenerateMoviePoster(data["vidPath"], previewPath, USERINPUT_PreviewPart)
    Preview = cv2.cvtColor(cv2.imread(previewPath), cv2.COLOR_BGR2RGB)
    PreviewWindow.image(Preview, title + " Preview", use_column_width=True)


# Repo Based Functions
def view_movies():
    # Title
    st.header("View Movies")

    # Load Inputs
    LoadOrganisedData_Movies()
    MovieNames = GetNames(DATA_MOVIES)
    USERINPUT_MovieChoice = st.selectbox("Select Movie", ["Select Movie"] + MovieNames)
    if USERINPUT_MovieChoice == "Select Movie": return

    # Process Inputs
    USERINPUT_MovieChoiceIndex = MovieNames.index(USERINPUT_MovieChoice)
    MovieChoiceData = DATA_MOVIES[USERINPUT_MovieChoiceIndex]

    # Display Outputs
    st.markdown("## Movie Details")
    posterPath = None
    if (MovieChoiceData["posterPath"] is not None) and (os.path.exists(MovieChoiceData["posterPath"])):
        posterPath = FixPath(MovieChoiceData["posterPath"])
    else:
        if CACHE_SETTINGS["GEN_POSTERS"]:
            posterPath = SAVEPATH_MOVIEPOSTERS + MovieChoiceData["name"] + DEFAULT_IMAGEEXT
            MediaOrganiser.GenerateMoviePoster(MovieChoiceData["vidPath"], posterPath, 0.25)
        else:
            posterPath = FixPath(DEFAULT_PATH_POSTER)
    Poster = cv2.cvtColor(cv2.imread(posterPath), cv2.COLOR_BGR2RGB)
    st.image(Poster, "Movie Poster", use_column_width=True)
    st.markdown(MovieChoiceData["name"])
    st.markdown("🎥 " + MovieChoiceData["vidPath"])
    if MovieChoiceData["subtitlePath"] is not None:
        st.markdown("**CC** " + "Subtitles available")

    st.markdown("## Movie Preview")
    UI_VideoPreview(MovieChoiceData, SAVEPATH_MOVIEPREVIEWS, "Movie")

    # Clear all images
    if CACHE_SETTINGS["CLEAR_DATA_AFTER_RUN"]:
        ClearPosterPreviews()

def view_series():
    # Title
    st.header("View Series")

    # Load Inputs
    LoadOrganisedData_Series()
    SeriesNames = GetNames(DATA_SERIES)
    USERINPUT_SeriesChoice = st.selectbox("Select Series", ["Select Series"] + SeriesNames)
    if USERINPUT_SeriesChoice == "Select Series": return

    # Process Inputs
    USERINPUT_SeriesChoiceIndex = SeriesNames.index(USERINPUT_SeriesChoice)
    SeriesChoiceData = DATA_SERIES[USERINPUT_SeriesChoiceIndex]
    SeriesPoster = SeriesChoiceData["posterPath"]

    # Display Outputs
    SeasonsNames = GetNames(SeriesChoiceData["data"])
    USERINPUT_SeasonsChoice = st.selectbox("Select Season", ["Select Season"] + SeasonsNames)
    if USERINPUT_SeasonsChoice == "Select Season": return

    USERINPUT_SeasonsChoiceIndex = SeasonsNames.index(USERINPUT_SeasonsChoice)
    SeasonsChoiceData = SeriesChoiceData["data"][USERINPUT_SeasonsChoiceIndex]
    SeasonPoster = SeasonsChoiceData["posterPath"]

    st.markdown("## Series Details")
    mainPosterPath = SeasonPoster if SeasonPoster is not None else SeriesPoster
    mainPosterPath = mainPosterPath if mainPosterPath is not None else DEFAULT_PATH_POSTER
    mainPoster = cv2.cvtColor(cv2.imread(mainPosterPath), cv2.COLOR_BGR2RGB)
    st.image(mainPoster, "Series", use_column_width=True)
    st.markdown("## " + SeriesChoiceData["name"])
    st.markdown("## " + SeasonsChoiceData["name"])

    st.markdown("## Episodes")
    st.markdown("<hr>", unsafe_allow_html=True)
    for ep in SeasonsChoiceData["episodes"]:
        col1, col2 = st.beta_columns([1, 2])

        UI_VideoPreview(ep, SAVEPATH_SERIESPREVIEWS, "Episode", col=col1)

        col2.markdown("🎥 " + ep["name"])
        if ep["subtitlePath"] is not None:
            col2.markdown("**CC** " + "Subtitles available")

        st.markdown("<hr>", unsafe_allow_html=True)

    # Clear all images
    if CACHE_SETTINGS["CLEAR_DATA_AFTER_RUN"]:
        ClearPosterPreviews()

def settings():
    global CACHE_MOVIEDIRS
    global CACHE_SERIESDIRS

    # Title
    st.header("Settings")

    # Load Inputs
    LoadOrganisedData_Movies()
    LoadOrganisedData_Series()

    st.markdown("## Movie Dirs")
    CACHE_MOVIEDIRS = UI_SpecifyDirPaths(CACHE_MOVIEDIRS)
    col1, col2 = st.beta_columns([1, 2])
    col1.markdown("Movies Loaded: ")
    MoviesCountField = col2.empty()
    MoviesCountField.markdown("" + str(len(DATA_MOVIES)))

    st.markdown("## Series Dirs")
    CACHE_SERIESDIRS = UI_SpecifyDirPaths(CACHE_SERIESDIRS)
    col1, col2 = st.beta_columns([1, 2])
    col1.markdown("Series Loaded: ")
    SeriesCountField = col2.empty()
    SeriesCountField.markdown("" + str(len(DATA_SERIES)))

    st.markdown("## Other Settings")
    CACHE_SETTINGS["GEN_POSTERS"] = st.checkbox("Generate Posters if not available", CACHE_SETTINGS["GEN_POSTERS"])
    CACHE_SETTINGS["CLEAR_DATA_AFTER_RUN"] = st.checkbox("Delete Generated Images After Runs", CACHE_SETTINGS["CLEAR_DATA_AFTER_RUN"])

    l, m, r = st.beta_columns([5, 1, 5])
    if m.button("Save"):
        SaveCacheData()

        # Process Inputs
        GenerateOrganisedData_Movies(CACHE_MOVIEDIRS)
        GenerateOrganisedData_Series(CACHE_SERIESDIRS)

        LoadOrganisedData_Movies()
        LoadOrganisedData_Series()

        # Display Outputs
        MoviesCountField.markdown("" + str(len(DATA_MOVIES)))
        SeriesCountField.markdown("" + str(len(DATA_SERIES)))

        m.markdown("Saved!")
        
    
#############################################################################################################################
# Driver Code
if __name__ == "__main__":
    main()