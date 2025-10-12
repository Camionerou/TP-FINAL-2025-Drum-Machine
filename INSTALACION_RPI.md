# 🥁 Instalación en Raspberry Pi - GUÍA RÁPIDA

## 📍 URL del Repositorio
**https://github.com/Camionerou/TP-FINAL-2025-Drum-Machine**

---

## 🚀 INSTALACIÓN COMPLETA (Copiar y Pegar)

### 1️⃣ Conectar a la Raspberry Pi

```bash
# Desde tu Mac/PC
ssh pi@DIRECCION_IP_DE_TU_RPI

# Contraseña por defecto: raspberry
# (cámbiala después con: passwd)
```

### 2️⃣ Clonar el Repositorio

```bash
cd ~
git clone https://github.com/Camionerou/TP-FINAL-2025-Drum-Machine.git
cd TP-FINAL-2025-Drum-Machine
```

### 3️⃣ Ejecutar Instalación Automática

```bash
chmod +x install.sh
./install.sh
```

### 4️⃣ Habilitar SPI (CRÍTICO)

```bash
sudo raspi-config
```

Navega con las flechas:
- **3 Interface Options**
- **I4 SPI**
- **Yes** (para habilitar)
- **Finish**
- **Yes** (para reiniciar)

```bash
# Después del reinicio, verificar
ls /dev/spi*
# Debe mostrar: /dev/spidev0.0 y /dev/spidev0.1
```

### 5️⃣ Agregar Samples de Audio

Los samples NO están incluidos. Debes agregarlos:

**Opción A: Copiar desde tu Mac**

```bash
# En tu Mac (en otra terminal)
cd /ruta/donde/tienes/tus/samples
scp kick.wav snare.wav chh.wav ohh.wav tom1.wav tom2.wav crash.wav ride.wav pi@IP_RPI:~/TP-FINAL-2025-Drum-Machine/samples/
```

**Opción B: Descargar desde Internet**

Descargar samples gratuitos de:
- https://freesound.org (busca "TR-808" o "drum samples")
- https://99sounds.org
- https://samplefocus.com

**Formato requerido:**
- Formato: WAV
- Sample Rate: 44.1 kHz
- Bit Depth: 16-bit
- Canales: Mono

**Nombres requeridos:**
- `kick.wav` - Bombo
- `snare.wav` - Redoblante
- `chh.wav` - Hi-Hat cerrado
- `ohh.wav` - Hi-Hat abierto
- `tom1.wav` - Tom agudo
- `tom2.wav` - Tom grave
- `crash.wav` - Crash cymbal
- `ride.wav` - Ride cymbal

### 6️⃣ Conectar Hardware

Sigue el diagrama completo en:
```bash
cat PINOUT.txt
```

**Conexiones críticas:**
- ⚠️ **MAX7219**: Alimentar con **5V**
- ⚠️ **MCP3008**: Alimentar con **3.3V** (NO 5V!)
- ⚠️ **Potenciómetros**: Conectar a **3.3V** (NO 5V!)
- ✅ **GND común** para todos los componentes
- ✅ **SPI compartido**: MOSI, MISO, SCLK
- ✅ **CS separados**: CE0 (MAX7219), CE1 (MCP3008)

### 7️⃣ Probar Hardware

```bash
cd ~/TP-FINAL-2025-Drum-Machine
python3 test_hardware.py
```

Este script probará:
- ✅ LEDs indicadores
- ✅ Display LED MAX7219
- ✅ Potenciómetros (MCP3008)
- ✅ Matriz de botones
- ✅ Motor de audio

### 8️⃣ ¡EJECUTAR LA DRUM MACHINE!

```bash
python3 main.py
```

**Para salir:** Presiona `Ctrl+C`

---

## 🎮 CONTROLES

### Botones (Matriz 4x4)

```
┌─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │  Kick, Snare, CHH, OHH
│ PAD │ PAD │ PAD │ PAD │
├─────┼─────┼─────┼─────┤
│  5  │  6  │  7  │  8  │  Tom1, Tom2, Crash, Ride
│ PAD │ PAD │ PAD │ PAD │
├─────┼─────┼─────┼─────┤
│  9  │ 10  │ 11  │ 12  │  Play/Stop, Mode, Tempo-, Tempo+
│PLAY │MODE │ T-  │ T+  │
├─────┼─────┼─────┼─────┤
│ 13  │ 14  │ 15  │ 16  │  Pattern, Clear, Save, Step
│PATT │CLEAR│SAVE │STEP │
└─────┴─────┴─────┴─────┘
```

### Potenciómetros

- **Pot 0**: Tempo (60-200 BPM)
- **Pot 1**: Swing (0-75%)
- **Pot 2**: Volumen Master
- **Pot 3**: Volumen Kick
- **Pot 4**: Volumen Snare
- **Pot 5**: Volumen Hi-Hats
- **Pot 6**: Volumen Toms
- **Pot 7**: Volumen Cymbals

### LEDs Indicadores

- 🔴 **Rojo**: Modo PAD activo
- 🟢 **Verde**: Modo SEQUENCER activo
- 🟡 **Amarillo**: Reproduciendo
- 🔵 **Azul**: Beat/tempo
- ⚪ **Blanco**: Patrón guardado

---

## 📖 MODOS DE USO

### Modo PAD (Tocar en tiempo real)

1. Presiona **Botón 10** hasta que LED ROJO esté encendido
2. Presiona **Botones 1-8** para tocar instrumentos
3. Ajusta volúmenes con potenciómetros

### Modo SEQUENCER (Programar ritmos)

1. Presiona **Botón 10** hasta que LED VERDE esté encendido
2. Usa **Botón 16** para seleccionar paso (0-15)
3. Presiona **Botones 1-8** para activar/desactivar instrumentos
4. Ajusta tempo con **Pot 0** o **Botones 11/12**
5. Ajusta swing con **Pot 1**
6. Presiona **Botón 9** para reproducir
7. Presiona **Botón 15** para guardar

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'RPi'"
```bash
pip3 install RPi.GPIO
```

### Error: "No module named 'spidev'"
```bash
pip3 install spidev
```

### SPI no funciona
```bash
# Verificar
ls /dev/spi*

# Si no aparece, habilitar en raspi-config
sudo raspi-config
# Interface Options → SPI → Enable → Reboot
```

### Audio no suena
```bash
# Verificar que los samples estén
ls -la samples/*.wav

# Probar audio del sistema
speaker-test -t wav -c 2
```

### Display LED no muestra nada
1. Verificar conexión SPI (DIN→GPIO10, CLK→GPIO11, CS→GPIO8)
2. Verificar alimentación 5V
3. Aumentar brillo en `config.py`: `MAX7219_BRIGHTNESS = 10`

### Potenciómetros no responden
1. Verificar que MCP3008 esté en 3.3V (NO 5V!)
2. Verificar conexión SPI (DIN→GPIO10, DOUT→GPIO9, CLK→GPIO11, CS→GPIO7)
3. Verificar que potenciómetros estén entre GND y 3.3V

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] RPi conectada y accesible por SSH
- [ ] Repositorio clonado
- [ ] `install.sh` ejecutado sin errores
- [ ] **SPI habilitado** (verificar con `ls /dev/spi*`)
- [ ] Samples WAV en carpeta `samples/`
- [ ] Hardware conectado según `PINOUT.txt`
- [ ] Test de hardware exitoso (`test_hardware.py`)
- [ ] Drum machine ejecutándose (`main.py`)

---

## 📱 EJECUTAR AL INICIO (OPCIONAL)

Para que se ejecute automáticamente al encender:

```bash
# Editar crontab
crontab -e

# Agregar esta línea
@reboot sleep 30 && cd /home/pi/TP-FINAL-2025-Drum-Machine && python3 main.py

# Guardar y salir
```

---

## 🎵 ¡LISTO PARA ROCKEAR!

Tu drum machine está lista. Ahora solo conecta todo el hardware y disfruta.

**Documentación completa:** README.md  
**Diagrama de pines:** PINOUT.txt  
**Repositorio:** https://github.com/Camionerou/TP-FINAL-2025-Drum-Machine

**Happy drumming!** 🥁🎶

