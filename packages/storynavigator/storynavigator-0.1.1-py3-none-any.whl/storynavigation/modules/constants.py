import sys

if sys.version_info < (3, 9):
    # importlib.resources either doesn't exist or lacks the files()
    # function, so use the PyPI version:
    import importlib_resources
else:
    import importlib.resources as importlib_resources

# metrics for measuring importance of characters or actors in the story
AGENT_PROMINENCE_METRICS = ['Subject frequency', 'Subject frequency (normalized)']
SFREQ_METRIC = 'Subject frequency'
SFREQ_NORM_METRIC = 'Subject frequency (normalized)'

# list of punctuation characters
PUNC = '''!()-[]{};:'"\\,<>./?@#$%^&*_~0123456789'''

# name of storynavigator package directory
MAIN_PACKAGE = "storynavigation"
# directory name for resource files for usage by storynavigator add-on
RESOURCES_SUBPACKAGE = "resources"

# Supported languages
NL = 'nl'
EN = 'en'
SUPPORTED_LANGUAGES = [EN, NL]

# Yes / no
YES = "yes"
NO = "no"
YES_NO_WORDS = [YES, NO]

# Number of story segments
N_STORY_SEGMENTS = list(range(1,11))

# filename from which to retrieve a list of dutch stopwords
NL_STOPWORDS_FILENAME = "dutchstopwords.txt"
# filename from which to retrieve a list of dutch past tense verbs
NL_PAST_TENSE_FILENAME = "past_tense_verbs_dutch.txt"
# filename from which to retrieve a list of dutch present tense verbs
NL_PRESENT_TENSE_FILENAME = "present_tense_verbs_dutch.txt"
# filename from which to retrieve a list of dutch false positive verbs
NL_FALSE_POSITIVE_VERB_FILENAME = "false_positive_verbs_dutch.txt"
# filename from which to retrieve a list of dutch stopwords
NL_PRONOUNS_FILENAME = "dutchpronouns.txt"
# filename from which to retrieve a list of dutch time words
NL_TIME_WORDS_FILENAME = "dutch_time_words.csv"
# filename from which to retrieve a list of dutch verb frames
NL_VERB_FRAMES_FILENAME = "dutch_verb_frames.csv"

# filename from which to retrieve a list of english stopwords
EN_STOPWORDS_FILENAME = "englishstopwords.txt"
# filename from which to retrieve a list of english past tense verbs
EN_PAST_TENSE_FILENAME = "past_tense_verbs_english.txt"
# filename from which to retrieve a list of english present tense verbs
EN_PRESENT_TENSE_FILENAME = "present_tense_verbs_english.txt"
# filename from which to retrieve a list of english false positive verbs
EN_FALSE_POSITIVE_VERB_FILENAME = "false_positive_verbs_english.txt"
# filename from which to retrieve a list of english stopwords
EN_PRONOUNS_FILENAME = "englishpronouns.txt"
# filename from which to retrieve a list of english time words
EN_TIME_WORDS_FILENAME = "english_time_words.csv"
# filename from which to retrieve a list of english verb frames
EN_VERB_FRAMES_FILENAME = "english_verb_frames.csv"


# package paths
PKG = importlib_resources.files(MAIN_PACKAGE)

NL_STOPWORDS_FILE = (
    PKG / RESOURCES_SUBPACKAGE / NL_STOPWORDS_FILENAME
)

NL_PRONOUNS_FILE = (
    PKG / RESOURCES_SUBPACKAGE / NL_PRONOUNS_FILENAME
)

NL_PAST_TENSE_FILE = (
    PKG / RESOURCES_SUBPACKAGE / NL_PAST_TENSE_FILENAME
)

NL_PRESENT_TENSE_FILE = (
    PKG / RESOURCES_SUBPACKAGE / NL_PRESENT_TENSE_FILENAME
)

NL_FALSE_POSITIVE_VERB_FILE = (
    PKG / RESOURCES_SUBPACKAGE / NL_FALSE_POSITIVE_VERB_FILENAME
)

NL_VERB_FRAMES_FILE = (
    PKG / RESOURCES_SUBPACKAGE / NL_VERB_FRAMES_FILENAME
)


NL_TIME_WORDS_FILE = (
    PKG / RESOURCES_SUBPACKAGE / NL_TIME_WORDS_FILENAME
)

EN_STOPWORDS_FILE = (
    PKG / RESOURCES_SUBPACKAGE / EN_STOPWORDS_FILENAME
)

EN_PRONOUNS_FILE = (
    PKG / RESOURCES_SUBPACKAGE / EN_PRONOUNS_FILENAME
)

EN_PAST_TENSE_FILE = (
    PKG / RESOURCES_SUBPACKAGE / EN_PAST_TENSE_FILENAME
)

EN_PRESENT_TENSE_FILE = (
    PKG / RESOURCES_SUBPACKAGE / EN_PRESENT_TENSE_FILENAME
)

EN_FALSE_POSITIVE_VERB_FILE = (
    PKG / RESOURCES_SUBPACKAGE / EN_FALSE_POSITIVE_VERB_FILENAME
)

EN_TIME_WORDS_FILE = (
    PKG / RESOURCES_SUBPACKAGE / EN_TIME_WORDS_FILENAME
)

EN_VERB_FRAMES_FILE = (
    PKG / RESOURCES_SUBPACKAGE / EN_VERB_FRAMES_FILENAME
)

# currently selected agent prominence metric
SELECTED_PROMINENCE_METRIC = 'Subject frequency'

# column names for agency table
FREQ_TABLE_HEADER = ['actor', 'raw_frequency']
ACTION_FREQ_TABLE_HEADER = ['action', 'raw_frequency']
ACTION_TENSEFREQ_TABLE_HEADER = ['tense', 'frequency']
SUBFREQ_TABLE_HEADER = ['actor', 'subject_frequency']
CUSTOMFREQ_TABLE_HEADER = ['category', 'frequency', 'category-level']
AGENCY_TABLE_HEADER = ['actor', 'agency']

# Halliday dimensions file
HALLIDAY_FILENAME = "halliday_dimensions_{}.json"

# dutch spacy model (small)
NL_SPACY_MODEL = "nl_core_news_sm"
# dutch spacy model (large)
NL_SPACY_MODEL_LG = "nl_core_news_lg"

# english spacy model (small)
EN_SPACY_MODEL = "en_core_web_sm"
# dutch spacy model (large)
EN_SPACY_MODEL_LG = "en_core_web_lg"

# colors for highlighting words in text
SUBJECT_PRONOUN_HIGHLIGHT_COLOR = "#87CEFA"
SUBJECT_NONPRONOUN_HIGHLIGHT_COLOR = "#ADD8E6"
NONSUBJECT_PRONOUN_HIGHLIGHT_COLOR = "#FFA500"
NONSUBJECT_NONPRONOUN_HIGHLIGHT_COLOR = "#FFE4B5"
ACTION_PAST_HIGHLIGHT_COLOR = "#FFC0CB"
ACTION_PRESENT_HIGHLIGHT_COLOR = "#DB7093"
CUSTOMTAG_HIGHLIGHT_COLOR = "#98FB98"

# test data file
TEST_DATA_FILE_NAME = "storynavigator-testdata.tab"

# color map
COLOR_MAP = {}
NON_SUBJECT_PRONOUN = "NSP"
NON_SUBJECT_NON_PRONOUN = "NSNP"
SUBJECT_PRONOUN = "SP"
SUBJECT_NON_PRONOUN = "SNP"
PAST_VB = "PAST_VB"
PRES_VB = "PRES_VB"

COLOR_MAP[NON_SUBJECT_PRONOUN] = NONSUBJECT_PRONOUN_HIGHLIGHT_COLOR
COLOR_MAP[NON_SUBJECT_NON_PRONOUN] = NONSUBJECT_NONPRONOUN_HIGHLIGHT_COLOR
COLOR_MAP[SUBJECT_PRONOUN] = SUBJECT_PRONOUN_HIGHLIGHT_COLOR
COLOR_MAP[SUBJECT_NON_PRONOUN] = SUBJECT_NONPRONOUN_HIGHLIGHT_COLOR
COLOR_MAP[PAST_VB] = ACTION_PAST_HIGHLIGHT_COLOR
COLOR_MAP[PRES_VB] = ACTION_PRESENT_HIGHLIGHT_COLOR

# column names in tagging information dataframe
TAGGING_DATAFRAME_COLUMNNAMES_BASE = ['storyid',
                                      'sentence',
                                      'token_text',
                                      'token_start_idx',
                                      'token_end_idx',
                                      'story_navigator_tag',
                                      'spacy_tag',
                                      'spacy_finegrained_tag',
                                      'spacy_dependency',
                                      'spacy_ne',
                                      'spacy_lemma',
                                      'spacy_head_text',
                                      'spacy_head_idx',
                                      'is_pronoun_boolean',
                                      'is_sentence_subject_boolean',
                                      'active_voice_subject_boolean',
                                      'associated_action',
                                      'voice',
                                      'future_verb']
TAGGING_DATAFRAME_COLUMNNAMES = TAGGING_DATAFRAME_COLUMNNAMES_BASE + ['sentence_id', 'segment_id', 'lang', 'num_words_in_sentence']

# means widget strategies
MEANS_STRATEGY_VERB_FRAMES = "use verb frames"
MEANS_STRATEGY_VERB_FRAME_PREPS = "use prepositions from verb frames   "
MEANS_STRATEGY_SPACY_PREPS = "use prepositions from Spacy"

# purpose widget strategies
PURPOSE_STRATEGY_ADVERBS = "use adverbs"
PURPOSE_STRATEGY_VERBS = "use verbs"

# first person words for purpose widget
NL_FIRST_PERSON_WORDS = ['ik', 'we', 'wij']
EN_FIRST_PERSON_WORDS = ['i', 'we']
