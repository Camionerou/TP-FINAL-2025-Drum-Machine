"""
Lector ADC para MCP3008 via SPI
Lee los 8 potenciómetros con suavizado
"""

import time
try:
    import spidev
except ImportError:
    print("Advertencia: spidev no disponible, usando mock")
    class MockSpiDev:
        def open(self, bus, device): pass
        def max_speed_hz(self, speed): pass
        def xfer2(self, data): return [0, 0, 0]
        def close(self): pass
    spidev = type('spidev', (), {'SpiDev': MockSpiDev})()

from config import SPI_MCP3008_CE, ADC_MAX_VALUE, ADC_THRESHOLD, ADC_MIN_VALID_VALUE


class ADCReader:
    """Lector de ADC MCP3008 para potenciómetros"""
    
    def __init__(self):
        """Inicializar SPI para MCP3008"""
        self.spi = spidev.SpiDev()
        self.spi.open(0, SPI_MCP3008_CE)  # Bus 0, CE1
        self.spi.max_speed_hz = 1350000   # 1.35 MHz
        
        # Valores actuales y anteriores para suavizado
        self.current_values = [0] * 8
        self.previous_values = [0] * 8
        
        # Realizar lectura inicial
        for channel in range(8):
            self.current_values[channel] = self._read_channel_raw(channel)
            self.previous_values[channel] = self.current_values[channel]
        
        print("ADC Reader (MCP3008) inicializado en CE1")
    
    def _read_channel_raw(self, channel):
        """
        Leer un canal del MCP3008
        
        Args:
            channel: Canal a leer (0-7)
            
        Returns:
            Valor raw (0-1023)
        """
        if channel < 0 or channel > 7:
            return 0
        
        # Protocolo MCP3008: start bit, single-ended mode, channel select
        # Formato: [1, (8+channel)<<4, 0]
        command = [1, (8 + channel) << 4, 0]
        
        # Realizar transferencia SPI
        reply = self.spi.xfer2(command)
        
        # Extraer valor de 10 bits de la respuesta
        # Los bits están en reply[1] (2 bits) y reply[2] (8 bits)
        value = ((reply[1] & 3) << 8) + reply[2]
        
        return value
    
    def read_channel(self, channel):
        """
        Leer canal con suavizado
        Si el valor es muy bajo (ruido/desconectado), retorna 1.0 (100%)
        
        Args:
            channel: Canal a leer (0-7)
            
        Returns:
            Valor normalizado (0.0-1.0), o 1.0 si lectura inválida
        """
        raw_value = self._read_channel_raw(channel)
        
        # Si el valor es menor al mínimo válido, retornar 100%
        # Esto maneja potenciómetros desconectados o con ruido
        if raw_value < ADC_MIN_VALID_VALUE:
            return 1.0
        
        # Aplicar suavizado simple (promedio con valor anterior)
        smoothed = (raw_value + self.previous_values[channel]) // 2
        
        # Actualizar valores
        self.previous_values[channel] = smoothed
        self.current_values[channel] = smoothed
        
        # Normalizar a 0.0-1.0
        return smoothed / ADC_MAX_VALUE
    
    def read_all_channels(self):
        """
        Leer todos los canales
        Si cualquier lectura es inválida, retorna 1.0 (100%)
        
        Returns:
            Lista de 8 valores normalizados (0.0-1.0), o 1.0 si lectura inválida
        """
        values = []
        for channel in range(8):
            values.append(self.read_channel(channel))
        return values
    
    def has_changed(self, channel, new_value_raw):
        """
        Verificar si un valor ha cambiado significativamente
        
        Args:
            channel: Canal a verificar
            new_value_raw: Nuevo valor raw (0-1023)
            
        Returns:
            True si el cambio es significativo
        """
        old_value = self.current_values[channel]
        return abs(new_value_raw - old_value) > ADC_THRESHOLD
    
    def get_channel_value(self, channel):
        """
        Obtener último valor leído de un canal (0.0-1.0)
        Retorna 1.0 si la lectura es inválida
        """
        if 0 <= channel < 8:
            if self.current_values[channel] < ADC_MIN_VALID_VALUE:
                return 1.0
            return self.current_values[channel] / ADC_MAX_VALUE
        return 1.0  # Si canal inválido, retornar 100%
    
    def cleanup(self):
        """Cerrar conexión SPI"""
        self.spi.close()

