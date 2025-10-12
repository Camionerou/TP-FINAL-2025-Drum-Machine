# 🎨 Guía del Sistema de Vistas Dinámicas

## Descripción General

La Drum Machine v2.0 incluye un sistema de vistas dinámicas que usa **toda la matriz LED 8x32** para mostrar información relevante. Las vistas cambian automáticamente cuando ajustas parámetros y vuelven al secuenciador después de 2 segundos.

---

## 🖥️ Vistas Disponibles

### 1. Vista SEQUENCER (Principal)
**Siempre activa** cuando no hay otra vista temporal.

```
┌────────────────────────────────────────────────┐
│ ▓░░░▓░░░░░▓░▓░░░░░▓░░░▓░░░░░▓░▓░░░▓░░░░░▓░░░ │  Kick
│ ░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░ │  Snare
│ ░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓░░░▓ │  CHH
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  OHH
│ ░░░░░░░░░░░░▓░░░░░░░░░░░░░░░░░░▓░░░░░░░░░░░░ │  Tom1
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓░░░░░░░░░░░ │  Tom2
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓░░░░░░░░░ │  Crash
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▓░ │  Ride
└────────────────────────────────────────────────┘
  0    4    8   12   16   20   24   28   31

▓ = Nota activa
█ = Paso actual (reproduciéndose)
░ = Paso seleccionado para edición (POT_SCROLL)
```

**Características:**
- Muestra **32 pasos completos** × 8 instrumentos
- Paso actual (playhead) se ilumina completamente durante reproducción
- Paso seleccionado (POT_SCROLL) tiene brillo diferente
- Edición en tiempo real mientras reproduce

---

### 2. Vista BPM
**Se activa** al girar POT_TEMPO (Pot 1).

```
┌────────────────────────────────────────────────┐
│  ▓▓   ▓▓▓   ▓   ▓                              │
│  ▓▓   ▓▓▓   ▓▓ ▓▓                              │  Texto "BPM"
│  ▓▓▓  ▓▓▓   ▓▓▓▓▓                              │
│  ▓▓▓  ▓▓    ▓▓▓▓▓                              │
│  ▓▓▓  ▓▓▓   ▓ ▓ ▓                              │
│                                                 │
│ ▓██████████████████████▓                       │  Barra de tempo
│ ▓██████████████████████▓                       │  (más larga = más rápido)
└────────────────────────────────────────────────┘
```

**Características:**
- Barra gráfica del tempo (1-31 LEDs)
- Indicadores pulsantes en los extremos al beat
- Duración: 2 segundos → vuelve a SEQUENCER

---

### 3. Vista VOLUMEN
**Se activa** al girar POT_MASTER o POT_VOL_* (Pots 3-7).

```
┌────────────────────────────────────────────────┐
│ ████████ ║ ████ ████ ███ ████                 │
│ ████████ ║ ████ ████ ███ ████                 │
│ ████████ ║ ████ ████ ███ ████                 │  Barras de volumen
│ ████████ ║ ████ ████ ███ ████                 │
│ ████████ ║ ████ ████ ███ ████                 │  Altura = nivel
│ ████████ ║ ████ ████ ███ ████                 │
│ ████████ ║ ████ ████ ███ ████                 │
│ ████████ ║ ████ ████ ███ ████                 │
└────────────────────────────────────────────────┘
  MASTER    DRUMS HATS TOMS CYMS
```

**Barras:**
- **Master**: Columnas 0-7 (volumen general)
- **Drums**: Kick + Snare
- **Hats**: CHH + OHH
- **Toms**: Tom1 + Tom2
- **Cyms**: Crash + Ride

---

### 4. Vista SWING
**Se activa** al girar POT_SWING (Pot 2).

```
┌────────────────────────────────────────────────┐
│  ▓▓▓▓                                           │
│  ▓       "SWING"                                │
│  ▓▓▓▓                                           │
│     ▓                                           │
│  ▓▓▓▓                                           │
│                                                 │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓               │  Línea base
│ ██████████████████████████████████              │  % Swing
└────────────────────────────────────────────────┘
```

**Características:**
- Línea recta = sin swing (0%)
- Onda sinusoidal = con swing (más curvada = más swing)
- Barra inferior muestra porcentaje (0-75%)

---

### 5. Vista PATTERN
**Se activa** al presionar BTN_PATTERN_PREV/NEXT (Botones 10/11).

```
┌────────────────────────────────────────────────┐
│ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓                │  Borde decorativo
│               ▓▓▓▓                              │
│              ▓    ▓                             │  Número grande
│             ▓     ▓                             │  del patrón (1-8)
│                   ▓                             │
│                  ▓                              │
│                 ▓                               │
│ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓                │  Borde decorativo
└────────────────────────────────────────────────┘
```

**Características:**
- Muestra número de patrón actual (1-8)
- Borde animado
- Duración: 1.5 segundos

---

### 6. Vista SAVE
**Se activa** al presionar BTN_SAVE (Botón 13).

```
Fase 1 (Guardando):
┌────────────────────────────────────────────────┐
│                 ░░░░░░░░░                       │
│              ░░░░░    ░░░░░░                    │
│           ░░░░           ░░░░░                  │  Ondas expandiéndose
│         ░░░                 ░░░                 │  desde el centro
│           ░░░           ░░░░░                   │
│              ░░░░░    ░░░░░░                    │
│                 ░░░░░░░░░                       │
└────────────────────────────────────────────────┘

Fase 2 (Confirmación):
┌────────────────────────────────────────────────┐
│                                                 │
│             ▓                                   │
│              ▓                                  │
│               ▓     ▓                           │  Checkmark ✓
│                ▓   ▓                            │
│                 ▓ ▓                             │
│                  ▓                              │
└────────────────────────────────────────────────┘
```

**Características:**
- Animación de ondas expandiéndose
- Checkmark final de confirmación
- Duración: 1.5 segundos

---

### 7. Vista PAD
**Se activa** al tocar un instrumento en modo PAD.

```
┌────────────────────────────────────────────────┐
│ ▓▓▓                                         ▓▓▓ │  Efecto de pulso
│ ▓▓▓            ▓  ▓                         ▓▓▓ │
│ ▓▓▓            ▓▓                           ▓▓▓ │
│                ▓▓▓                              │  Primera letra
│                ▓▓▓                              │  del instrumento
│                ▓ ▓▓                             │  (K, S, C, O, T, R)
│                ▓  ▓▓                            │
│ ▓▓▓            ▓   ▓▓                       ▓▓▓ │  Efecto de pulso
└────────────────────────────────────────────────┘
```

**Características:**
- Muestra letra del instrumento tocado
- Efecto pulsante en las esquinas
- Duración: 1 segundo

---

## 🎮 Controles del Sistema

### Potenciómetros

| Pot | Función | Vista Activada |
|-----|---------|----------------|
| 0 | **Scroll Pasos** (0-31) | Ninguna (actualiza SEQUENCER) |
| 1 | **Tempo** (60-200 BPM) | Vista BPM |
| 2 | **Swing** (0-75%) | Vista SWING |
| 3 | **Master Volume** | Vista VOLUMEN |
| 4 | **Vol Drums** (Kick + Snare) | Vista VOLUMEN |
| 5 | **Vol Hats** (CHH + OHH) | Vista VOLUMEN |
| 6 | **Vol Toms** (Tom1 + Tom2) | Vista VOLUMEN |
| 7 | **Vol Cyms** (Crash + Ride) | Vista VOLUMEN |

### Botones

| Botón | Función Simple | Doble-Click | Hold |
|-------|---------------|-------------|------|
| 1-8 | **Instrumento** | - | + otro = operaciones |
| 9 | **Play/Stop** | Reset a paso 0 | - |
| 10 | **Cambiar Modo** | - | Bloquear modo (2s) |
| 11 | **Patrón -** | - | Desplazamiento rápido |
| 12 | **Patrón +** | - | Desplazamiento rápido |
| 13 | **Clear paso** | Clear instrumento | Clear todo (3s) |
| 14 | **Guardar** | - | + 11/12 = guardar en patrón específico |
| 15 | **Copiar paso** | - | + 11/12 = pegar |
| 16 | **Mute** | - | + 1-8 = mute global |

---

## 💡 Flujo de Trabajo

### Crear un Ritmo (Modo Sequencer)

1. Asegúrate de estar en **Modo SEQUENCER** (LED Verde encendido)
2. Gira **Pot 0** para seleccionar un paso (0-31)
   - El paso seleccionado se resalta en el display
3. Presiona **Botones 1-8** para activar/desactivar instrumentos en ese paso
4. Repite para construir tu patrón
5. Presiona **Botón 9** para reproducir
6. Ajusta **tempo**, **swing** y **volúmenes** con los pots
   - Las vistas aparecerán automáticamente
7. Presiona **Botón 14** para guardar

### Tocar en Tiempo Real (Modo Pad)

1. Presiona **Botón 10** para cambiar a **Modo PAD** (LED Rojo encendido)
2. Presiona **Botones 1-8** para tocar instrumentos
   - La vista PAD mostrará cada instrumento tocado
3. Ajusta volúmenes en tiempo real con los pots

### Operaciones Avanzadas

**Copiar/Pegar Pasos:**
1. Selecciona paso con **Pot 0**
2. Presiona **Botón 15** (Copy)
3. Mantén **Botón 15** y presiona **Botón 11/12** para navegar y pegar

**Clear Selectivo:**
- **Click simple Botón 13**: Limpia paso actual
- **Doble-click Botón 13** + **Botón 1-8**: Limpia instrumento en todos los pasos
- **Hold 3s Botón 13**: Limpia patrón completo

**Guardar en Patrón Específico:**
1. Mantén **Botón 14** (Save)
2. Presiona **Botón 11** (patrón anterior) o **Botón 12** (patrón siguiente)

---

## 🎨 Consejos de Uso

1. **Las vistas son temporales**: No interrumpen tu workflow, vuelven automáticamente
2. **Edita mientras reproduce**: Puedes ajustar el patrón sin detener la reproducción
3. **Scroll independiente**: POT_SCROLL no afecta el playhead durante reproducción
4. **Feedback visual**: Cada acción tiene respuesta visual inmediata
5. **LEDs indicadores**: Mantienen información persistente sobre modo y estado

---

## 🔧 Timing de Vistas

- **Vista BPM/SWING/VOLUMEN**: 2 segundos
- **Vista PATTERN**: 1.5 segundos
- **Vista SAVE**: 1.5 segundos (con animación)
- **Vista PAD**: 1 segundo
- **Inactividad**: 3 segundos sin input → forzar vista SEQUENCER

---

¡Disfruta del sistema de vistas dinámicas! 🥁🎨

