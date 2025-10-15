# 🥁 Raspberry Pi Drum Machine v2.5

Drum machine profesional con Raspberry Pi 3 B+ - Secuenciador de 32 pasos, pads en tiempo real, efectos master y salida Bluetooth.

---

## 🚀 Quick Start

```bash
# 1. Clonar o copiar el proyecto
cd ~
git clone <repositorio> DRUMMACHINE
cd DRUMMACHINE

# 2. Instalar
chmod +x scripts/install_service.sh scripts/optimize_boot.sh
sudo ./scripts/install_service.sh
sudo ./scripts/optimize_boot.sh

# 3. Reiniciar
sudo reboot
```

**¡Listo!** La drum machine arranca automáticamente al encender.

---

## ✨ Características

### Core
- **Secuenciador 32 pasos** × 8 instrumentos
- **Modo PAD** - Tocar en tiempo real
- **Modo SEQUENCER** - Programar patrones
- **Display LED 8×32** - Visualización completa
- **8 Patrones guardables** en JSON

### Audio Profesional
- **Efectos Master:**
  - Reverb (sala, plate, hall)
  - Delay (tiempo variable)
  - Compressor (dynamic range)
  - Filter (low-pass, high-pass)
  - Distortion/Saturation
- **Salida Bluetooth** - Audio inalámbrico
- **Soft Limiter** - Sin distorsión
- **Latencia < 5ms**

### Control Inteligente
- **16 Botones** - Multi-evento (click, doble-click, hold)
- **8 Potenciómetros** - Control analógico preciso
- **Tap Tempo** - Establecer BPM naturalmente
- **Swing 0-75%** - Groove humanizado

### Extras
- **MIDI Output** - Clock + Notes
- **Autoarranque** - Funciona al encender
- **Sistema de Vistas** - 10 vistas dinámicas

---

## 🎮 Controles Principales

### Botones 0-7: Instrumentos
| Botón | Instrumento | Modo PAD | Modo SEQ |
|-------|-------------|----------|----------|
| 0 | Kick | Tocar | Toggle nota |
| 1 | Snare | Tocar | Toggle nota |
| 2 | Closed Hi-Hat | Tocar | Toggle nota |
| 3 | Open Hi-Hat | Tocar | Toggle nota |
| 4 | Tom 1 | Tocar | Toggle nota |
| 5 | Tom 2 | Tocar | Toggle nota |
| 6 | Crash | Tocar | Toggle nota |
| 7 | Ride | Tocar | Toggle nota |

### Botones 8-15: Funciones
| Botón | Simple | Doble-Click | Hold |
|-------|--------|-------------|------|
| 8 | Play/Stop | Reset paso 0 | - |
| 9 | Cambiar Modo | - | Bloquear modo |
| 10 | Patrón - | - | - |
| 11 | Patrón + / **Tap Tempo** | Activar Tap | - |
| 12 | Clear paso | Clear instr. | **Vista EFFECTS** |
| 13 | Save | - | - |
| 14 | Copy | - | Paste |
| 15 | Mute | Solo | Menú Bluetooth |

### Potenciómetros
| Pot | Función | Vista |
|-----|---------|-------|
| 0 | Scroll pasos (0-31) | - |
| 1 | Tempo (60-200 BPM) | BPM |
| 2 | Swing (0-75%) | SWING |
| 3 | Master Volume | VOLUME |
| 4-7 | Volúmenes grupales | VOL_GROUP |

**En Vista EFFECTS:**
- Pot 0: Reverb
- Pot 1: Delay
- Pot 2: Compressor
- Pot 3: Filter
- Pot 4: Distortion

---

## 📦 Hardware Necesario

### Componentes Principales
- Raspberry Pi 3 B+
- Fuente 5V 3A
- MicroSD 16GB Clase 10

### Interfaz
- MAX7219 8×32 LED Display (4 módulos)
- MCP3008 ADC (lectura de pots)
- Matriz de botones 4×4
- 8× Potenciómetros 10kΩ
- 5× LEDs indicadores

### Audio
- Salida: Jack 3.5mm integrado
- Opcional: Altavoces Bluetooth

**Ver `PINOUT.txt` para conexiones detalladas.**

---

## 📚 Documentación Completa

**Todo en un solo lugar:**  
👉 **`INFORME_TECNICO_PRODUCTO.md`**

Incluye:
- Especificaciones técnicas completas
- Diagramas de arquitectura
- Guía de instalación detallada
- BOM con costos
- Historial de desarrollo
- Troubleshooting
- Referencias

---

## 🔧 Comandos Útiles

```bash
# Ver estado del servicio
sudo systemctl status drummachine

# Ver logs en tiempo real
sudo journalctl -u drummachine -f

# Detener (para desarrollo)
sudo systemctl stop drummachine

# Iniciar manualmente
cd ~/DRUMMACHINE
python3 main.py

# Actualizar desde Git
git pull
sudo systemctl restart drummachine
```

---

## 🎯 Workflow de Uso

### Crear un Ritmo (Modo SEQUENCER)

1. LED Verde encendido = Modo SEQUENCER
2. Girar **Pot 0** para seleccionar paso (0-31)
3. Presionar **Botones 0-7** para activar/desactivar instrumentos
4. **BTN 8** = Play/Stop
5. Ajustar tempo, swing y volúmenes con pots
6. **BTN 13** = Guardar patrón

### Tocar en Tiempo Real (Modo PAD)

1. **BTN 9** para cambiar a Modo PAD (LED Rojo)
2. Presionar **Botones 0-7** para tocar instrumentos
3. Ajustar volúmenes en tiempo real

### Usar Efectos

1. **Hold BTN 12** para entrar en Vista EFFECTS
2. Ajustar efectos con **Pots 0-4**
3. **BTN 13** para guardar preset
4. Esperar 2s o presionar otro botón para volver

### Tap Tempo

1. **Doble-click BTN 11** para activar modo Tap
2. Presionar **BTN 11** al ritmo deseado (mínimo 2 veces)
3. BPM se actualiza automáticamente

### Conectar Bluetooth

1. **Hold BTN 15** + **BTN 9** = Menú Bluetooth
2. Dispositivos disponibles en display
3. **Pot 0** para navegar, **BTN 13** para conectar

---

## 📝 Estructura del Proyecto

```
DRUMMACHINE/
├── core/                     # Módulos principales
├── ui/                       # Interfaz y vistas
├── features/                 # MIDI, Bluetooth, Efectos
├── hardware/                 # Drivers de periféricos
├── data/                     # Samples y patrones
├── scripts/                  # Instalación y utilidades
├── main.py                   # Punto de entrada
├── requirements.txt
├── INFORME_TECNICO_PRODUCTO.md
├── README.md                 # Este archivo
└── PINOUT.txt
```

---

## 🐛 Troubleshooting

### Drum machine no arranca

```bash
sudo journalctl -u drummachine -n 50
sudo systemctl status drummachine
```

### Audio no sale

```bash
# Verificar dispositivos de salida
aplay -l

# Probar audio
speaker-test -t wav -c 2
```

### Bluetooth no conecta

```bash
# Reiniciar servicio Bluetooth
sudo systemctl restart bluetooth

# Emparejamiento manual
bluetoothctl
> scan on
> pair [MAC]
> connect [MAC]
```

**Más soluciones en:** `INFORME_TECNICO_PRODUCTO.md` sección Troubleshooting

---

## 🎓 Desarrollo

**Metodología:** Planificación → Acción → Commit → Documentación

**Próximas mejoras planificadas:**
- Sample editor integrado
- Pattern chaining (secuenciar patrones)
- Grabación de sesiones
- Efectos por instrumento

Ver **`PLAN_REORGANIZACION.md`** para roadmap completo.

---

## 📜 Licencia

Proyecto de código abierto educativo - IPS 6to Electro 2025

**Autores:** Enzo Saldivia y Joaquín Aguerreberry

---

## 🙏 Créditos

- Plataforma: Raspberry Pi 3 B+
- Audio: pygame, numpy
- Hardware: RPi.GPIO, spidev
- Samples: No incluidos (usar fuentes gratuitas)

**Fuentes recomendadas de samples:**
- [Freesound.org](https://freesound.org)
- [99Sounds.org](https://99sounds.org)
- [Samples.kb6.de](http://samples.kb6.de)

---

**¡Disfruta tu Drum Machine!** 🥁🎶

Para documentación técnica completa: **`INFORME_TECNICO_PRODUCTO.md`**
