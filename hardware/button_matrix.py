"""
Lectura de matriz de botones 4x4 con debouncing
"""

import time
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    # Mock para desarrollo fuera de Raspberry Pi
    print("Advertencia: RPi.GPIO no disponible, usando mock")
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        OUT = "OUT"
        PUD_UP = "PUD_UP"
        PUD_DOWN = "PUD_DOWN"
        HIGH = 1
        LOW = 0
        
        def __init__(self):
            self._mock_pressed_buttons = set()
            self._mock_press_time = 0
        
        def setmode(self, mode): pass
        def setup(self, pin, mode, pull_up_down=None): pass
        def input(self, pin): 
            # Simular botón presionado si está en el mock
            return self.LOW if pin in self._mock_pressed_buttons else self.HIGH
        def output(self, pin, state): pass
        def cleanup(self): pass
        
        def mock_press_button(self, button_id):
            """Simular presión de botón para testing"""
            self._mock_pressed_buttons.add(button_id)
        
        def mock_release_button(self, button_id):
            """Simular liberación de botón para testing"""
            self._mock_pressed_buttons.discard(button_id)
        
        def mock_release_all(self):
            """Simular liberación de todos los botones"""
            self._mock_pressed_buttons.clear()
    
    GPIO = MockGPIO()

from core.config import BUTTON_ROWS, BUTTON_COLS, DEBOUNCE_TIME


class ButtonMatrix:
    """Lector de matriz de botones 4x4"""
    
    def __init__(self, on_button_press=None):
        """
        Inicializar matriz de botones
        
        Args:
            on_button_press: Callback para eventos de botón (button_id)
        """
        self.rows = BUTTON_ROWS
        self.cols = BUTTON_COLS
        self.on_button_press = on_button_press
        
        # Estado de botones para debouncing
        self.button_states = [[False] * len(self.cols) for _ in range(len(self.rows))]
        self.last_press_time = [[0] * len(self.cols) for _ in range(len(self.rows))]
        
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Configurar pines GPIO para la matriz"""
        GPIO.setmode(GPIO.BCM)
        
        # Configurar filas como salidas (inicialmente HIGH)
        for row in self.rows:
            GPIO.setup(row, GPIO.OUT)
            GPIO.output(row, GPIO.HIGH)
        
        # Configurar columnas como entradas con pull-up
        for col in self.cols:
            GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def scan(self):
        """
        Escanear matriz y detectar pulsaciones
        
        Returns:
            Lista de IDs de botones presionados (0-15)
        """
        pressed_buttons = []
        current_time = time.time()
        
        for row_idx, row_pin in enumerate(self.rows):
            # Activar fila actual (LOW)
            GPIO.output(row_pin, GPIO.LOW)
            
            # Pequeño delay para estabilización
            time.sleep(0.001)
            
            # Leer columnas
            for col_idx, col_pin in enumerate(self.cols):
                # Leer estado (LOW = presionado)
                pressed = GPIO.input(col_pin) == GPIO.LOW
                
                # Verificar debouncing
                time_since_last = current_time - self.last_press_time[row_idx][col_idx]
                
                if pressed and not self.button_states[row_idx][col_idx]:
                    # Botón recién presionado
                    if time_since_last > DEBOUNCE_TIME:
                        self.button_states[row_idx][col_idx] = True
                        self.last_press_time[row_idx][col_idx] = current_time
                        
                        # Llamar callback si existe
                        if self.on_button_press:
                            button_id = row_idx * len(self.cols) + col_idx
                            self.on_button_press(button_id)
                
                elif not pressed:
                    # Botón liberado
                    self.button_states[row_idx][col_idx] = False
                
                # Agregar a lista si está presionado (para hold detection)
                if self.button_states[row_idx][col_idx]:
                    button_id = row_idx * len(self.cols) + col_idx
                    pressed_buttons.append(button_id)
            
            # Desactivar fila (HIGH)
            GPIO.output(row_pin, GPIO.HIGH)
        
        return pressed_buttons
    
    def is_button_pressed(self, button_id):
        """
        Verificar si un botón específico está presionado
        
        Args:
            button_id: ID del botón (0-15)
            
        Returns:
            True si está presionado, False si no
        """
        if 0 <= button_id < 16:
            row = button_id // len(self.cols)
            col = button_id % len(self.cols)
            return self.button_states[row][col]
        return False
    
    def cleanup(self):
        """Limpiar configuración GPIO"""
        # No hacer cleanup completo, solo resetear las filas
        for row in self.rows:
            GPIO.output(row, GPIO.HIGH)

