"""
Controlador de LEDs indicadores
Maneja 5 LEDs de estado con patrones de parpadeo
"""

import time
import threading
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    print("Advertencia: RPi.GPIO no disponible, usando mock")
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        HIGH = 1
        LOW = 0
        
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def output(self, pin, state): pass
        def cleanup(self): pass
    
    GPIO = MockGPIO()

from config import LED_RED, LED_GREEN, LED_YELLOW, LED_BLUE, LED_WHITE


class LEDController:
    """Controlador de LEDs indicadores"""
    
    def __init__(self):
        """Inicializar LEDs"""
        self.leds = {
            'red': LED_RED,
            'green': LED_GREEN,
            'yellow': LED_YELLOW,
            'blue': LED_BLUE,
            'white': LED_WHITE
        }
        
        # Estado de LEDs
        self.led_states = {name: False for name in self.leds}
        
        # Control de parpadeo
        self.blink_states = {name: False for name in self.leds}
        self.blink_thread = None
        self.running = False
        
        self._setup_gpio()
        self._start_blink_thread()
    
    def _setup_gpio(self):
        """Configurar pines GPIO para LEDs"""
        GPIO.setmode(GPIO.BCM)
        
        for name, pin in self.leds.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    
    def _start_blink_thread(self):
        """Iniciar thread de parpadeo"""
        self.running = True
        self.blink_thread = threading.Thread(target=self._blink_loop, daemon=True)
        self.blink_thread.start()
    
    def _blink_loop(self):
        """Loop de parpadeo en thread separado"""
        while self.running:
            for name in self.leds:
                if self.blink_states[name]:
                    # Toggle LED
                    self.led_states[name] = not self.led_states[name]
                    self._update_led(name)
            
            time.sleep(0.25)  # Parpadeo a 2 Hz
    
    def _update_led(self, name):
        """Actualizar estado físico de un LED"""
        if name in self.leds:
            pin = self.leds[name]
            state = GPIO.HIGH if self.led_states[name] else GPIO.LOW
            GPIO.output(pin, state)
    
    def set_led(self, name, state):
        """
        Establecer estado de un LED
        
        Args:
            name: Nombre del LED ('red', 'green', 'yellow', 'blue', 'white')
            state: True (encendido) o False (apagado)
        """
        if name in self.leds:
            self.blink_states[name] = False  # Detener parpadeo
            self.led_states[name] = state
            self._update_led(name)
    
    def set_blink(self, name, enable):
        """
        Establecer parpadeo de un LED
        
        Args:
            name: Nombre del LED
            enable: True para activar parpadeo, False para detener
        """
        if name in self.leds:
            self.blink_states[name] = enable
            if not enable:
                # Si se desactiva el parpadeo, apagar el LED
                self.led_states[name] = False
                self._update_led(name)
    
    def pulse_led(self, name, duration=0.2):
        """
        Hacer un pulso breve en un LED
        
        Args:
            name: Nombre del LED
            duration: Duración del pulso en segundos
        """
        if name in self.leds:
            self.set_led(name, True)
            threading.Timer(duration, lambda: self.set_led(name, False)).start()
    
    def all_off(self):
        """Apagar todos los LEDs"""
        for name in self.leds:
            self.set_led(name, False)
            self.blink_states[name] = False
    
    def test_sequence(self):
        """Secuencia de prueba de LEDs"""
        for name in ['red', 'green', 'yellow', 'blue', 'white']:
            self.set_led(name, True)
            time.sleep(0.2)
            self.set_led(name, False)
    
    def cleanup(self):
        """Limpiar recursos"""
        self.running = False
        if self.blink_thread:
            self.blink_thread.join(timeout=1.0)
        self.all_off()

