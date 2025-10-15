"""
MIDI Handler para Drum Machine
Envía MIDI Clock, Notes y CC a dispositivos externos
"""

import time
try:
    import rtmidi
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    print("⚠️ python-rtmidi no disponible. Instalar con: pip3 install python-rtmidi")


class MIDIHandler:
    """Manejador de salida MIDI para sincronización y control"""
    
    # MIDI General Messages
    MIDI_CLOCK = 0xF8
    MIDI_START = 0xFA
    MIDI_STOP = 0xFC
    MIDI_CONTINUE = 0xFB
    
    # MIDI Note mappings (General MIDI Drum Map)
    MIDI_NOTE_MAP = {
        'kick': 36,      # C1  - Kick
        'snare': 38,     # D1  - Snare
        'chh': 42,       # F#1 - Closed Hi-Hat
        'ohh': 46,       # A#1 - Open Hi-Hat
        'tom1': 48,      # C2  - High Tom
        'tom2': 45,      # A1  - Low Tom
        'crash': 49,     # C#2 - Crash
        'ride': 51       # D#2 - Ride
    }
    
    def __init__(self, port_name=None, enable_clock=True, enable_notes=True, enable_cc=False):
        """
        Inicializar MIDI handler
        
        Args:
            port_name: Nombre del puerto MIDI (None = auto-detectar)
            enable_clock: Enviar MIDI clock
            enable_notes: Enviar MIDI notes
            enable_cc: Enviar MIDI CC
        """
        self.midi_out = None
        self.enabled = False
        self.enable_clock = enable_clock
        self.enable_notes = enable_notes
        self.enable_cc = enable_cc
        
        self.clock_counter = 0
        self.is_playing = False
        
        if not MIDI_AVAILABLE:
            print("⚠️ MIDI deshabilitado: python-rtmidi no instalado")
            return
        
        try:
            self.midi_out = rtmidi.MidiOut()
            
            # Listar puertos disponibles
            available_ports = self.midi_out.get_ports()
            
            if not available_ports:
                print("⚠️ No se encontraron puertos MIDI")
                return
            
            # Seleccionar puerto
            if port_name:
                # Buscar puerto específico
                for i, name in enumerate(available_ports):
                    if port_name.lower() in name.lower():
                        self.midi_out.open_port(i)
                        self.enabled = True
                        print(f"✓ MIDI conectado a: {name}")
                        break
            else:
                # Usar primer puerto disponible
                self.midi_out.open_port(0)
                self.enabled = True
                print(f"✓ MIDI conectado a: {available_ports[0]}")
            
            if not self.enabled:
                print(f"⚠️ Puerto MIDI '{port_name}' no encontrado")
                print(f"   Puertos disponibles: {available_ports}")
        
        except Exception as e:
            print(f"⚠️ Error inicializando MIDI: {e}")
            self.enabled = False
    
    def send_clock(self):
        """Enviar MIDI clock tick (debe llamarse 24 veces por quarter note)"""
        if not self.enabled or not self.enable_clock:
            return
        
        try:
            self.midi_out.send_message([self.MIDI_CLOCK])
        except Exception as e:
            print(f"Error enviando MIDI clock: {e}")
    
    def send_start(self):
        """Enviar MIDI start message"""
        if not self.enabled or not self.enable_clock:
            return
        
        try:
            self.midi_out.send_message([self.MIDI_START])
            self.is_playing = True
            self.clock_counter = 0
            print("▶️ MIDI Start enviado")
        except Exception as e:
            print(f"Error enviando MIDI start: {e}")
    
    def send_stop(self):
        """Enviar MIDI stop message"""
        if not self.enabled or not self.enable_clock:
            return
        
        try:
            self.midi_out.send_message([self.MIDI_STOP])
            self.is_playing = False
            print("⏹️ MIDI Stop enviado")
        except Exception as e:
            print(f"Error enviando MIDI stop: {e}")
    
    def send_continue(self):
        """Enviar MIDI continue message"""
        if not self.enabled or not self.enable_clock:
            return
        
        try:
            self.midi_out.send_message([self.MIDI_CONTINUE])
            self.is_playing = True
        except Exception as e:
            print(f"Error enviando MIDI continue: {e}")
    
    def send_note_on(self, instrument_name, velocity=127, channel=9):
        """
        Enviar MIDI Note On
        
        Args:
            instrument_name: Nombre del instrumento ('kick', 'snare', etc.)
            velocity: Velocidad (0-127)
            channel: Canal MIDI (9 = drums por convención, 0-indexed = canal 10)
        """
        if not self.enabled or not self.enable_notes:
            return
        
        if instrument_name not in self.MIDI_NOTE_MAP:
            return
        
        note = self.MIDI_NOTE_MAP[instrument_name]
        status = 0x90 + channel  # Note On en canal
        
        try:
            self.midi_out.send_message([status, note, velocity])
        except Exception as e:
            print(f"Error enviando MIDI note: {e}")
    
    def send_note_off(self, instrument_name, channel=9):
        """
        Enviar MIDI Note Off
        
        Args:
            instrument_name: Nombre del instrumento
            channel: Canal MIDI
        """
        if not self.enabled or not self.enable_notes:
            return
        
        if instrument_name not in self.MIDI_NOTE_MAP:
            return
        
        note = self.MIDI_NOTE_MAP[instrument_name]
        status = 0x80 + channel  # Note Off
        
        try:
            self.midi_out.send_message([status, note, 0])
        except Exception as e:
            print(f"Error enviando MIDI note off: {e}")
    
    def send_cc(self, cc_number, value, channel=0):
        """
        Enviar MIDI Control Change
        
        Args:
            cc_number: Número de CC (0-127)
            value: Valor (0-127)
            channel: Canal MIDI (0-15)
        """
        if not self.enabled or not self.enable_cc:
            return
        
        status = 0xB0 + channel  # Control Change
        
        try:
            self.midi_out.send_message([status, cc_number, value])
        except Exception as e:
            print(f"Error enviando MIDI CC: {e}")
    
    def calculate_clock_interval(self, bpm):
        """
        Calcular intervalo entre MIDI clocks
        
        Args:
            bpm: Tempo en BPM
            
        Returns:
            Intervalo en segundos entre clocks
        """
        # MIDI clock: 24 pulsos por quarter note
        # A 120 BPM: 2 beats/seg = 48 clocks/seg = 0.020833s por clock
        beats_per_second = bpm / 60.0
        clocks_per_second = beats_per_second * 24
        return 1.0 / clocks_per_second
    
    def cleanup(self):
        """Cerrar puerto MIDI"""
        if self.midi_out and self.enabled:
            try:
                self.send_stop()
                self.midi_out.close_port()
                print("✓ Puerto MIDI cerrado")
            except:
                pass
    
    def __del__(self):
        """Destructor"""
        self.cleanup()


# Ejemplo de uso
if __name__ == "__main__":
    # Test básico
    midi = MIDIHandler()
    
    if midi.enabled:
        print("\n🎹 Test MIDI:")
        midi.send_start()
        time.sleep(0.1)
        
        # Tocar kick
        midi.send_note_on('kick', velocity=127)
        time.sleep(0.5)
        midi.send_note_off('kick')
        
        midi.send_stop()
        midi.cleanup()
    else:
        print("\n❌ MIDI no disponible para test")

