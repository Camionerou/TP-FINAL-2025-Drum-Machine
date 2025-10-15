"""
Splash screen para mostrar durante la inicialización
Muestra animación de carga en el display LED
"""

def show_splash(led_matrix):
    """
    Mostrar splash screen mientras carga el sistema
    
    Args:
        led_matrix: Instancia de LEDMatrix
    """
    # Limpiar display
    led_matrix.clear()
    
    # Animación simple de carga
    # Texto "DRUM" en el centro
    drum_pattern = [
        [0,1,1,1,0,0,1,1,1,0,0,1,0,0,1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,1,0,1,1,1,0,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,0,0,1,0,0,1,0,0,1,1,0,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
    ]
    
    # Centrar verticalmente (8 filas, usar 3 filas en blanco arriba)
    for row_idx, row_data in enumerate(drum_pattern):
        for col_idx, pixel in enumerate(row_data):
            if pixel:
                led_matrix.set_pixel(row_idx + 2, col_idx, True)
    
    # Barra de progreso en la fila 7
    for i in range(32):
        led_matrix.set_pixel(7, i, True)
        led_matrix.display()
        import time
        time.sleep(0.02)  # 640ms total
    
    led_matrix.display()

def show_loading_bar(led_matrix, progress, max_progress):
    """
    Actualizar barra de progreso durante carga
    
    Args:
        led_matrix: Instancia de LEDMatrix
        progress: Progreso actual (0-max_progress)
        max_progress: Máximo progreso
    """
    # Calcular porcentaje
    percentage = int((progress / max_progress) * 32)
    
    # Actualizar barra (fila 7)
    for i in range(32):
        led_matrix.set_pixel(7, i, i < percentage)
    
    led_matrix.display()

