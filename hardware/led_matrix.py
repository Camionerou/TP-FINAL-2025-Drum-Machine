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
        
        # INVERTIR eje X para corregir espejado
        x = (self.width - 1) - x
        
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
        
        # INVERTIR eje X para corregir espejado
        x = (self.width - 1) - x
        
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
        Vista BPM: Todo horizontal
        Formato: BPM 145
        
        Args:
            bpm: Tempo actual (60-200)
        """
        self.clear()
        
        # Texto "BPM" centrado verticalmente (filas 2-4)
        # B
        for y in range(2, 5):
            self.set_pixel(2, y, True)
        self.set_pixel(3, 2, True)
        self.set_pixel(3, 3, True)
        self.set_pixel(3, 4, True)
        # P
        for y in range(2, 5):
            self.set_pixel(5, y, True)
        self.set_pixel(6, 2, True)
        self.set_pixel(6, 3, True)
        # M
        for y in range(2, 5):
            self.set_pixel(8, y, True)
            self.set_pixel(11, y, True)
        self.set_pixel(9, 3, True)
        self.set_pixel(10, 3, True)
        
        # Número BPM grande a la derecha
        self._draw_number(bpm, 14, 2)
        
        self.update()
    
    def draw_swing_view(self, swing):
        """
        Vista SWING: Todo horizontal
        Formato: SWG 35
        
        Args:
            swing: Porcentaje de swing (0-75)
        """
        self.clear()
        
        # Texto "SWG"
        # S
        self.set_pixel(2, 2, True)
        self.set_pixel(3, 2, True)
        self.set_pixel(2, 3, True)
        self.set_pixel(3, 4, True)
        # W
        for y in range(2, 5):
            self.set_pixel(5, y, True)
            self.set_pixel(8, y, True)
        self.set_pixel(6, 4, True)
        self.set_pixel(7, 4, True)
        # G
        for y in range(2, 5):
            self.set_pixel(10, y, True)
        self.set_pixel(11, 2, True)
        self.set_pixel(11, 4, True)
        
        # Número SWING
        self._draw_number(swing, 14, 2)
        
        self.update()
    
    def draw_volume_view(self, volume):
        """
        Vista VOLUME: Todo horizontal
        Formato: VOL 87
        
        Args:
            volume: Volumen master (0-100)
        """
        self.clear()
        
        # Texto "VOL"
        # V
        self.set_pixel(2, 2, True)
        self.set_pixel(3, 4, True)
        self.set_pixel(4, 2, True)
        # O
        for y in range(2, 5):
            self.set_pixel(6, y, True)
            self.set_pixel(8, y, True)
        self.set_pixel(7, 2, True)
        self.set_pixel(7, 4, True)
        # L
        for y in range(2, 5):
            self.set_pixel(10, y, True)
        self.set_pixel(11, 4, True)
        
        # Número VOL
        self._draw_number(volume, 14, 2)
        
        self.update()
    
    def draw_vol_group_view(self, group_name, volume):
        """
        Vista de volumen grupal: Label + número
        Formato: DR 90 o HH 75 etc
        
        Args:
            group_name: Nombre del grupo ('DR', 'HH', 'TM', 'CY')
            volume: Volumen (0.0-1.0)
        """
        self.clear()
        
        # Convertir a porcentaje
        vol_percent = int(volume * 100)
        
        # Dibujar label según el grupo (centrado verticalmente filas 2-4)
        if group_name == 'DR':
            # D
            for y in range(2, 5):
                self.set_pixel(4, y, True)
            self.set_pixel(5, 2, True)
            self.set_pixel(5, 4, True)
            self.set_pixel(6, 3, True)
            # R
            for y in range(2, 5):
                self.set_pixel(8, y, True)
            self.set_pixel(9, 2, True)
            self.set_pixel(9, 3, True)
        
        elif group_name == 'HH':
            # H
            for y in range(2, 5):
                self.set_pixel(4, y, True)
                self.set_pixel(7, y, True)
            self.set_pixel(5, 3, True)
            self.set_pixel(6, 3, True)
            # H
            for y in range(2, 5):
                self.set_pixel(9, y, True)
                self.set_pixel(12, y, True)
            self.set_pixel(10, 3, True)
            self.set_pixel(11, 3, True)
        
        elif group_name == 'TM':
            # T
            self.set_pixel(4, 2, True)
            self.set_pixel(5, 2, True)
            self.set_pixel(6, 2, True)
            for y in range(2, 5):
                self.set_pixel(5, y, True)
            # M
            for y in range(2, 5):
                self.set_pixel(8, y, True)
                self.set_pixel(11, y, True)
            self.set_pixel(9, 3, True)
            self.set_pixel(10, 3, True)
        
        elif group_name == 'CY':
            # C
            for y in range(2, 5):
                self.set_pixel(4, y, True)
            self.set_pixel(5, 2, True)
            self.set_pixel(5, 4, True)
            # Y
            self.set_pixel(7, 2, True)
            self.set_pixel(9, 2, True)
            self.set_pixel(8, 3, True)
            for y in range(3, 5):
                self.set_pixel(8, y, True)
        
        # Número grande a la derecha
        self._draw_number(vol_percent, 14, 2)
        
        self.update()
    
    def draw_pattern_view(self, pattern_num, bpm, steps):
        """
        Vista PATTERN: Todo horizontal
        Formato: PAT 3
        
        Args:
            pattern_num: Número de patrón (1-8)
            bpm: Tempo actual (no se muestra por espacio)
            steps: Número de pasos (no se muestra por espacio)
        """
        self.clear()
        
        # Todo horizontal centrado
        # Texto "PAT"
        # P
        self.set_pixel(6, 3, True)
        self.set_pixel(6, 4, True)
        self.set_pixel(7, 3, True)
        # A
        self.set_pixel(9, 3, True)
        self.set_pixel(9, 4, True)
        self.set_pixel(10, 3, True)
        self.set_pixel(10, 4, True)
        # T
        self.set_pixel(12, 3, True)
        self.set_pixel(13, 3, True)
        self.set_pixel(12, 4, True)
        
        # Número de patrón grande
        self._draw_number(pattern_num, 16, 2)
        
        self.update()
    
    def draw_save_view(self, pattern_num):
        """
        Vista SAVE: Todo horizontal
        Formato: SAVED P3 ✓
        
        Args:
            pattern_num: Número de patrón guardado
        """
        self.clear()
        
        # Todo horizontal centrado
        # Texto "SAVED"
        # S
        self.set_pixel(2, 3, True)
        self.set_pixel(3, 3, True)
        self.set_pixel(3, 4, True)
        # A
        self.set_pixel(5, 3, True)
        self.set_pixel(5, 4, True)
        # V
        self.set_pixel(7, 3, True)
        self.set_pixel(8, 4, True)
        self.set_pixel(9, 3, True)
        # E
        self.set_pixel(11, 3, True)
        self.set_pixel(11, 4, True)
        # D
        self.set_pixel(13, 3, True)
        self.set_pixel(13, 4, True)
        self.set_pixel(14, 3, True)
        
        # "P"
        self.set_pixel(17, 3, True)
        self.set_pixel(17, 4, True)
        
        # Número de patrón
        self._draw_number(pattern_num, 19, 2)
        
        # Checkmark ✓
        self.set_pixel(25, 4, True)
        self.set_pixel(26, 5, True)
        self.set_pixel(27, 3, True)
        self.set_pixel(28, 2, True)
        
        self.update()
    
    def cleanup(self):
        """Limpiar y apagar display"""
        self.clear()
        self._write_all(REG_SHUTDOWN, 0x00)  # Apagar display
        self.spi.close()

