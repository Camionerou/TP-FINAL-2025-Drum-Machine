#!/usr/bin/env python3
"""
Script de prueba de hardware para Raspberry Pi Drum Machine
Útil para verificar que todos los componentes estén conectados correctamente
"""

import time
import sys

print("=" * 60)
print("  TEST DE HARDWARE - RASPBERRY PI DRUM MACHINE")
print("=" * 60)
print()

# Test 1: Importar módulos
print("[1/6] Probando importación de módulos...")
try:
    from core.config import *
    from core.audio_engine import AudioEngine
    from core.sequencer import Sequencer
    from hardware import ButtonMatrix, LEDMatrix, ADCReader, LEDController
    print("✓ Todos los módulos importados correctamente")
except Exception as e:
    print(f"✗ Error importando módulos: {e}")
    sys.exit(1)

print()

# Test 2: LEDs Indicadores
print("[2/6] Probando LEDs indicadores...")
try:
    led_controller = LEDController()
    print("  Encendiendo cada LED por 0.5 segundos...")
    
    leds = ['red', 'green', 'yellow', 'blue', 'white']
    for led in leds:
        print(f"    - LED {led}")
        led_controller.set_led(led, True)
        time.sleep(0.5)
        led_controller.set_led(led, False)
        time.sleep(0.2)
    
    print("✓ LEDs indicadores funcionando")
except Exception as e:
    print(f"✗ Error con LEDs: {e}")
    led_controller = None

print()

# Test 3: Display LED MAX7219
print("[3/6] Probando display LED MAX7219...")
try:
    led_matrix = LEDMatrix()
    print("  Patrón de prueba...")
    led_matrix.test_pattern()
    time.sleep(2)
    
    print("  Llenando display...")
    led_matrix.fill()
    time.sleep(1)
    
    print("  Limpiando display...")
    led_matrix.clear()
    time.sleep(0.5)
    
    print("✓ Display LED funcionando")
except Exception as e:
    print(f"✗ Error con display LED: {e}")
    led_matrix = None

print()

# Test 4: ADC MCP3008
print("[4/6] Probando ADC MCP3008 (potenciómetros)...")
try:
    adc_reader = ADCReader()
    print("  Leyendo todos los canales (ajusta los pots para ver cambios)...")
    
    for i in range(3):
        values = adc_reader.read_all_channels()
        print(f"  Lectura {i+1}:")
        for ch, val in enumerate(values):
            bar_length = int(val * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"    CH{ch}: {bar} {val:.2f}")
        time.sleep(1)
        print()
    
    print("✓ ADC funcionando")
except Exception as e:
    print(f"✗ Error con ADC: {e}")
    adc_reader = None

print()

# Test 5: Matriz de Botones
print("[5/6] Probando matriz de botones...")
print("  Presiona algunos botones (10 segundos)...")
print("  Presiona Ctrl+C para saltar este test")

try:
    button_count = [0]
    
    def on_button(btn_id):
        button_count[0] += 1
        print(f"  ✓ Botón {btn_id} presionado (total: {button_count[0]})")
    
    button_matrix = ButtonMatrix(on_button_press=on_button)
    
    start_time = time.time()
    while time.time() - start_time < 10:
        button_matrix.scan()
        time.sleep(0.01)
    
    if button_count[0] > 0:
        print(f"✓ Matriz de botones funcionando ({button_count[0]} pulsaciones detectadas)")
    else:
        print("⚠  No se detectaron pulsaciones (verifica conexiones)")
    
except KeyboardInterrupt:
    print("\n  Test de botones saltado")
    button_matrix = None
except Exception as e:
    print(f"✗ Error con matriz de botones: {e}")
    button_matrix = None

print()

# Test 6: Audio Engine
print("[6/6] Probando motor de audio...")
print("  (Verifica si hay samples en el directorio 'samples/')")
try:
    audio_engine = AudioEngine()
    
    # Probar cada instrumento
    print("  Probando instrumentos (si están disponibles)...")
    for i in range(NUM_INSTRUMENTS):
        if audio_engine.samples.get(i) is not None:
            print(f"    - Reproduciendo {INSTRUMENTS[i]}")
            audio_engine.play_sample(i)
            time.sleep(0.5)
        else:
            print(f"    ⚠ Sample {INSTRUMENTS[i]} no disponible")
    
    print("✓ Motor de audio funcionando")
except Exception as e:
    print(f"✗ Error con audio: {e}")
    audio_engine = None

print()

# Cleanup
print("Limpiando recursos...")
try:
    if led_controller:
        led_controller.cleanup()
    if led_matrix:
        led_matrix.cleanup()
    if adc_reader:
        adc_reader.cleanup()
    if button_matrix:
        button_matrix.cleanup()
    if audio_engine:
        audio_engine.cleanup()
except:
    pass

print()
print("=" * 60)
print("  TEST COMPLETADO")
print("=" * 60)
print()
print("Resumen:")
print("  - Si todos los tests pasaron (✓), el hardware está listo")
print("  - Si hay advertencias (⚠), verifica esas conexiones")
print("  - Si hay errores (✗), revisa las conexiones según README.md")
print()
print("¡Ya puedes ejecutar: python3 main.py")
print()

