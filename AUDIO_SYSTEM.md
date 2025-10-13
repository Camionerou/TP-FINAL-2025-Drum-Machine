# 🔊 Sistema de Audio Profesional

## Arquitectura

```
Sample WAV → AudioEngine → AudioProcessor → Limitador Suave → Output
              ↓              ↓                ↓
           Volume      Ganancia Master    Previene Distorsión
```

---

## 🎚️ AudioProcessor

### Características Implementadas

**1. Procesamiento en Tiempo Real**
- Convierte samples a arrays numpy
- Aplica ganancia sin límites
- Usa limitador suave (tanh) en lugar de hard clipping

**2. Ganancia Master Sin Límites**
```python
AUDIO_GAIN_BOOST = 2.0  # Puede ser cualquier valor
```
- Ya no limitado a 1.0
- Puede amplificar mucho más
- El limitador previene distorsión

**3. Limitador Suave (Soft Limiter)**
```python
limited = np.tanh(audio_data / threshold) * threshold
```
- Más musical que hard clipping
- Compresión suave en niveles altos
- Evita distorsión áspera

**4. Volúmenes Extendidos**
- Master: 0.0 - 2.0 (antes limitado a 1.0)
- Instrumentos: 0.0 - 2.0
- Combinado con gain boost = mucho más rango

---

## 🎛️ Cadena de Ganancia

```
Volumen Final = Instrumento × Master × Gain Boost
                   (0-2.0)    (0-2.0)    (2.0)

Ejemplo máximo: 2.0 × 2.0 × 2.0 = 8.0x
```

Luego pasa por el limitador suave que previene distorsión.

---

## 🔧 Configuración Actual

```python
# config.py
MASTER_VOLUME_DEFAULT = 1.0
AUDIO_GAIN_BOOST = 2.0

# Inicialización (main.py)
- Todos los instrumentos al 100%
- Master volume al 100%
- Resultado: Volumen máximo al iniciar
```

---

## 🚀 Futuros Efectos Posibles

Con esta base, ahora es fácil agregar:

### Efectos de Audio
- [ ] **Reverb** (convolución)
- [ ] **Delay/Echo** (buffer circular)
- [ ] **Distorsión** (wave shaping)
- [ ] **Filtros** (low-pass, high-pass, band-pass)
- [ ] **Compresión** (dynamic range)
- [ ] **EQ** (ecualizador de bandas)

### Procesamiento Avanzado
- [ ] **Pitch shifting** (cambiar tono)
- [ ] **Time stretching** (cambiar duración sin afectar tono)
- [ ] **Bit crushing** (reducción de bits para efecto lo-fi)
- [ ] **Ring modulation** (modulación)

### Efectos por Instrumento
- [ ] **Kick**: Sub-bass boost
- [ ] **Snare**: Compresión + reverb corto
- [ ] **Hi-Hats**: High-pass filter
- [ ] **Toms**: Pitch envelope
- [ ] **Cymbals**: Reverb largo

---

## 🎯 Cómo Agregar un Efecto

```python
# En audio_processor.py

def apply_reverb(self, audio_data, room_size=0.5):
    """Aplicar reverb simple"""
    # Implementación de reverb
    pass

def apply_filter(self, audio_data, cutoff=1000, filter_type='lowpass'):
    """Aplicar filtro"""
    # Implementación de filtro
    pass

# En audio_engine.py

def play_sample(self, instrument_id, volume=None, reverb=0, filter_cutoff=None):
    # Procesar con efectos
    processed = self.processor.process_sample(...)
    if reverb > 0:
        processed = self.processor.apply_reverb(processed, reverb)
    # etc...
```

---

## 📊 Ventajas del Sistema

✅ **Ganancia real** sin límite artificial  
✅ **Limitador musical** (tanh en vez de clip)  
✅ **Procesamiento numpy** (rápido y eficiente)  
✅ **Base extensible** para efectos futuros  
✅ **Fallback automático** si procesamiento falla  
✅ **Control fino** de volumen  

---

## 🔊 Ajustes Disponibles

### En `config.py`:
```python
AUDIO_GAIN_BOOST = 2.0    # Aumenta para más volumen (3.0, 4.0, etc.)
```

### En `audio_processor.py`:
```python
self.limiter_threshold = 0.95  # Threshold del limitador (0.8-0.99)
self.limiter_enabled = True    # Activar/desactivar limitador
```

### En código:
```python
# Cambiar ganancia master en tiempo real
audio_engine.processor.set_master_gain(3.0)

# Ajustar threshold del limitador
audio_engine.processor.set_limiter_threshold(0.9)
```

---

## 🎵 Próximos Pasos Sugeridos

1. **Aumentar `AUDIO_GAIN_BOOST`** si todavía está bajo
2. **Agregar potenciómetro de ganancia** (usar pot libre)
3. **Implementar reverb** para cymbals
4. **Agregar compresión** para kick/snare

---

¡Sistema de audio profesional listo para expandir! 🔊🎛️

