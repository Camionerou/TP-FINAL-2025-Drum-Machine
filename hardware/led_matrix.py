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
    
    def draw_sequencer_grid(self, pattern, current_step=-1, selected_step=-1):
        """
        Dibujar grid del secuenciador completo (32 pasos × 8 instrumentos)
        
        Args:
            pattern: Array 32x8 con el patrón (True/False)
            current_step: Paso actual siendo reproducido (-1 si no está reproduciendo)
            selected_step: Paso seleccionado para edición (POT_SCROLL)
        """
        # Limpiar toda la matriz
        self.clear()
        
        # Dibujar patrón completo (32 pasos)
        for step in range(min(32, len(pattern))):
            for instrument in range(min(8, len(pattern[step]))):
                if pattern[step][instrument]:
                    self.set_pixel(step, instrument, True)
        
        # Destacar paso seleccionado (brillo diferente - invertir píxeles)
        if 0 <= selected_step < 32:
            for y in range(8):
                current_state = self.get_pixel(selected_step, y)
                # Solo invertir si no es el current_step
                if selected_step != current_step:
                    self.set_pixel(selected_step, y, not current_state)
        
        # Destacar paso actual durante reproducción (parpadear)
        if 0 <= current_step < 32:
            # Hacer parpadear toda la columna del paso actual
            for y in range(8):
                self.set_pixel(current_step, y, True)
        
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
    
    # ===== MÉTODOS DE RENDERIZADO DE VISTAS =====
    
    def draw_bpm_view(self, bpm, beat_pulse=False, frame=0):
        """
        Vista de BPM: Muestra el tempo de manera visual
        
        Args:
            bpm: Tempo actual (60-200)
            beat_pulse: Si debe pulsar con el beat
            frame: Frame de animación
        """
        self.clear()
        
        # Texto "BPM" estilizado en las primeras 3 filas
        # B
        for y in range(5):
            self.set_pixel(2, y, True)
        self.set_pixel(3, 0, True)
        self.set_pixel(3, 2, True)
        self.set_pixel(3, 4, True)
        self.set_pixel(4, 1, True)
        self.set_pixel(4, 3, True)
        
        # P
        for y in range(5):
            self.set_pixel(6, y, True)
        self.set_pixel(7, 0, True)
        self.set_pixel(7, 2, True)
        self.set_pixel(8, 1, True)
        
        # M
        for y in range(5):
            self.set_pixel(10, y, True)
            self.set_pixel(13, y, True)
        self.set_pixel(11, 1, True)
        self.set_pixel(12, 2, True)
        
        # Barra gráfica del tempo en las últimas 3 filas
        bpm_normalized = (bpm - 60) / (200 - 60)  # 0.0 a 1.0
        bar_width = int(bpm_normalized * 30) + 1  # 1-31 LEDs
        
        for x in range(bar_width):
            self.set_pixel(x + 1, 6, True)
            self.set_pixel(x + 1, 7, True)
        
        # Pulso al beat (animación)
        if beat_pulse or (frame % 4 < 2):
            # Indicador pulsante en los extremos
            self.set_pixel(0, 6, True)
            self.set_pixel(0, 7, True)
            self.set_pixel(31, 6, True)
            self.set_pixel(31, 7, True)
        
        self.update()
    
    def draw_volume_view(self, volumes):
        """
        Vista de volúmenes: Barras para cada grupo
        
        Args:
            volumes: Dict con 'master', 'drums', 'hats', 'toms', 'cyms'
        """
        self.clear()
        
        master = volumes.get('master', 0.5)
        drums = volumes.get('drums', 0.5)
        hats = volumes.get('hats', 0.5)
        toms = volumes.get('toms', 0.5)
        cyms = volumes.get('cyms', 0.5)
        
        # Master volume (más ancho, columnas 0-7)
        master_height = int(master * 8)
        for x in range(8):
            for y in range(master_height):
                self.set_pixel(x, 7 - y, True)
        
        # Separador
        for y in range(8):
            self.set_pixel(8, y, y % 2 == 0)
        
        # Drums (columnas 10-14)
        drums_height = int(drums * 8)
        for x in range(10, 15):
            for y in range(drums_height):
                self.set_pixel(x, 7 - y, True)
        
        # Hats (columnas 16-20)
        hats_height = int(hats * 8)
        for x in range(16, 21):
            for y in range(hats_height):
                self.set_pixel(x, 7 - y, True)
        
        # Toms (columnas 22-25)
        toms_height = int(toms * 8)
        for x in range(22, 26):
            for y in range(toms_height):
                self.set_pixel(x, 7 - y, True)
        
        # Cymbals (columnas 27-31)
        cyms_height = int(cyms * 8)
        for x in range(27, 32):
            for y in range(cyms_height):
                self.set_pixel(x, 7 - y, True)
        
        self.update()
    
    def draw_swing_view(self, swing, frame=0):
        """
        Vista de swing: Representación visual del groove
        
        Args:
            swing: Porcentaje de swing (0-75)
            frame: Frame de animación
        """
        self.clear()
        
        # Título "SWING"
        # S
        for x in range(2, 5):
            self.set_pixel(x, 0, True)
            self.set_pixel(x, 2, True)
            self.set_pixel(x, 4, True)
        self.set_pixel(2, 1, True)
        self.set_pixel(4, 3, True)
        
        # Representación visual del swing como onda
        swing_normalized = swing / 75.0
        
        # Línea base recta (sin swing)
        for x in range(32):
            self.set_pixel(x, 6, True)
        
        # Onda sinusoidal que se curva más con mayor swing
        if swing > 0:
            import math
            for x in range(32):
                # Onda sinusoidal con amplitud proporcional al swing
                amplitude = swing_normalized * 2  # Máximo 2 píxeles de desplazamiento
                offset = int(amplitude * math.sin(x * math.pi / 8))
                y = 6 + offset
                if 0 <= y < 8:
                    self.set_pixel(x, y, True)
        
        # Indicador numérico en la parte inferior (% como barras)
        percent_bars = int((swing / 75.0) * 32)
        for x in range(percent_bars):
            self.set_pixel(x, 7, True)
        
        self.update()
    
    def draw_pattern_view(self, pattern_num):
        """
        Vista de patrón: Muestra el número grande del patrón
        
        Args:
            pattern_num: Número de patrón (1-8)
        """
        self.clear()
        
        # Números grandes 5x7 píxeles centrados
        numbers = {
            1: [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(0,1)],
            2: [(0,0),(1,0),(2,0),(2,1),(2,2),(1,3),(0,3),(0,4),(0,5),(0,6),(1,6),(2,6)],
            3: [(0,0),(1,0),(2,0),(2,1),(2,2),(1,3),(2,4),(2,5),(0,6),(1,6),(2,6)],
            4: [(0,0),(0,1),(0,2),(0,3),(1,3),(2,0),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6)],
            5: [(0,0),(1,0),(2,0),(0,1),(0,2),(0,3),(1,3),(2,3),(2,4),(2,5),(0,6),(1,6),(2,6)],
            6: [(0,0),(1,0),(2,0),(0,1),(0,2),(0,3),(1,3),(2,3),(0,4),(2,4),(0,5),(2,5),(0,6),(1,6),(2,6)],
            7: [(0,0),(1,0),(2,0),(2,1),(2,2),(2,3),(1,4),(1,5),(0,6)],
            8: [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(1,3),(2,3),(0,4),(2,4),(0,5),(2,5),(0,6),(1,6),(2,6)]
        }
        
        # Dibujar número centrado
        if pattern_num in numbers:
            offset_x = 14  # Centrar en x
            offset_y = 1   # Centrar en y
            for x, y in numbers[pattern_num]:
                self.set_pixel(offset_x + x, offset_y + y, True)
        
        # Borde decorativo
        for x in range(32):
            if x % 4 < 2:
                self.set_pixel(x, 0, True)
                self.set_pixel(x, 7, True)
        
        self.update()
    
    def draw_save_animation(self, frame):
        """
        Vista de guardado: Animación de guardando
        
        Args:
            frame: Frame de animación
        """
        self.clear()
        
        # Animación de ondas expandiéndose desde el centro
        center_x = 16
        center_y = 4
        
        # Calcular radio basado en frame
        radius = (frame % 20) // 2
        
        if radius < 10:
            # Ondas expandiéndose
            for x in range(32):
                for y in range(8):
                    dist = abs(x - center_x) + abs(y - center_y)
                    if dist == radius or dist == radius + 2:
                        self.set_pixel(x, y, True)
        else:
            # Checkmark final
            # ✓
            self.set_pixel(12, 4, True)
            self.set_pixel(13, 5, True)
            self.set_pixel(14, 6, True)
            self.set_pixel(15, 5, True)
            self.set_pixel(16, 4, True)
            self.set_pixel(17, 3, True)
            self.set_pixel(18, 2, True)
            self.set_pixel(19, 1, True)
        
        self.update()
    
    def draw_pad_view(self, instrument_id, instrument_name, frame):
        """
        Vista de pad: Muestra el instrumento tocado
        
        Args:
            instrument_id: ID del instrumento (0-7)
            instrument_name: Nombre del instrumento
            frame: Frame de animación
        """
        self.clear()
        
        # Nombre del instrumento (simplificado)
        # Solo mostrar primera letra grande
        first_letter = instrument_name[0].upper() if instrument_name else 'X'
        
        # Letra grande centrada
        # (implementación simple, solo algunas letras)
        letters = {
            'K': [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(2,2),(2,3),(3,1),(3,2),(3,4),(3,5),(4,0),(4,6)],
            'S': [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(1,3),(2,3),(3,4),(3,5),(0,6),(1,6),(2,6),(3,6)],
            'C': [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,6),(2,6),(3,6)],
            'O': [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(2,4),(0,5),(2,5),(0,6),(1,6),(2,6)],
            'T': [(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6)],
            'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(2,1),(2,2),(1,3),(2,4),(2,5),(2,6)]
        }
        
        if first_letter in letters:
            offset_x = 13  # Centrar
            offset_y = 1
            for x, y in letters[first_letter]:
                self.set_pixel(offset_x + x, offset_y + y, True)
        
        # Efecto de "golpe" - círculo pulsante
        pulse_size = 3 - (frame % 6) // 2
        if pulse_size > 0:
            # Esquinas pulsantes
            for i in range(pulse_size):
                self.set_pixel(i, 0, True)
                self.set_pixel(31-i, 0, True)
                self.set_pixel(i, 7, True)
                self.set_pixel(31-i, 7, True)
        
        self.update()
    
    def cleanup(self):
        """Limpiar y apagar display"""
        self.clear()
        self._write_all(REG_SHUTDOWN, 0x00)  # Apagar display
        self.spi.close()

