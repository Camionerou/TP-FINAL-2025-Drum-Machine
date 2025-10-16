#!/usr/bin/env python3
"""
Script de diagnóstico para botones en Raspberry Pi
Muestra estado de botones en tiempo real para debug
"""

import sys
import time
sys.path.append('.')

from core.drum_machine import DrumMachine

def diagnose_buttons():
    """Diagnosticar detección de botones"""
    print("🔍 Diagnóstico de botones - Presiona botones para probar")
    print("Hold BTN 12 (1s): Effects, Hold BTN 15 (2s): Bluetooth")
    print("Ctrl+C para salir")
    
    dm = DrumMachine()
    
    try:
        while True:
            # Escanear botones
            pressed_buttons = dm.button_matrix.scan()
            
            # Actualizar handler
            dm.button_handler.update(pressed_buttons)
            
            # Mostrar estado cada segundo
            if pressed_buttons:
                print(f"🔘 Botones: {pressed_buttons}")
            
            time.sleep(0.1)  # 10 FPS
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo diagnóstico...")
    
    finally:
        dm.cleanup()

if __name__ == "__main__":
    diagnose_buttons()
