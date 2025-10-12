# 📦 Instrucciones para Subir y Usar la Drum Machine

## 🚀 PARTE 1: Subir el Repositorio a GitHub

### Paso 1: Crear el Repositorio en GitHub

1. Ve a [GitHub](https://github.com)
2. Haz clic en el botón **"+"** arriba a la derecha → **"New repository"**
3. Configura el repositorio:
   - **Repository name**: `TP-FINAL-2025-Drum-Machine`
   - **Description**: `Drum Machine profesional con Raspberry Pi 3 B+ - Secuenciador de 16 pasos, pads en tiempo real, display LED 8x32`
   - **Visibility**: Public (o Private si prefieres)
   - **NO** marques "Initialize this repository with a README" (ya tenemos uno)
4. Haz clic en **"Create repository"**

### Paso 2: Conectar y Subir desde tu Mac

Abre la terminal en tu Mac y ejecuta estos comandos:

```bash
cd /Users/enzosaldivia/DRUMMACHINE

# Configurar el nombre de la rama principal (si es necesario)
git branch -M main

# Conectar con tu repositorio de GitHub (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/TP-FINAL-2025-Drum-Machine.git

# Subir el código
git push -u origin main
```

**Nota**: Si te pide credenciales, usa un **Personal Access Token** en lugar de tu contraseña:
- Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token (classic)
- Dale permisos de "repo"
- Copia el token y úsalo como contraseña

---

## 💻 PARTE 2: Instalar en la Raspberry Pi

### Opción A: Clonación Directa (Recomendado)

#### 1. Conectarse a la Raspberry Pi

```bash
# Desde tu Mac, conéctate via SSH
ssh pi@DIRECCION_IP_DE_TU_RPI

# O usa el nombre de host si está configurado
ssh pi@raspberrypi.local
```

**Contraseña por defecto**: `raspberry` (cámbiala si no lo has hecho)

#### 2. Clonar el Repositorio

```bash
# Una vez dentro de la Raspberry Pi
cd ~
git clone https://github.com/TU_USUARIO/TP-FINAL-2025-Drum-Machine.git
cd TP-FINAL-2025-Drum-Machine
```

#### 3. Ejecutar el Script de Instalación

```bash
# Hacer el script ejecutable (si no lo es)
chmod +x install.sh

# Ejecutar instalación
./install.sh
```

Este script hará:
- Actualizar el sistema
- Instalar dependencias (pygame, spidev, RPi.GPIO)
- Crear directorios necesarios
- Configurar permisos

#### 4. Habilitar SPI (MUY IMPORTANTE)

```bash
sudo raspi-config
```

- Selecciona: **3 Interface Options**
- Selecciona: **I4 SPI**
- Selecciona: **Yes** para habilitar SPI
- Selecciona: **Finish**
- Reinicia: `sudo reboot`

#### 5. Agregar Samples de Audio

**IMPORTANTE**: El proyecto NO incluye los samples de audio (son archivos grandes).

```bash
cd ~/TP-FINAL-2025-Drum-Machine/samples

# Opción 1: Copiar desde tu Mac usando SCP
# En tu Mac, ejecuta:
# scp kick.wav snare.wav chh.wav ohh.wav tom1.wav tom2.wav crash.wav ride.wav pi@IP_RPI:~/TP-FINAL-2025-Drum-Machine/samples/

# Opción 2: Descargar samples gratuitos
# Visita: https://freesound.org o https://99sounds.org
# Descarga samples de batería y nómbralos como:
# kick.wav, snare.wav, chh.wav, ohh.wav, tom1.wav, tom2.wav, crash.wav, ride.wav
```

**Formato requerido**: WAV, 44.1kHz, 16-bit, mono

#### 6. Conectar el Hardware

Sigue el archivo `PINOUT.txt` para todas las conexiones:

```bash
# Ver el pinout detallado
cat PINOUT.txt
```

**Puntos críticos**:
- ✅ MAX7219: 5V para alimentación
- ✅ MCP3008: **3.3V** (NO 5V) para alimentación y potenciómetros
- ✅ SPI habilitado en raspi-config
- ✅ GND común para todos los componentes

#### 7. Probar el Hardware

```bash
cd ~/TP-FINAL-2025-Drum-Machine
python3 test_hardware.py
```

Este script probará:
- LEDs indicadores
- Display LED MAX7219
- Potenciómetros (MCP3008)
- Matriz de botones
- Motor de audio

#### 8. ¡Ejecutar la Drum Machine!

```bash
python3 main.py
```

Para salir: **Ctrl+C**

---

### Opción B: Copiar por SCP (Sin Git)

Si prefieres copiar los archivos directamente sin usar Git:

```bash
# Desde tu Mac
cd /Users/enzosaldivia
scp -r DRUMMACHINE pi@IP_RPI:~/

# Luego en la RPi, renombrar
ssh pi@IP_RPI
mv ~/DRUMMACHINE ~/TP-FINAL-2025-Drum-Machine
cd ~/TP-FINAL-2025-Drum-Machine
./install.sh
```

---

## 🎮 Uso Rápido

Una vez todo instalado:

```bash
cd ~/TP-FINAL-2025-Drum-Machine
python3 main.py
```

### Controles Básicos

**Botones:**
- 1-8: Instrumentos (Kick, Snare, Hi-Hats, Toms, Cymbals)
- 9: Play/Stop
- 10: Cambiar modo (PAD ↔ SEQUENCER)
- 11-12: Tempo -/+
- 13: Cambiar patrón (1-8)
- 14: Limpiar patrón
- 15: Guardar patrón
- 16: Seleccionar paso

**Potenciómetros:**
- 0: Tempo
- 1: Swing
- 2: Volumen Master
- 3-7: Volúmenes individuales

**LEDs:**
- Rojo: Modo PAD
- Verde: Modo SEQUENCER
- Amarillo: Reproduciendo
- Azul: Beat
- Blanco: Guardado exitoso

---

## 🔧 Solución de Problemas

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
# Verificar que SPI esté habilitado
ls /dev/spi*
# Debe mostrar: /dev/spidev0.0 y /dev/spidev0.1

# Si no aparece, habilitar en raspi-config
sudo raspi-config
```

### Audio no suena

1. Verificar que los samples WAV estén en `samples/`
2. Verificar formato: 44.1kHz, 16-bit, mono
3. Probar salida de audio: `speaker-test -t wav -c 2`

### Display LED no muestra nada

1. Verificar conexión SPI (DIN, CLK, CS)
2. Verificar alimentación 5V del MAX7219
3. Aumentar brillo en `config.py`: `MAX7219_BRIGHTNESS = 10`

---

## 📂 Estructura del Proyecto

```
TP-FINAL-2025-Drum-Machine/
├── main.py                 # 🎮 Ejecutar esto
├── config.py              # ⚙️ Configuración
├── audio_engine.py        # 🔊 Motor de audio
├── sequencer.py           # 🎵 Secuenciador
├── hardware/              # 🔌 Módulos de hardware
├── samples/               # 🥁 Agregar tus WAV aquí
├── patterns/              # 💾 Patrones guardados
├── install.sh             # 📦 Script de instalación
├── test_hardware.py       # 🧪 Probar hardware
├── PINOUT.txt            # 📋 Diagrama de conexiones
└── README.md             # 📖 Documentación completa
```

---

## 🎯 Checklist de Instalación

- [ ] Repositorio clonado en la RPi
- [ ] Script `install.sh` ejecutado
- [ ] SPI habilitado en `raspi-config`
- [ ] Samples WAV agregados a `samples/`
- [ ] Hardware conectado según `PINOUT.txt`
- [ ] Test de hardware ejecutado (`test_hardware.py`)
- [ ] Drum machine funcionando (`main.py`)

---

## 📞 Recursos Adicionales

- **README.md**: Documentación completa del proyecto
- **PINOUT.txt**: Diagrama ASCII detallado de conexiones
- **samples/README.md**: Cómo obtener samples gratuitos
- **test_hardware.py**: Script de diagnóstico de hardware

---

## 🎵 ¡Disfruta tu Drum Machine!

Para cualquier duda, consulta el `README.md` completo.

**Happy drumming!** 🥁🎶

