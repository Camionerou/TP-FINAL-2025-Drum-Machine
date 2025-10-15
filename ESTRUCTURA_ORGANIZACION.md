# 📁 PLAN DE ORGANIZACIÓN DE CODEBASE

## Estructura Objetivo

```
DRUMMACHINE/
│
├── docs/                           # 📚 TODA LA DOCUMENTACIÓN
│   ├── INFORME_TECNICO_PRODUCTO.md
│   ├── PLAN_REORGANIZACION.md
│   ├── CHANGELOG_LIMPIEZA.md
│   └── PINOUT.txt
│
├── core/                           # 🎯 MÓDULOS PRINCIPALES
│   ├── __init__.py
│   ├── drum_machine.py            # main.py renombrado
│   ├── audio_engine.py
│   ├── audio_processor.py
│   ├── sequencer.py
│   └── config.py
│
├── ui/                             # 🖥️ INTERFAZ DE USUARIO
│   ├── __init__.py
│   ├── view_manager.py
│   ├── button_handler.py
│   └── splash_screen.py
│
├── features/                       # ✨ CARACTERÍSTICAS OPCIONALES
│   ├── __init__.py
│   ├── tap_tempo.py
│   ├── midi_handler.py
│   └── bluetooth_audio.py         # A crear
│
├── hardware/                       # 🔌 DRIVERS DE HARDWARE
│   ├── __init__.py
│   ├── button_matrix.py
│   ├── led_matrix.py
│   ├── adc_reader.py
│   └── led_controller.py
│
├── data/                           # 💾 DATOS DEL PROYECTO
│   ├── samples/                   # Samples de audio
│   │   ├── kick.wav
│   │   ├── snare.wav
│   │   └── ...
│   └── patterns/                  # Patrones guardados
│       └── pattern_1.json
│
├── scripts/                        # 🛠️ SCRIPTS DE INSTALACIÓN
│   ├── drummachine.service
│   ├── install_service.sh
│   └── optimize_boot.sh
│
├── main.py                         # 🚀 PUNTO DE ENTRADA
├── requirements.txt
└── README.md
```

## Mapeo de Archivos

### Archivos a MOVER:

```bash
# Documentación → docs/
INFORME_TECNICO_PRODUCTO.md  → docs/INFORME_TECNICO_PRODUCTO.md
PLAN_REORGANIZACION.md       → docs/PLAN_REORGANIZACION.md
CHANGELOG_LIMPIEZA.md        → docs/CHANGELOG_LIMPIEZA.md
COMMIT_MESSAGE.txt           → docs/COMMIT_MESSAGE.txt
PINOUT.txt                   → docs/PINOUT.txt

# Core → core/
audio_engine.py              → core/audio_engine.py
audio_processor.py           → core/audio_processor.py
sequencer.py                 → core/sequencer.py
config.py                    → core/config.py

# UI → ui/
view_manager.py              → ui/view_manager.py
button_handler.py            → ui/button_handler.py
splash_screen.py             → ui/splash_screen.py

# Features → features/
tap_tempo.py                 → features/tap_tempo.py
midi_handler.py              → features/midi_handler.py

# Hardware → hardware/ (ya existe)
# (mantener como está)

# Data → data/
samples/                     → data/samples/
patterns/                    → data/patterns/

# Scripts → scripts/
drummachine.service          → scripts/drummachine.service
install_service.sh           → scripts/install_service.sh
optimize_boot.sh             → scripts/optimize_boot.sh

# Raíz (mantener)
main.py                      → main.py (actualizar imports)
README.md                    → README.md
requirements.txt             → requirements.txt
```

### Archivos a ELIMINAR:

```bash
main_old.py                  # Backup viejo, ya no necesario
COMMIT_MESSAGE.txt           # Temporal, mover a docs/ y luego eliminar
```

## Archivos __init__.py a Crear

```python
# core/__init__.py
# ui/__init__.py
# features/__init__.py
# hardware/__init__.py (ya existe)
```

## main.py Actualizado

```python
#!/usr/bin/env python3
"""
Raspberry Pi Drum Machine v2.5
Punto de entrada principal
"""

from core.drum_machine import DrumMachine

if __name__ == "__main__":
    drum = DrumMachine()
    drum.run()
```

## Orden de Ejecución

1. Crear carpetas
2. Crear archivos __init__.py
3. Mover archivos
4. Actualizar imports en todos los módulos
5. Actualizar main.py
6. Probar que funciona
7. Commit
8. Actualizar documentación

