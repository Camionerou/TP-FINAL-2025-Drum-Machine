#!/usr/bin/env python3
"""
Script de prueba para funciones hold
Simula presión de botones para probar hold functions
"""

import sys
import time
sys.path.append('.')

from core.drum_machine import DrumMachine
from hardware.button_matrix import GPIO

def test_hold_functions():
    """Probar funciones hold con simulación"""
    print("🧪 Probando funciones hold...")
    
    # Inicializar drum machine
    dm = DrumMachine()
    print("✅ DrumMachine inicializado")
    
    # Test 1: Hold BTN 12 (EFFECTS) - 1 segundo
    print("\n🎛️ Test 1: Hold BTN 12 (EFFECTS) por 1.5s...")
    
    # Simular presión de BTN 12
    GPIO.mock_press_button(12)
    
    # Simular múltiples scans durante 1.5 segundos
    start_time = time.time()
    while time.time() - start_time < 1.5:
        pressed = dm.button_matrix.scan()
        dm.button_handler.update(pressed)
        time.sleep(0.05)  # 20 FPS
    
    # Liberar botón
    GPIO.mock_release_button(12)
    dm.button_handler.update(dm.button_matrix.scan())
    
    print("✅ Test EFFECTS completado")
    
    # Test 2: Hold BTN 15 (Bluetooth) - 2 segundos
    print("\n🔌 Test 2: Hold BTN 15 (Bluetooth) por 2.5s...")
    
    # Simular presión de BTN 15
    GPIO.mock_press_button(15)
    
    # Simular múltiples scans durante 2.5 segundos
    start_time = time.time()
    while time.time() - start_time < 2.5:
        pressed = dm.button_matrix.scan()
        dm.button_handler.update(pressed)
        time.sleep(0.05)  # 20 FPS
    
    # Liberar botón
    GPIO.mock_release_button(15)
    dm.button_handler.update(dm.button_matrix.scan())
    
    print("✅ Test Bluetooth completado")
    
    # Test 3: Hold BTN 12 por 3.5s (Clear completo)
    print("\n🗑️ Test 3: Hold BTN 12 (Clear completo) por 3.5s...")
    
    # Simular presión de BTN 12
    GPIO.mock_press_button(12)
    
    # Simular múltiples scans durante 3.5 segundos
    start_time = time.time()
    while time.time() - start_time < 3.5:
        pressed = dm.button_matrix.scan()
        dm.button_handler.update(pressed)
        time.sleep(0.05)  # 20 FPS
    
    # Liberar botón
    GPIO.mock_release_button(12)
    dm.button_handler.update(dm.button_matrix.scan())
    
    print("✅ Test Clear completo completado")
    
    # Cleanup
    dm.cleanup()
    print("\n✅ Todos los tests completados")

if __name__ == "__main__":
    test_hold_functions()
