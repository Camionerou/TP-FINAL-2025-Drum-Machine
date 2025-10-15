#!/usr/bin/env python3
"""
Script simple para probar el display y verificar letras
"""

import time
from hardware.led_matrix import LEDMatrix

print("Probando display LED...")
matrix = LEDMatrix()

# Test 1: Patrón simple
print("Test 1: Línea horizontal")
matrix.clear()
for x in range(32):
    matrix.set_pixel(x, 3, True)
matrix.update()
time.sleep(2)

# Test 2: Línea vertical
print("Test 2: Línea vertical")
matrix.clear()
for y in range(8):
    matrix.set_pixel(15, y, True)
matrix.update()
time.sleep(2)

# Test 3: Vista BPM
print("Test 3: Vista BPM")
matrix.draw_bpm_view(120)
time.sleep(3)

# Test 4: Números simples
print("Test 4: Números 0-9")
matrix.clear()
for i in range(10):
    matrix._draw_number(i, i * 3, 2)
matrix.update()
time.sleep(3)

matrix.cleanup()
print("Test completado")

