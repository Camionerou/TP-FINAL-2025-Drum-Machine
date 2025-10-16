#!/usr/bin/env python3
"""
Script de diagnóstico para detección de botones
Verifica que los botones se detecten correctamente en Raspberry Pi
"""

import sys
import time
sys.path.append('.')

try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO disponible - Ejecutándose en Raspberry Pi")
    REAL_HARDWARE = True
except ImportError:
    print("⚠️ RPi.GPIO no disponible - Modo mock")
    REAL_HARDWARE = False

from core.config import BUTTON_ROWS, BUTTON_COLS

def test_button_matrix():
    """Probar matriz de botones"""
    print(f"\n🔧 Configuración:")
    print(f"Filas: {BUTTON_ROWS}")
    print(f"Columnas: {BUTTON_COLS}")
    
    if REAL_HARDWARE:
        # Configurar GPIO
        GPIO.setmode(GPIO.BCM)
        
        # Configurar filas como salidas
        for row in BUTTON_ROWS:
            GPIO.setup(row, GPIO.OUT)
            GPIO.output(row, GPIO.HIGH)  # Inicialmente HIGH
        
        # Configurar columnas como entradas con pull-up
        for col in BUTTON_COLS:
            GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print("✅ GPIO configurado")
        
        print("\n🎮 Presiona botones para probar (Ctrl+C para salir):")
        print("Botones 0-15 corresponden a:")
        print("0-3: Primera fila, 4-7: Segunda fila, 8-11: Tercera fila, 12-15: Cuarta fila")
        
        try:
            while True:
                pressed_buttons = []
                
                for row_idx, row_pin in enumerate(BUTTON_ROWS):
                    # Activar fila actual (LOW)
                    GPIO.output(row_pin, GPIO.LOW)
                    
                    # Pequeño delay para estabilización
                    time.sleep(0.001)
                    
                    # Leer columnas
                    for col_idx, col_pin in enumerate(BUTTON_COLS):
                        button_id = row_idx * len(BUTTON_COLS) + col_idx
                        
                        # Si columna está LOW, botón está presionado
                        if GPIO.input(col_pin) == GPIO.LOW:
                            pressed_buttons.append(button_id)
                    
                    # Desactivar fila (HIGH)
                    GPIO.output(row_pin, GPIO.HIGH)
                
                if pressed_buttons:
                    print(f"Botones presionados: {pressed_buttons}")
                
                time.sleep(0.1)  # 10 FPS
                
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo...")
        
        finally:
            GPIO.cleanup()
            print("✅ GPIO limpiado")
    
    else:
        print("\n⚠️ No se puede probar hardware real fuera de Raspberry Pi")
        print("Este script debe ejecutarse en la Raspberry Pi para probar botones reales")

if __name__ == "__main__":
    test_button_matrix()
