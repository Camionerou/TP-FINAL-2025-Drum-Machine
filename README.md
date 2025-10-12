# 🥁 Raspberry Pi Drum Machine

Drum machine profesional construida con Raspberry Pi 3 B+ que incluye secuenciador de 16 pasos, modo de pads en tiempo real, display LED 8x32, y controles con potenciómetros.

## 📋 Características

- **8 Instrumentos de batería**: Kick, Snare, Hi-Hats (cerrado/abierto), Toms, Crash, Ride
- **Modo Pad**: Tocar batería en tiempo real como pads electrónicos
- **Modo Secuenciador**: Programar patrones de 16 pasos
- **Display LED 8x32**: Visualización del patrón y parámetros en tiempo real
- **8 Potenciómetros**: Control de tempo, swing, volumen master y volúmenes individuales
- **16 Botones**: 8 pads de instrumento + 8 funciones de control
- **Swing**: Groove humanizado configurable
- **Guardado de patrones**: Hasta 8 patrones guardables en JSON
- **LEDs indicadores**: Estado visual del modo y reproducción

## 🛠️ Hardware Necesario

### Componentes Principales
- Raspberry Pi 3 B+
- Matriz LED MAX7219 8x32 (4 módulos de 8x8)
- Conversor ADC MCP3008
- Matriz de botones 4x4 (16 pulsadores)
- 8 Potenciómetros de 10kΩ

### LEDs y Componentes Adicionales
- 5 LEDs (rojo, verde, amarillo, azul, blanco)
- 5 resistencias de 220Ω (para LEDs)
- Cables jumper
- Protoboard o PCB

### Opcional
- Amplificador de audio o altavoz con entrada 3.5mm
- Fuente de alimentación 5V/2.5A mínimo

## 🔌 Conexiones Hardware

### Bus SPI Compartido
Ambos dispositivos SPI (MAX7219 y MCP3008) comparten las líneas de datos y reloj:
- **MOSI (Master Out Slave In)**: GPIO 10 - Pin 19
- **MISO (Master In Slave Out)**: GPIO 9 - Pin 21
- **SCLK (Clock)**: GPIO 11 - Pin 23

### MAX7219 - Display LED 8x32
```
MAX7219         Raspberry Pi
VCC         →   5V (Pin 2 o 4)
GND         →   GND (cualquier pin GND)
DIN         →   GPIO 10 / MOSI (Pin 19)
CLK         →   GPIO 11 / SCLK (Pin 23)
CS          →   GPIO 8 / CE0 (Pin 24)
```

### MCP3008 - ADC de 8 canales
```
MCP3008         Raspberry Pi
VDD         →   3.3V (Pin 1 o 17)
VREF        →   3.3V (Pin 1 o 17)
AGND        →   GND
DGND        →   GND
DIN         →   GPIO 10 / MOSI (Pin 19)
DOUT        →   GPIO 9 / MISO (Pin 21)
CLK         →   GPIO 11 / SCLK (Pin 23)
CS          →   GPIO 7 / CE1 (Pin 26)
CH0-CH7     →   Potenciómetros (ver abajo)
```

### Matriz de Botones 4x4
Configuración con pull-up interno:
```
Filas:
Fila 1      →   GPIO 17 (Pin 11)
Fila 2      →   GPIO 27 (Pin 13)
Fila 3      →   GPIO 22 (Pin 15)
Fila 4      →   GPIO 23 (Pin 16)

Columnas:
Columna 1   →   GPIO 24 (Pin 18)
Columna 2   →   GPIO 25 (Pin 22)
Columna 3   →   GPIO 5 (Pin 29)
Columna 4   →   GPIO 6 (Pin 31)
```

Conectar cada intersección fila-columna con un pulsador normalmente abierto.

### Potenciómetros (10kΩ)
Cada potenciómetro se conecta así:
- **Terminal 1**: GND
- **Terminal 2 (central/wiper)**: Canal MCP3008 (CH0-CH7)
- **Terminal 3**: 3.3V ⚠️ **IMPORTANTE: NO usar 5V!**

Asignación de canales:
- **CH0**: Tempo (60-200 BPM)
- **CH1**: Swing (0-75%)
- **CH2**: Volumen Master
- **CH3**: Volumen Kick
- **CH4**: Volumen Snare
- **CH5**: Volumen Hi-Hats
- **CH6**: Volumen Toms
- **CH7**: Volumen Cymbals

### LEDs Indicadores
Todos los LEDs con resistencias de 220Ω:
```
LED Rojo (Modo Pad)         →   GPIO 12 (Pin 32) → 220Ω → LED → GND
LED Verde (Modo Seq)        →   GPIO 16 (Pin 36) → 220Ω → LED → GND
LED Amarillo (Playing)      →   GPIO 20 (Pin 38) → 220Ω → LED → GND
LED Azul (Beat)             →   GPIO 21 (Pin 40) → 220Ω → LED → GND
LED Blanco (Save)           →   GPIO 26 (Pin 37) → 220Ω → LED → GND
```

## 📦 Instalación

### 1. Preparar Raspberry Pi

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3-pip python3-pygame portaudio19-dev

# Habilitar SPI
sudo raspi-config
# Seleccionar: Interface Options → SPI → Enable
```

### 2. Clonar o copiar el proyecto

```bash
cd ~
git clone <tu-repositorio> DRUMMACHINE
# O copiar todos los archivos al directorio DRUMMACHINE
cd DRUMMACHINE
```

### 3. Instalar dependencias Python

```bash
pip3 install -r requirements.txt
```

### 4. Preparar samples de audio

Coloca tus samples WAV en el directorio `samples/`:
- `kick.wav`
- `snare.wav`
- `chh.wav` (Closed Hi-Hat)
- `ohh.wav` (Open Hi-Hat)
- `tom1.wav`
- `tom2.wav`
- `crash.wav`
- `ride.wav`

**Formato recomendado**: 44.1kHz, 16-bit, mono, WAV

Puedes descargar samples gratuitos de sitios como:
- [Freesound.org](https://freesound.org)
- [99Sounds](https://99sounds.org)
- [Sample Focus](https://samplefocus.com)

## 🚀 Uso

### Iniciar la Drum Machine

```bash
cd ~/DRUMMACHINE
python3 main.py
```

### Controles

#### Botones 1-8: Instrumentos/Pads
En **Modo PAD**: Tocan los instrumentos directamente
En **Modo SEQUENCER**: Activan/desactivan notas en el paso seleccionado

Asignación:
1. Kick
2. Snare
3. Closed Hi-Hat
4. Open Hi-Hat
5. Tom 1
6. Tom 2
7. Crash
8. Ride

#### Botones de Control (9-16)

| Botón | Función |
|-------|---------|
| 9 | **Play/Stop** - Iniciar/detener secuenciador |
| 10 | **Modo** - Cambiar entre PAD y SEQUENCER |
| 11 | **Tempo -** - Disminuir BPM |
| 12 | **Tempo +** - Aumentar BPM |
| 13 | **Patrón** - Cambiar al siguiente patrón (1-8) |
| 14 | **Clear** - Limpiar patrón actual |
| 15 | **Save** - Guardar patrón actual |
| 16 | **Step Select** - Seleccionar paso en secuenciador |

#### Potenciómetros

| Pot | Control |
|-----|---------|
| 0 | Tempo (60-200 BPM) |
| 1 | Swing (0-75%) |
| 2 | Volumen Master |
| 3 | Volumen Kick |
| 4 | Volumen Snare |
| 5 | Volumen Hi-Hats |
| 6 | Volumen Toms |
| 7 | Volumen Cymbals |

#### LEDs Indicadores

- **LED Rojo**: Modo PAD activo
- **LED Verde**: Modo SEQUENCER activo
- **LED Amarillo**: Secuenciador reproduciendo
- **LED Azul**: Indicador de beat (parpadea al tempo)
- **LED Blanco**: Confirmación de guardado

### Display LED

El display 8x32 está dividido en 3 zonas:
- **Zona 1 (columnas 0-7)**: Pasos 1-8 del secuenciador
- **Zona 2 (columnas 8-15)**: Pasos 9-16 del secuenciador
- **Zona 3 (columnas 16-31)**: Información (BPM, patrón, modo)

## 🎵 Workflow de Uso

### Modo PAD (Tocar en tiempo real)
1. Presionar Botón 10 hasta que LED Rojo esté encendido
2. Presionar Botones 1-8 para tocar instrumentos
3. Ajustar volúmenes con potenciómetros 3-7
4. Ajustar volumen master con potenciómetro 2

### Modo SEQUENCER (Programar patrones)
1. Presionar Botón 10 hasta que LED Verde esté encendido
2. Usar Botón 16 para seleccionar paso (0-15)
3. Presionar Botones 1-8 para activar/desactivar instrumentos en ese paso
4. Ajustar tempo con potenciómetro 0 o Botones 11/12
5. Ajustar swing con potenciómetro 1
6. Presionar Botón 9 para reproducir
7. Presionar Botón 15 para guardar el patrón

### Gestión de Patrones
- Presionar Botón 13 para cambiar entre patrones 1-8
- Cada patrón se guarda independientemente en `patterns/pattern_X.json`
- Los patrones incluyen notas, BPM y swing

## 📁 Estructura del Proyecto

```
DRUMMACHINE/
├── main.py                 # Programa principal
├── config.py              # Configuración de pines y constantes
├── audio_engine.py        # Motor de audio
├── sequencer.py           # Secuenciador de 16 pasos
├── hardware/
│   ├── __init__.py
│   ├── button_matrix.py   # Lectura de matriz 4x4
│   ├── led_matrix.py      # Control MAX7219
│   ├── adc_reader.py      # Lectura MCP3008
│   └── led_controller.py  # Control de LEDs
├── samples/               # Samples de audio WAV
├── patterns/              # Patrones guardados (JSON)
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## 🔧 Configuración Avanzada

### Ajustar Latencia de Audio

Editar `config.py`:
```python
AUDIO_BUFFER_SIZE = 512  # Menor = menos latencia, mayor CPU
```

### Cambiar Brillo del Display

Editar `config.py`:
```python
MAX7219_BRIGHTNESS = 3  # 0-15
```

### Personalizar Pines GPIO

Todos los pines están definidos en `config.py` y pueden modificarse según necesidad.

## 🐛 Solución de Problemas

### "No se encuentra RPi.GPIO"
El código incluye mocks para desarrollo. En Raspberry Pi real, instalar:
```bash
pip3 install RPi.GPIO
```

### "No se encuentra spidev"
```bash
pip3 install spidev
```

### SPI no funciona
Verificar que SPI esté habilitado:
```bash
ls /dev/spi*
# Debería mostrar /dev/spidev0.0 y /dev/spidev0.1
```

### Audio con latencia
1. Reducir `AUDIO_BUFFER_SIZE` en `config.py`
2. Verificar que los samples sean cortos y optimizados
3. Usar samples en formato WAV mono 44.1kHz

### Los botones no responden
1. Verificar conexiones de filas y columnas
2. Ajustar `DEBOUNCE_TIME` en `config.py`
3. Probar cada botón individualmente

### Display LED no muestra nada
1. Verificar conexión SPI (DIN, CLK, CS)
2. Verificar alimentación 5V del MAX7219
3. Aumentar brillo en `config.py`

## 📝 Notas Importantes

- **⚠️ Voltaje**: El MCP3008 usa 3.3V, NO conectar potenciómetros a 5V
- **⚠️ Alimentación**: Usar fuente de al menos 2.5A para Raspberry Pi
- **⚠️ SPI**: Habilitar SPI en raspi-config antes de usar
- Los samples de audio NO están incluidos, debes agregarlos tú mismo

## 🎨 Personalización

### Agregar más instrumentos
1. Agregar samples en `samples/`
2. Actualizar `INSTRUMENTS` en `config.py`
3. Ajustar `NUM_INSTRUMENTS`

### Cambiar número de pasos
Modificar `NUM_STEPS` en `config.py` (requiere ajustes en display)

### Agregar efectos
Modificar `audio_engine.py` para incluir reverb, delay, etc.

## 📜 Licencia

Este proyecto es de código abierto. Úsalo, modifícalo y mejóralo como quieras.

## 🙏 Créditos

Desarrollado para Raspberry Pi 3 B+
Samples de audio no incluidos (usar fuentes gratuitas mencionadas arriba)

---

**¡Disfruta tu Drum Machine!** 🥁🎶

