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
    
    def draw_sequencer_grid(self, pattern, current_step=-1):
        """
        Dibujar grid del secuenciador (primeros 16 pasos en 2 bloques de 8x8)
        
        Args:
            pattern: Array 16x8 con el patrón (True/False)
            current_step: Paso actual siendo reproducido (-1 si no está reproduciendo)
        """
        # Limpiar las primeras dos secciones (16 columnas)
        for x in range(16):
            for y in range(8):
                self.set_pixel(x, y, False)
        
        # Dibujar patrón
        for step in range(min(16, len(pattern))):
            for instrument in range(min(8, len(pattern[step]))):
                if pattern[step][instrument]:
                    self.set_pixel(step, instrument, True)
        
        # Destacar paso actual
        if 0 <= current_step < 16:
            # Hacer parpadear toda la columna del paso actual (invertir)
            for y in range(8):
                current_state = self.get_pixel(current_step, y)
                self.set_pixel(current_step, y, not current_state)
        
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
    
    def cleanup(self):
        """Limpiar y apagar display"""
        self.clear()
        self._write_all(REG_SHUTDOWN, 0x00)  # Apagar display
        self.spi.close()

