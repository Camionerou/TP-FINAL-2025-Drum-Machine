"""
Controlador de matriz LED MAX7219 8x32
Maneja 4 módulos MAX7219 (8x8 cada uno) para display de información
"""

try:
    import spidev
except ImportError:
    print("Advertencia: spidev no disponible, usando mock")
    class MockSpiDev:
        def open(self, bus, device): pass
        def max_speed_hz(self, speed): pass
        def xfer2(self, data): return [0] * len(data)
        def close(self): pass
    spidev = type('spidev', (), {'SpiDev': MockSpiDev})()

from config import SPI_MAX7219_CE, MAX7219_NUM_DEVICES, MAX7219_BRIGHTNESS


# Registros MAX7219
REG_NOOP = 0x00
REG_DIGIT0 = 0x01
REG_DIGIT1 = 0x02
REG_DIGIT2 = 0x03
REG_DIGIT3 = 0x04
REG_DIGIT4 = 0x05
REG_DIGIT5 = 0x06
REG_DIGIT6 = 0x07
REG_DIGIT7 = 0x08
REG_DECODEMODE = 0x09
REG_INTENSITY = 0x0A
REG_SCANLIMIT = 0x0B
REG_SHUTDOWN = 0x0C
REG_DISPLAYTEST = 0x0F


class LEDMatrix:
    """Controlador de matriz LED MAX7219"""
    
    def __init__(self, num_devices=MAX7219_NUM_DEVICES):
        """
        Inicializar matriz LED
        
        Args:
            num_devices: Número de módulos MAX7219 en cascada
        """
        self.num_devices = num_devices
        self.width = 8 * num_devices  # 8 columnas por dispositivo
        self.height = 8
        
        # Buffer de display (cada dispositivo tiene 8 filas de 8 bits)
        self.buffer = [[0] * 8 for _ in range(num_devices)]
        
        # Inicializar SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, SPI_MAX7219_CE)  # Bus 0, CE0
        self.spi.max_speed_hz = 1000000   # 1 MHz
        
        self._init_display()
        print(f"LED Matrix (MAX7219) inicializado: {self.width}x{self.height} en CE0")
    
    def _init_display(self):
        """Inicializar todos los dispositivos MAX7219"""
        # Configurar todos los dispositivos
        self._write_all(REG_SCANLIMIT, 0x07)      # Mostrar todos los 8 dígitos
        self._write_all(REG_DECODEMODE, 0x00)     # Sin decodificación (modo raw)
        self._write_all(REG_DISPLAYTEST, 0x00)    # Modo normal (no test)
        self._write_all(REG_INTENSITY, MAX7219_BRIGHTNESS)  # Brillo
        self._write_all(REG_SHUTDOWN, 0x01)       # Encender display
        
        # Limpiar display
        self.clear()
    
    def _write_all(self, register, data):
        """
        Escribir el mismo valor a todos los dispositivos
        
        Args:
            register: Registro del MAX7219
            data: Dato a escribir
        """
        # Crear paquete para todos los dispositivos
        packet = []
        for _ in range(self.num_devices):
            packet.extend([register, data])
        
        self.spi.xfer2(packet)
    
    def _write_device(self, device_id, register, data):
        """
        Escribir a un dispositivo específico
        
        Args:
            device_id: ID del dispositivo (0 = primero en la cadena)
            register: Registro del MAX7219
            data: Dato a escribir
        """
        packet = []
        
        # Agregar NOOPs para dispositivos después del objetivo
        for i in range(self.num_devices - 1, device_id, -1):
            packet.extend([REG_NOOP, 0x00])
        
        # Agregar comando para el dispositivo objetivo
        packet.extend([register, data])
        
        # Agregar NOOPs para dispositivos antes del objetivo
        for i in range(device_id):
            packet.extend([REG_NOOP, 0x00])
        
        self.spi.xfer2(packet)
    
    def set_pixel(self, x, y, state):
        """
        Establecer un pixel
        
        Args:
            x: Posición X (0 a width-1)
            y: Posición Y (0 a 7)
            state: True (encendido) o False (apagado)
        """
        if x < 0 or x >= self.width or y < 0 or y >= 8:
            return
        
        # Determinar dispositivo y posición local
        device_id = x // 8
        local_x = x % 8
        
        # Actualizar buffer
        if state:
            self.buffer[device_id][y] |= (1 << local_x)
        else:
            self.buffer[device_id][y] &= ~(1 << local_x)
    
    def get_pixel(self, x, y):
        """Obtener estado de un pixel"""
        if x < 0 or x >= self.width or y < 0 or y >= 8:
            return False
        
        device_id = x // 8
        local_x = x % 8
        
        return bool(self.buffer[device_id][y] & (1 << local_x))
    
    def clear(self):
        """Limpiar toda la matriz"""
        for device_id in range(self.num_devices):
            for row in range(8):
                self.buffer[device_id][row] = 0
        self.update()
    
    def fill(self):
        """Encender todos los LEDs"""
        for device_id in range(self.num_devices):
            for row in range(8):
                self.buffer[device_id][row] = 0xFF
        self.update()
    
    def update(self):
        """Actualizar display con el buffer actual"""
        for device_id in range(self.num_devices):
            for row in range(8):
                register = REG_DIGIT0 + row
                data = self.buffer[device_id][row]
                self._write_device(device_id, register, data)
    
    def draw_sequencer_grid(self, pattern, display_step=-1):
        """
        Dibujar grid del secuenciador completo (32 pasos × 8 instrumentos)
        Con playhead dual inteligente
        
        Args:
            pattern: Array 32x8 con el patrón (True/False)
            display_step: Paso a resaltar (playhead cuando reproduce, paso seleccionado cuando no)
        """
        # Limpiar toda la matriz
        self.clear()
        
        # Dibujar patrón completo (32 pasos)
        for step in range(min(32, len(pattern))):
            for instrument in range(min(8, len(pattern[step]))):
                if pattern[step][instrument]:
                    self.set_pixel(step, instrument, True)
        
        # Destacar paso actual/seleccionado (iluminar toda la columna)
        if 0 <= display_step < 32:
            for y in range(8):
                self.set_pixel(display_step, y, True)
        
        self.update()
    
    def draw_info(self, bpm, pattern_num, mode, is_playing=False):
        """
        Dibujar información en las últimas 2 secciones (16 columnas)
        
        Args:
            bpm: Tempo actual
            pattern_num: Número de patrón (1-8)
            mode: Modo actual ('PAD' o 'SEQ')
            is_playing: Si está reproduciendo
        """
        # Por simplicidad, usar los últimos 16 LEDs para mostrar:
        # - Columna 16-23: BPM (representación visual)
        # - Columna 24-31: Patrón y modo
        
        # Limpiar sección de info
        for x in range(16, 32):
            for y in range(8):
                self.set_pixel(x, y, False)
        
        # Mostrar BPM como barras (más alto = más LEDs encendidos)
        bpm_normalized = (bpm - 60) / (200 - 60)  # 0.0 a 1.0
        bpm_leds = int(bpm_normalized * 8)
        for y in range(bpm_leds):
            for x in range(16, 20):  # 4 columnas para BPM
                self.set_pixel(x, 7 - y, True)
        
        # Mostrar número de patrón (1-8) como LEDs verticales
        for y in range(pattern_num):
            self.set_pixel(21, y, True)
        
        # Mostrar modo (PAD vs SEQ)
        if mode == 'PAD':
            # Dibujar 'P' simple
            for y in range(5):
                self.set_pixel(24, y, True)
            self.set_pixel(25, 0, True)
            self.set_pixel(25, 2, True)
            self.set_pixel(26, 1, True)
        else:
            # Dibujar 'S' simple
            for x in range(24, 27):
                self.set_pixel(x, 0, True)
                self.set_pixel(x, 2, True)
                self.set_pixel(x, 4, True)
            self.set_pixel(24, 1, True)
            self.set_pixel(26, 3, True)
        
        # Indicador de reproducción (esquina)
        if is_playing:
            self.set_pixel(31, 0, True)
            self.set_pixel(31, 1, True)
        
        self.update()
    
    def draw_text_simple(self, text, offset_x=0):
        """
        Dibujar texto simple (solo números y letras básicas)
        
        Args:
            text: Texto a mostrar
            offset_x: Desplazamiento horizontal
        """
        # Implementación básica - por ahora solo limpiar y mostrar algo
        self.clear()
        # TODO: Implementar fuente de caracteres si es necesario
        self.update()
    
    def test_pattern(self):
        """Patrón de prueba"""
        self.clear()
        # Dibujar un patrón de tablero de ajedrez
        for x in range(self.width):
            for y in range(8):
                if (x + y) % 2 == 0:
                    self.set_pixel(x, y, True)
        self.update()
    
    # ===== FUENTE DE NÚMEROS 3x5 COMPACTA =====
    
    def _get_digit_3x5(self, digit):
        """
        Obtener bitmap de un dígito en formato 3x5 píxeles
        
        Args:
            digit: Dígito 0-9
            
        Returns:
            Lista de tuplas (x, y) con píxeles a encender
        """
        digits = {
            '0': [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
            '1': [(1,0),(0,1),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
            '2': [(0,0),(1,0),(2,0),(2,1),(0,2),(1,2),(2,2),(0,3),(0,4),(1,4),(2,4)],
            '3': [(0,0),(1,0),(2,0),(2,1),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
            '4': [(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(2,3),(2,4)],
            '5': [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
            '6': [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
            '7': [(0,0),(1,0),(2,0),(2,1),(2,2),(1,3),(1,4)],
            '8': [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
            '9': [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
        }
        return digits.get(str(digit), [])
    
    def _draw_number(self, number, start_x, start_y):
        """
        Dibujar un número en la posición especificada
        
        Args:
            number: Número a dibujar (puede ser string o int)
            start_x: Posición X inicial
            start_y: Posición Y inicial
        """
        str_number = str(number)
        x_offset = start_x
        
        for char in str_number:
            if char.isdigit():
                pixels = self._get_digit_3x5(char)
                for px, py in pixels:
                    self.set_pixel(x_offset + px, start_y + py, True)
                x_offset += 4  # 3 píxeles de ancho + 1 de espacio
            elif char == ' ':
                x_offset += 2
    
    # ===== MÉTODOS DE RENDERIZADO DE VISTAS LIMPIAS =====
    
    def draw_bpm_view(self, bpm):
        """
        Vista BPM: Tempo simple y grande
        Formato:  145
                  BPM
        
        Args:
            bpm: Tempo actual (60-200)
        """
        self.clear()
        
        # Número BPM grande y centrado en filas 1-5
        self._draw_number(bpm, 8, 1)
        
        # Texto "BPM" centrado en fila 7
        # B
        self.set_pixel(11, 7, True)
        self.set_pixel(12, 7, True)
        # P
        self.set_pixel(14, 7, True)
        self.set_pixel(15, 7, True)
        # M
        self.set_pixel(17, 7, True)
        self.set_pixel(18, 7, True)
        self.set_pixel(19, 7, True)
        
        self.update()
    
    def draw_swing_view(self, swing):
        """
        Vista SWING: Swing simple y grande
        Formato:  35
                  SWG
        
        Args:
            swing: Porcentaje de swing (0-75)
        """
        self.clear()
        
        # Número SWING grande y centrado
        self._draw_number(swing, 10, 1)
        
        # Texto "SWG"
        # S
        self.set_pixel(11, 7, True)
        self.set_pixel(12, 7, True)
        # W
        self.set_pixel(14, 7, True)
        self.set_pixel(15, 7, True)
        self.set_pixel(16, 7, True)
        # G
        self.set_pixel(18, 7, True)
        self.set_pixel(19, 7, True)
        
        self.update()
    
    def draw_volume_view(self, volume):
        """
        Vista VOLUME: Volumen master simple
        Formato:  87
                  VOL
        
        Args:
            volume: Volumen master (0-100)
        """
        self.clear()
        
        # Número VOLUME grande y centrado
        self._draw_number(volume, 10, 1)
        
        # Texto "VOL"
        # V
        self.set_pixel(11, 7, True)
        self.set_pixel(12, 7, True)
        self.set_pixel(13, 7, True)
        # O
        self.set_pixel(15, 7, True)
        self.set_pixel(16, 7, True)
        # L
        self.set_pixel(18, 7, True)
        self.set_pixel(19, 7, True)
        
        self.update()
    
    def draw_volumes_view(self, volumes):
        """
        Vista VOLUMES: 4 cuadrantes simples con barras horizontales
        Formato: DR  HH  TM  CY  (fila 0)
                 ██  ███ ██  ████ (fila 7)
        
        Args:
            volumes: Dict con 'drums', 'hats', 'toms', 'cyms' (0.0-1.0)
        """
        self.clear()
        
        drums = volumes.get('drums', 0.5)
        hats = volumes.get('hats', 0.5)
        toms = volumes.get('toms', 0.5)
        cyms = volumes.get('cyms', 0.5)
        
        # Cuadrante 1: DRUMS (columnas 0-7)
        # Label "DR" en fila 0
        self.set_pixel(2, 0, True)
        self.set_pixel(3, 0, True)  # D
        self.set_pixel(5, 0, True)
        self.set_pixel(6, 0, True)  # R
        
        # Barra horizontal en fila 7
        drums_leds = int(drums * 8)
        for x in range(drums_leds):
            self.set_pixel(x, 7, True)
        
        # Cuadrante 2: HATS (columnas 8-15)
        # Label "HH" en fila 0
        self.set_pixel(10, 0, True)
        self.set_pixel(11, 0, True)  # H
        self.set_pixel(13, 0, True)
        self.set_pixel(14, 0, True)  # H
        
        # Barra horizontal
        hats_leds = int(hats * 8)
        for x in range(hats_leds):
            self.set_pixel(8 + x, 7, True)
        
        # Cuadrante 3: TOMS (columnas 16-23)
        # Label "TM" en fila 0
        self.set_pixel(18, 0, True)
        self.set_pixel(19, 0, True)  # T
        self.set_pixel(21, 0, True)
        self.set_pixel(22, 0, True)  # M
        
        # Barra horizontal
        toms_leds = int(toms * 8)
        for x in range(toms_leds):
            self.set_pixel(16 + x, 7, True)
        
        # Cuadrante 4: CYMBALS (columnas 24-31)
        # Label "CY" en fila 0
        self.set_pixel(26, 0, True)
        self.set_pixel(27, 0, True)  # C
        self.set_pixel(29, 0, True)
        self.set_pixel(30, 0, True)  # Y
        
        # Barra horizontal
        cyms_leds = int(cyms * 8)
        for x in range(cyms_leds):
            self.set_pixel(24 + x, 7, True)
        
        self.update()
    
    def draw_pattern_view(self, pattern_num, bpm, steps):
        """
        Vista PATTERN: Info detallada del patrón
        Formato: PAT  3/8
                 145  32
        
        Args:
            pattern_num: Número de patrón (1-8)
            bpm: Tempo actual
            steps: Número de pasos
        """
        self.clear()
        
        # Línea superior (fila 0): "PAT  3/8"
        # P
        self.set_pixel(2, 0, True)
        self.set_pixel(3, 0, True)
        # A
        self.set_pixel(5, 0, True)
        self.set_pixel(6, 0, True)
        # T
        self.set_pixel(8, 0, True)
        self.set_pixel(9, 0, True)
        
        # Patrón: "3/8"
        self._draw_number(pattern_num, 14, 0)
        self.set_pixel(17, 2, True)  # "/"
        self._draw_number(8, 18, 0)
        
        # Línea inferior: BPM y STEPS con números grandes
        # BPM (número grande centrado izquierda)
        self._draw_number(bpm, 2, 3)
        
        # STEPS (número grande centrado derecha)
        self._draw_number(steps, 22, 3)
        
        self.update()
    
    def draw_save_view(self, pattern_num):
        """
        Vista SAVE: Confirmación simple
        Formato: SAVED  3  ✓
        
        Args:
            pattern_num: Número de patrón guardado
        """
        self.clear()
        
        # Texto "SAVED" pequeño en fila 0
        # S
        self.set_pixel(6, 0, True)
        self.set_pixel(7, 0, True)
        # A
        self.set_pixel(9, 0, True)
        self.set_pixel(10, 0, True)
        # V
        self.set_pixel(12, 0, True)
        self.set_pixel(13, 0, True)
        # E
        self.set_pixel(15, 0, True)
        self.set_pixel(16, 0, True)
        # D
        self.set_pixel(18, 0, True)
        self.set_pixel(19, 0, True)
        
        # Número de patrón grande en centro
        self._draw_number(pattern_num, 12, 2)
        
        # Checkmark ✓ en la derecha
        self.set_pixel(24, 4, True)
        self.set_pixel(25, 5, True)
        self.set_pixel(26, 6, True)
        self.set_pixel(27, 5, True)
        self.set_pixel(28, 4, True)
        self.set_pixel(29, 3, True)
        
        self.update()
    
    def cleanup(self):
        """Limpiar y apagar display"""
        self.clear()
        self._write_all(REG_SHUTDOWN, 0x00)  # Apagar display
        self.spi.close()

