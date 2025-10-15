#!/usr/bin/env python3
"""
Script para normalizar/amplificar samples de audio
Aumenta el volumen de los WAV sin distorsión
"""

import os
import wave
import struct

def normalize_wav(input_path, output_path, target_amplitude=0.9):
    """
    Normalizar un archivo WAV
    
    Args:
        input_path: Ruta del WAV original
        output_path: Ruta del WAV normalizado
        target_amplitude: Amplitud objetivo (0.0-1.0), 0.9 = 90% del máximo
    """
    print(f"Normalizando: {input_path}")
    
    # Abrir WAV original
    with wave.open(input_path, 'rb') as wav_in:
        # Obtener parámetros
        params = wav_in.getparams()
        n_channels = params.nchannels
        sampwidth = params.sampwidth
        framerate = params.framerate
        n_frames = params.nframes
        
        # Leer todos los frames
        frames = wav_in.readframes(n_frames)
    
    # Convertir a lista de samples
    if sampwidth == 1:
        samples = struct.unpack(f'{n_frames * n_channels}B', frames)
        samples = [(s - 128) / 128.0 for s in samples]  # Normalizar a -1.0 a 1.0
    elif sampwidth == 2:
        samples = struct.unpack(f'{n_frames * n_channels}h', frames)
        samples = [s / 32768.0 for s in samples]
    else:
        print(f"  Advertencia: Formato no soportado (sampwidth={sampwidth})")
        return False
    
    # Encontrar amplitud máxima
    max_amplitude = max(abs(s) for s in samples)
    
    if max_amplitude == 0:
        print(f"  Advertencia: Sample silencioso")
        return False
    
    # Calcular factor de normalización
    normalization_factor = target_amplitude / max_amplitude
    
    print(f"  - Amplitud original: {max_amplitude:.3f}")
    print(f"  - Factor de normalización: {normalization_factor:.2f}x")
    
    # Normalizar samples
    normalized = [s * normalization_factor for s in samples]
    
    # Convertir de vuelta a bytes
    if sampwidth == 2:
        normalized_int = [int(s * 32767) for s in normalized]
        normalized_int = [max(-32768, min(32767, s)) for s in normalized_int]  # Clipping
        frames_out = struct.pack(f'{len(normalized_int)}h', *normalized_int)
    else:
        normalized_int = [int((s + 1.0) * 128) for s in normalized]
        normalized_int = [max(0, min(255, s)) for s in normalized_int]
        frames_out = struct.pack(f'{len(normalized_int)}B', *normalized_int)
    
    # Guardar WAV normalizado
    with wave.open(output_path, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(frames_out)
    
    print(f"  ✓ Guardado: {output_path}")
    return True

def main():
    """Normalizar todos los samples"""
    print("=" * 60)
    print("  NORMALIZACIÓN DE SAMPLES")
    print("=" * 60)
    print()
    
    samples_dir = 'samples'
    backup_dir = 'samples/backup_original'
    
    # Crear backup
    os.makedirs(backup_dir, exist_ok=True)
    
    instruments = ['kick', 'snare', 'chh', 'ohh', 'tom1', 'tom2', 'crash', 'ride']
    
    for instrument in instruments:
        input_path = os.path.join(samples_dir, f'{instrument}.wav')
        backup_path = os.path.join(backup_dir, f'{instrument}.wav')
        output_path = input_path  # Sobrescribir el original
        temp_path = input_path + '.tmp'
        
        if not os.path.exists(input_path):
            print(f"✗ No encontrado: {input_path}")
            continue
        
        # Hacer backup si no existe
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(input_path, backup_path)
            print(f"  Backup creado: {backup_path}")
        
        # Normalizar
        if normalize_wav(input_path, temp_path, target_amplitude=0.95):
            # Reemplazar original
            os.replace(temp_path, output_path)
            print(f"  ✓ {instrument}.wav normalizado\n")
        else:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"  ✗ Error normalizando {instrument}.wav\n")
    
    print("=" * 60)
    print("  NORMALIZACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("Los samples originales están en: samples/backup_original/")
    print("Los samples normalizados reemplazaron los originales")
    print()

if __name__ == "__main__":
    main()

