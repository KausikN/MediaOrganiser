"""
Stream lit GUI for hosting MediaOrganiser
"""

# Imports
import streamlit as st
import os
import json

from streamlit.cursor import make_delta_path

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
CACHEPATH_MOVIEDIRS = "StreamLitGUI/CacheData/MovieDirs.json"
CACHEPATH_SERIESDIRS = "StreamLitGUI/CacheData/SeriesDirs.json"

SAVEPATH_MOVIEDATA = 'OrganisedData/Movies/'
SAVEPATH_SERIESDATA = 'OrganisedData/Series/'

DEFAULT_PATH_POSTER = 'StreamLitGUI/DefaultData/MoviePosterNotFound.jpg'

# Main Vars
DATA_MOVIES = []
DATA_SERIES = []

# Util Vars
CACHE_MOVIEDIRS = []
CACHE_SERIESDIRS = []

# Util Functions
def Data_Path2SaveName(path):
    return path.strip("/").replace("/", ";").replace("\\", ";")

def LoadCacheData():
    global CACHE_MOVIEDIRS
    global CACHE_SERIESDIRS
    CACHE_MOVIEDIRS = json.load(open(CACHEPATH_MOVIEDIRS, 'r'))["dirs"]
    CACHE_SERIESDIRS = json.load(open(CACHEPATH_SERIESDIRS, 'r'))["dirs"]

def SaveCacheData():
    global CACHE_MOVIEDIRS
    global CACHE_SERIESDIRS
    json.dump({"dirs": CACHE_MOVIEDIRS}, open(CACHEPATH_MOVIEDIRS, 'w'))
    json.dump({"dirs": CACHE_SERIESDIRS}, open(CACHEPATH_SERIESDIRS, 'w'))

# Main Functions
def GenerateOrganisedData_Movies(paths):
    # Delete Prexisting Data
    for f in os.listdir(SAVEPATH_MOVIEDATA):
        os.remove(os.path.join(SAVEPATH_MOVIEDATA, f))
    # Generate New Data
    for path in paths:
        savePath = SAVEPATH_MOVIEDATA + "MoviesData_" + Data_Path2SaveName(path) + ".json"
        MediaOrganiser.MediaOrganise_Movies(path, savePath)

def GenerateOrganisedData_Series(paths):
    # Delete Prexisting Data
    for f in os.listdir(SAVEPATH_SERIESDATA):
        os.remove(os.path.join(SAVEPATH_SERIESDATA, f))
    # Generate New Data
    for path in paths:
        savePath = SAVEPATH_SERIESDATA + "SeriesData_" + Data_Path2SaveName(path) + ".json"
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
    if (MovieChoiceData["posterPath"] is not None) and (os.path.exists(MovieChoiceData["posterPath"])):
        st.image(MovieChoiceData["posterPath"], "Movie Poster", use_column_width=True)
    else:
        st.image(DEFAULT_PATH_POSTER, "Movie Poster", use_column_width=True)
    col1, col2 = st.beta_columns([1, 2])
    col1.markdown("Name:")
    col2.markdown(MovieChoiceData["name"])

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

    # Display Outputs
    SeasonsNames = GetNames(SeriesChoiceData["data"])
    USERINPUT_SeasonsChoice = st.selectbox("Select Season", ["Select Season"] + SeasonsNames)
    if USERINPUT_SeasonsChoice == "Select Season": return

    USERINPUT_SeasonsChoiceIndex = SeasonsNames.index(USERINPUT_SeasonsChoice)
    SeasonsChoiceData = SeriesChoiceData["data"][USERINPUT_SeasonsChoiceIndex]

    st.markdown("## Episodes")
    st.markdown("<hr>", unsafe_allow_html=True)
    for ep in SeasonsChoiceData["episodes"]:
        col1, col2 = st.beta_columns([1, 2])
        if (ep["posterPath"] is not None) and (os.path.exists(ep["posterPath"])):
            col1.image(ep["posterPath"], "Episode Poster", use_column_width=True)
        else:
            col1.image(DEFAULT_PATH_POSTER, "Episode Poster", use_column_width=True)
        col2.markdown(ep["name"])
        st.markdown("<hr>", unsafe_allow_html=True)

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