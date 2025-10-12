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

NUM_STEPS = 32           # 32 pasos en el secuenciador (expandido)
BPM_MIN = 60
BPM_MAX = 200
BPM_DEFAULT = 120
SWING_MAX = 75           # Swing máximo en porcentaje

# ===== CONSTANTES DE POTENCIÓMETROS =====

# Canales del MCP3008 (Sistema de vistas dinámicas)
POT_SCROLL = 0          # Scroll entre pasos 0-31 (selecciona paso a editar)
POT_TEMPO = 1           # BPM 60-200 → Trigger vista BPM
POT_SWING = 2           # Swing 0-75% → Trigger vista SWING
POT_MASTER = 3          # Volumen Master → Trigger vista VOLUMEN
POT_VOL_DRUMS = 4       # Vol Kick + Snare (grupo ritmo)
POT_VOL_HATS = 5        # Vol CHH + OHH (grupo hi-hats)
POT_VOL_TOMS = 6        # Vol Tom1 + Tom2 (grupo toms)
POT_VOL_CYMS = 7        # Vol Crash + Ride (grupo cymbals)

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

# ===== MAPEO DE BOTONES (Sistema mejorado) =====

# Botones 0-7: Instrumentos/pads (función depende del modo)
# En modo PAD: Tocan instrumento + trigger vista PAD
# En modo SEQUENCER: Toggle nota en paso actual (POT_SCROLL)

# Botones 8-15: Funciones inteligentes
BTN_PLAY_STOP = 8       # Simple: Play/Stop | Doble: Reset a paso 0
BTN_MODE = 9            # Simple: Cambiar modo | Hold 2s: Bloquear modo
BTN_PATTERN_PREV = 10   # Simple: Patrón anterior | Hold: Rápido
BTN_PATTERN_NEXT = 11   # Simple: Patrón siguiente | Hold: Rápido
BTN_CLEAR = 12          # Simple: Clear paso | Doble: Clear instrumento | Hold 3s: Clear patrón
BTN_SAVE = 13           # Simple: Guardar | Hold+11/12: Guardar en patrón específico
BTN_COPY = 14           # Simple: Copiar paso | Hold+11/12: Pegar
BTN_MUTE = 15           # Simple: Mute paso | Doble: Solo | Hold+1-8: Mute global

# ===== RUTAS =====

SAMPLES_DIR = 'samples'
PATTERNS_DIR = 'patterns'
MAX_PATTERNS = 8

# ===== TIMING =====

MAIN_LOOP_FPS = 60       # FPS del loop principal
DEBOUNCE_TIME = 0.02     # 20ms debounce para botones

# ===== SISTEMA DE VISTAS =====

VIEW_TIMEOUT = 1.0       # Segundos antes de volver a vista SEQUENCER
VIEW_INACTIVITY_TIMEOUT = 3.0  # Segundos de inactividad para forzar SEQUENCER
ANIMATION_FPS = 10       # FPS para animaciones de vistas

# ===== DETECCIÓN DE EVENTOS DE BOTONES =====

DOUBLE_CLICK_TIME = 0.3  # Tiempo máximo entre clicks para doble-click
HOLD_TIME = 0.8          # Tiempo mínimo para botón mantenido
LONG_HOLD_TIME = 3.0     # Tiempo para hold largo (clear completo, etc)

# ===== CONFIGURACIÓN DE VOLUMEN =====

MASTER_VOLUME_DEFAULT = 0.8
INSTRUMENT_VOLUME_DEFAULT = 1.0

