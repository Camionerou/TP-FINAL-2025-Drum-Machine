#!/usr/bin/env python3
"""
Script de prueba de audio para diagnosticar problemas
"""

import pygame
import os
import time

print("=" * 60)
print("  TEST DE AUDIO - DRUM MACHINE")
print("=" * 60)
print()

# Test 1: Inicializar pygame mixer
print("[1/5] Inicializando pygame mixer...")
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    print(f"✓ Mixer inicializado")
    print(f"  - Frequency: {pygame.mixer.get_init()[0]} Hz")
    print(f"  - Format: {pygame.mixer.get_init()[1]}")
    print(f"  - Channels: {pygame.mixer.get_init()[2]}")
except Exception as e:
    print(f"✗ Error inicializando mixer: {e}")
    exit(1)

print()

# Test 2: Verificar samples
print("[2/5] Verificando samples...")
samples_dir = 'samples'
required_samples = ['kick', 'snare', 'chh', 'ohh', 'tom1', 'tom2', 'crash', 'ride']

for sample_name in required_samples:
    sample_path = os.path.join(samples_dir, f"{sample_name}.wav")
    if os.path.exists(sample_path):
        size = os.path.getsize(sample_path)
        print(f"  ✓ {sample_name}.wav ({size} bytes)")
    else:
        print(f"  ✗ {sample_name}.wav NO ENCONTRADO")

print()

# Test 3: Cargar y reproducir un sample
print("[3/5] Cargando kick.wav...")
try:
    kick = pygame.mixer.Sound(os.path.join(samples_dir, 'kick.wav'))
    print(f"✓ Kick cargado correctamente")
    print(f"  - Duración: {kick.get_length():.2f} segundos")
    
    print("\n[4/5] Probando reproducción...")
    print("  Reproduciendo kick 3 veces...")
    for i in range(3):
        kick.set_volume(1.0)
        kick.play()
        print(f"    ♪ Kick {i+1}")
        time.sleep(0.5)
    
    print("\n✓ Reproducción completada")
    
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Test 4: Información del sistema de audio
print("[5/5] Información de audio del sistema:")
try:
    import subprocess
    
    # Verificar salida de audio (solo en Linux/RPi)
    try:
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        print(result.stdout)
    except:
        print("  (comando aplay no disponible - probablemente no estás en RPi)")
        print("  En Mac, el audio debería funcionar automáticamente")
        
except Exception as e:
    print(f"  Info: {e}")

print()
print("=" * 60)
print("  TEST COMPLETADO")
print("=" * 60)
print()
print("Si escuchaste los 3 kicks: ✓ Audio funcionando")
print("Si NO escuchaste nada:")
print("  - Verifica que tengas altavoces/audífonos conectados")
print("  - En RPi: sudo raspi-config → Advanced → Audio → Force 3.5mm")
print("  - Ajusta el volumen del sistema")
print("  - Prueba: speaker-test -t wav -c 2")
print()

pygame.mixer.quit()

