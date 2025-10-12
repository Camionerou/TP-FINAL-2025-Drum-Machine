<!-- 7dafe8fe-f33d-4e1e-8a25-e7486e24767b d5432785-0ac5-411b-9f1b-1aab15a40986 -->
# Plan: Sistema de Vistas Dinámicas para Drum Machine

## Arquitectura de Vistas

### Sistema de Vistas Automáticas

**Vista Principal:** SEQUENCER (32x8 LEDs)

- Muestra los 32 pasos completos × 8 instrumentos
- Playhead se mueve automáticamente durante reproducción
- Resalta el paso siendo editado (según scroll pot)

**Vistas Temporales** (aparecen 2-3 segundos al ajustar):

1. **Vista BPM**: Gráfico visual del tempo (60-200 BPM)
2. **Vista VOLUMEN**: Barras para Master + grupos de instrumentos
3. **Vista SWING**: Visualización del porcentaje de swing (0-75%)
4. **Vista PATTERN**: Muestra número de patrón actual (1-8)
5. **Vista SAVE**: Animación de guardado exitoso
6. **Vista PAD**: Muestra último instrumento tocado en modo PAD

**Transiciones:**

- Aparecen automáticamente al ajustar un parámetro
- Duración: 2 segundos
- Vuelven automáticamente a vista SEQUENCER
- Durante vista temporal, secuenciador sigue funcionando en background

## Configuración de Potenciómetros (Rediseño)

```python
POT_SCROLL = 0      # Scroll entre pasos 0-31 (selecciona paso a editar)
POT_TEMPO = 1       # BPM 60-200 → Trigger vista BPM
POT_SWING = 2       # Swing 0-75% → Trigger vista SWING
POT_MASTER = 3      # Volumen Master → Trigger vista VOLUMEN
POT_VOL_DRUMS = 4   # Vol Kick + Snare (grupo ritmo)
POT_VOL_HATS = 5    # Vol CHH + OHH (grupo hi-hats)
POT_VOL_TOMS = 6    # Vol Tom1 + Tom2 (grupo toms)
POT_VOL_CYMS = 7    # Vol Crash + Ride (grupo cymbals)
```

**Lógica de volúmenes grupales:**

- Pot4-7 ajustan sus respectivos grupos
- Al mover cualquiera → Trigger vista VOLUMEN mostrando todos

## Botones Rediseñados (16 botones)

### Botones 1-8: Instrumentos (Modo dependiente)

**Modo PAD:**

- Presionar: Toca el instrumento
- Trigger vista PAD mostrando instrumento

**Modo SEQUENCER:**

- Presionar: Toggle nota en paso actual (definido por POT_SCROLL)
- Mantener + otro botón: Operaciones especiales

### Botones 9-16: Funciones Inteligentes

**BTN 9: PLAY/STOP**

- Simple: Play/Stop secuenciador
- Doble click: Reiniciar a paso 0

**BTN 10: MODE (PAD ↔ SEQUENCER)**

- Simple: Cambiar modo
- Mantener 2s: Bloquear modo (no cambia accidentalmente)

**BTN 11: PATTERN -**

- Simple: Patrón anterior (1←8)
- Trigger vista PATTERN
- Mantener: Desplazamiento rápido

**BTN 12: PATTERN +**

- Simple: Patrón siguiente (1→8)
- Trigger vista PATTERN
- Mantener: Desplazamiento rápido

**BTN 13: CLEAR**

- Simple: Limpiar paso actual (según POT_SCROLL)
- Doble click: Limpiar instrumento en todos los pasos
- Mantener 3s: Limpiar patrón completo (con confirmación)

**BTN 14: SAVE**

- Simple: Guardar patrón actual
- Trigger vista SAVE con animación
- Mantener + BTN 11/12: Guardar en patrón específico

**BTN 15: COPY**

- Simple: Copiar paso actual
- Mantener + BTN 11/12: Navegar y pegar

**BTN 16: MUTE/SOLO**

- Simple: Silenciar instrumento en paso actual
- Doble click: Solo del instrumento
- Mantener + 1-8: Mute/unmute instrumento global

## Implementación del Sistema de Vistas

### Nuevo archivo: `view_manager.py`

```python
class ViewManager:
  - current_view: View enum
  - view_timeout: float
  - view_data: dict
    
    Vistas:
  - VIEW_SEQUENCER (default)
  - VIEW_BPM
  - VIEW_VOLUME
  - VIEW_SWING
  - VIEW_PATTERN
  - VIEW_SAVE
  - VIEW_PAD
    
    Métodos:
  - show_view(view_type, data, duration=2.0)
  - update() → Manejar timeouts
  - render(led_matrix) → Dibujar vista actual
```

### Renderizado por Vista

**Vista SEQUENCER (32x8):**

```
Matriz completa muestra 32 pasos × 8 instrumentos
LED encendido = nota activa
Columna parpadeante = paso actual (playhead)
Columna con brillo diferente = paso seleccionado (POT_SCROLL)
```

**Vista BPM:**

```
Row 0-3: Texto "BPM" estilizado
Row 4-7: Barra gráfica del tempo
        Más LEDs = más rápido
        Animación de pulso al beat
```

**Vista VOLUMEN:**

```
8 columnas, una por grupo:
Col 0-3: Master (altura = nivel)
Col 4-7: Grupos de instrumentos (4 barras)
```

**Vista SWING:**

```
Representación circular/onda del swing
0% = lineal
75% = máxima curvatura
```

**Vista PATTERN:**

```
Número grande del patrón (1-8)
LEDs formando el número
```

**Vista SAVE:**

```
Animación de "guardando":
- Efecto de ondas expandiéndose
- Checkmark final
- Duración: 1.5s
```

**Vista PAD:**

```
Nombre del instrumento + visualizador
Efecto de "golpe" visual
```

## Modificaciones a Archivos Existentes

### `config.py`

- Actualizar mapeo de potenciómetros
- Agregar constantes de vistas
- Agregar tiempos de transición
- Actualizar botones a 16 funciones

### `hardware/led_matrix.py`

- Optimizar `draw_sequencer_grid()` para 32 pasos
- Agregar métodos de renderizado por vista:
        - `draw_bpm_view(bpm)`
        - `draw_volume_view(volumes)`
        - `draw_swing_view(swing)`
        - `draw_pattern_view(pattern_num)`
        - `draw_save_animation(frame)`
        - `draw_pad_view(instrument_id)`
- Agregar sistema de animaciones

### `main.py`

- Integrar `ViewManager`
- Detectar cambios en potenciómetros → trigger vistas
- Sistema de detección de doble-click en botones
- Sistema de botón mantenido (hold)
- Actualizar mapeo de botones
- Lógica de combinaciones de botones

### `sequencer.py`

- Expandir de 16 a 32 pasos
- Actualizar `NUM_STEPS = 32`
- Mantener compatibilidad con patrones guardados

### `hardware/button_matrix.py`

- Agregar detección de doble-click
- Agregar detección de botón mantenido
- Agregar detección de combinaciones

## Nuevos Archivos

### `view_manager.py`

- Clase `ViewManager`
- Enum `ViewType`
- Sistema de timeouts
- Coordinación de renderizado

### `button_handler.py`

- Clase `ButtonHandler`
- Manejo de eventos:
        - Single press
        - Double click
        - Hold
        - Combinations
- Callbacks por tipo de evento

## Características Avanzadas

### Sistema de Scroll (POT_SCROLL)

```python
# POT_SCROLL define paso a editar (0-31)
current_edit_step = int(pot_value * 31)

# En vista secuenciador:
# - Resaltar paso siendo editado
# - Botones 1-8 modifican ese paso

# Durante reproducción:
# - Scroll no afecta playhead
# - Se puede editar mientras reproduce
```

### Detección Inteligente de Cambios

```python
# Solo trigger vista si cambio es significativo
if abs(new_bpm - old_bpm) > 2:
    view_manager.show_view(VIEW_BPM, {'bpm': new_bpm})

# Timer de inactividad
# Si no hay input por 3s → forzar vista SEQUENCER
```

### Feedback Visual Mejorado

- Animaciones suaves entre vistas
- Efectos de parpadeo para confirmaciones
- Indicadores de estado persistentes en LEDs externos

## Flujo de Trabajo Mejorado

### Edición de Secuencia

1. Girar POT_SCROLL para seleccionar paso (0-31)
2. Vista muestra paso seleccionado resaltado
3. Presionar botones 1-8 para toggle instrumentos en ese paso
4. Repetir para construir patrón

### Ajuste de Parámetros

1. Girar cualquier pot de control → Vista temporal aparece
2. Ver feedback visual en tiempo real
3. Después de 2s → Vuelve a secuenciador
4. Parámetro permanece ajustado

### Operaciones Avanzadas

- **Clear selectivo:** BTN13 limpia solo paso actual
- **Clear instrumento:** Doble-click BTN13 + BTN1-8
- **Copy/Paste:** BTN15 copia, mantener + navegar para pegar
- **Mute temporal:** BTN16 + BTN1-8 silencia instrumento

## Mejoras de UX

1. **Feedback inmediato:** Cada acción tiene respuesta visual
2. **Reversión automática:** Vistas temporales no interrumpen workflow
3. **Edición no destructiva:** Scroll y edición sin afectar reproducción
4. **Confirmaciones visuales:** Saves, clears, cambios de patrón
5. **Estados persistentes:** LEDs externos mantienen info de modo/estado

## Testing

Actualizar `test_hardware.py` para:

- Probar renderizado de cada vista
- Probar transiciones automáticas
- Probar detección de doble-click/hold
- Probar scroll de 32 pasos

### To-dos

- [ ] Crear estructura de directorios y archivos base del proyecto
- [ ] Implementar config.py con todas las constantes y pines GPIO
- [ ] Crear audio_engine.py con pygame para reproducir samples
- [ ] Implementar hardware/button_matrix.py para lectura de matriz 4x4
- [ ] Implementar hardware/led_matrix.py para control de MAX7219
- [ ] Implementar hardware/adc_reader.py para lectura de potenciómetros MCP3008
- [ ] Implementar hardware/led_controller.py para LEDs indicadores
- [ ] Crear sequencer.py con lógica de secuenciador de 16 pasos y guardado de patrones
- [ ] Implementar main.py con clase DrumMachine y loop principal integrando todos los componentes
- [ ] Crear README.md con documentación completa, diagramas de conexión y requirements.txt