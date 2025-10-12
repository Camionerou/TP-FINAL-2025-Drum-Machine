# Samples de Audio

Este directorio debe contener los samples de batería en formato WAV.

## Archivos Necesarios

Coloca los siguientes archivos aquí:

- `kick.wav` - Bombo
- `snare.wav` - Redoblante
- `chh.wav` - Hi-Hat cerrado
- `ohh.wav` - Hi-Hat abierto
- `tom1.wav` - Tom 1 (agudo)
- `tom2.wav` - Tom 2 (grave)
- `crash.wav` - Crash cymbal
- `ride.wav` - Ride cymbal

## Especificaciones Recomendadas

- **Formato**: WAV
- **Sample Rate**: 44.1 kHz
- **Bit Depth**: 16-bit
- **Canales**: Mono
- **Duración**: 0.5 - 2 segundos

## Dónde Conseguir Samples Gratuitos

### Sitios Recomendados

1. **Freesound.org**
   - https://freesound.org
   - Samples gratuitos con diversas licencias
   - Buscar: "drum samples", "808", "909"

2. **99Sounds**
   - https://99sounds.org
   - Packs de samples gratuitos de alta calidad

3. **Sample Focus**
   - https://samplefocus.com
   - Gran variedad de samples de batería

4. **Reverb Drum Machines**
   - Samples de drum machines clásicas (TR-808, TR-909)

5. **LANDR Samples**
   - https://samples.landr.com
   - Algunos samples gratuitos disponibles

### Kits de Batería Recomendados

- TR-808 samples (clásico)
- TR-909 samples (house/techno)
- Acoustic drum samples (más orgánico)
- Electronic samples (synthético)

## Conversión de Formato

Si tienes samples en otros formatos, puedes convertirlos usando:

```bash
# Con ffmpeg
ffmpeg -i input.mp3 -ar 44100 -ac 1 -sample_fmt s16 output.wav

# Con sox
sox input.mp3 -r 44100 -c 1 -b 16 output.wav
```

## Optimización

Para mejor rendimiento:
1. Mantén los samples cortos (< 2 segundos)
2. Normaliza el volumen
3. Elimina silencio al inicio y final
4. Usa mono en lugar de stereo

## Licencias

⚠️ **Importante**: Asegúrate de tener los derechos o licencia apropiada para usar los samples, especialmente si planeas distribuir tu proyecto.

## Ejemplo de Descarga

Para obtener un pack básico de 808:

1. Ve a Freesound.org
2. Busca "TR-808" o "808 drum"
3. Descarga samples individuales
4. Renombra según los nombres requeridos arriba
5. Coloca en este directorio

