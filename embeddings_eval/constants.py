# Constants for WavLM Evaluation

# Task Groups
GROUP_DDK = 'ddk'
GROUP_MONOLOGUE = 'monologue'
GROUP_READTEXT = 'readtext'
GROUP_SENTENCE = 'sentence'
GROUP_WORDS = 'words'

ALL_GROUPS = [GROUP_DDK, GROUP_MONOLOGUE, GROUP_READTEXT, GROUP_SENTENCE, GROUP_WORDS]

# Health Status
STATUS_PD = 'PD'
STATUS_HC = 'HC'

# Gender Status
SEX_M = 'M'
SEX_F = 'F'

# Visualization Colors (PD vs HC x Male vs Female)
# Men (M)
COLOR_M_PD = '#FF0000'   # Red
COLOR_M_HC = '#008000'   # Green
# Women (F)
COLOR_F_PD = '#FF77FF'   # Light Purple/Magenta
COLOR_F_HC = '#90EE90'   # Light Green

# Visualization Symbols (Matplotlib markers)
SYMBOL_SPEAKER_CENTROID = '*'  # Star
SYMBOL_SAMPLE = 'o'            # Circle (Default fallback)

# Group-specific markers
GROUP_MARKERS = {
    GROUP_DDK: 'v',        # Inverted Triangle
    GROUP_MONOLOGUE: 's',  # Square
    GROUP_READTEXT: 'p',   # Pentagon
    GROUP_SENTENCE: 'h',   # Hexagon
    GROUP_WORDS: '^'       # Triangle
}
