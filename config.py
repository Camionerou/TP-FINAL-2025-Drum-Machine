"""
Configuración de hardware y constantes para Raspberry Pi Drum Machine
"""

# ===== PINES GPIO =====

# Matriz de botones 4x4
BUTTON_ROWS = [17, 27, 22, 23]      # GPIO para filas (pines 11, 13, 15, 16)
BUTTON_COLS = [24, 25, 5, 6]        # GPIO para columnas (pines 18, 22, 29, 31)

# LEDs indicadores
LED_RED = 12        # Modo Pad activo (pin 32)
LED_GREEN = 16      # Modo Secuenciador activo (pin 36)
LED_YELLOW = 20     # Secuenciador reproduciendo (pin 38)
LED_BLUE = 21       # Beat/tempo indicator (pin 40)
LED_WHITE = 26      # Patrón guardado (pin 37)

# SPI Dispositivos
# MAX7219 usa CE0 (GPIO 8, pin 24)
# MCP3008 usa CE1 (GPIO 7, pin 26)
SPI_MAX7219_CE = 0  # CE0
SPI_MCP3008_CE = 1  # CE1

# ===== CONSTANTES DE AUDIO =====

# Instrumentos
INSTRUMENTS = [
    'kick',      # 0
    'snare',     # 1
    'chh',       # 2 - Closed Hi-Hat
    'ohh',       # 3 - Open Hi-Hat
    'tom1',      # 4
    'tom2',      # 5
    'crash',     # 6
    'ride'       # 7
]

NUM_INSTRUMENTS = len(INSTRUMENTS)

# Configuración de audio
SAMPLE_RATE = 44100
AUDIO_BUFFER_SIZE = 512  # Buffer bajo para latencia mínima
AUDIO_CHANNELS = 8       # Permitir 8 sonidos simultáneos

# ===== CONSTANTES DEL SECUENCIADOR =====

NUM_STEPS = 16           # 16 pasos en el secuenciador
BPM_MIN = 60
BPM_MAX = 200
BPM_DEFAULT = 120
SWING_MAX = 75           # Swing máximo en porcentaje

# ===== CONSTANTES DE POTENCIÓMETROS =====

# Canales del MCP3008
POT_TEMPO = 0
POT_SWING = 1
POT_MASTER_VOL = 2
POT_KICK_VOL = 3
POT_SNARE_VOL = 4
POT_HIHATS_VOL = 5
POT_TOMS_VOL = 6
POT_CYMBALS_VOL = 7

# Configuración ADC
ADC_MAX_VALUE = 1023
ADC_THRESHOLD = 10       # Cambio mínimo para considerar un ajuste

# ===== CONSTANTES DE DISPLAY =====

# MAX7219 configuración
MAX7219_NUM_DEVICES = 4  # 4 módulos de 8x8 = 8x32
MAX7219_BRIGHTNESS = 3   # 0-15, ajustar según necesidad

# ===== MODOS DE OPERACIÓN =====

MODE_PAD = 0
MODE_SEQUENCER = 1

# ===== MAPEO DE BOTONES =====

# Botones 0-7: Instrumentos/pads
# Botones 8-15: Funciones de control
BTN_PLAY_STOP = 8
BTN_MODE = 9
BTN_TEMPO_DOWN = 10
BTN_TEMPO_UP = 11
BTN_PATTERN = 12
BTN_CLEAR = 13
BTN_SAVE = 14
BTN_STEP_SELECT = 15

# ===== RUTAS =====

SAMPLES_DIR = 'samples'
PATTERNS_DIR = 'patterns'
MAX_PATTERNS = 8

# ===== TIMING =====

MAIN_LOOP_FPS = 60       # FPS del loop principal
DEBOUNCE_TIME = 0.02     # 20ms debounce para botones

# ===== CONFIGURACIÓN DE VOLUMEN =====

MASTER_VOLUME_DEFAULT = 0.8
INSTRUMENT_VOLUME_DEFAULT = 1.0

