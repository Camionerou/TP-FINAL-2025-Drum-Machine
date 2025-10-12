"""
Programa principal de Raspberry Pi Drum Machine
Integra todos los componentes y maneja la lógica principal
"""

import time
import sys
from config import (
    MODE_PAD, MODE_SEQUENCER,
    BTN_PLAY_STOP, BTN_MODE, BTN_TEMPO_DOWN, BTN_TEMPO_UP,
    BTN_PATTERN, BTN_CLEAR, BTN_SAVE, BTN_STEP_SELECT,
    POT_TEMPO, POT_SWING, POT_MASTER_VOL, POT_KICK_VOL,
    POT_SNARE_VOL, POT_HIHATS_VOL, POT_TOMS_VOL, POT_CYMBALS_VOL,
    MAIN_LOOP_FPS, BPM_MIN, BPM_MAX, NUM_INSTRUMENTS, INSTRUMENTS,
    MAX_PATTERNS
)

from audio_engine import AudioEngine
from sequencer import Sequencer
from hardware import ButtonMatrix, LEDMatrix, ADCReader, LEDController


class DrumMachine:
    """Drum Machine principal"""
    
    def __init__(self):
        """Inicializar drum machine"""
        print("=" * 50)
        print("RASPBERRY PI DRUM MACHINE")
        print("=" * 50)
        
        # Estado
        self.mode = MODE_PAD
        self.selected_instrument = 0
        self.selected_step = 0
        self.running = True
        
        # Inicializar componentes
        print("\nInicializando componentes...")
        
        try:
            # Audio
            self.audio_engine = AudioEngine()
            
            # Secuenciador
            self.sequencer = Sequencer(self.audio_engine)
            
            # Hardware
            self.button_matrix = ButtonMatrix(on_button_press=self._on_button_press)
            self.led_matrix = LEDMatrix()
            self.adc_reader = ADCReader()
            self.led_controller = LEDController()
            
            print("\n✓ Todos los componentes inicializados")
            
            # Inicializar LEDs de estado
            self._update_mode_leds()
            
            # Mostrar pantalla inicial
            self.led_matrix.test_pattern()
            time.sleep(1)
            self.led_matrix.clear()
            
            # Test de LEDs
            print("\nProbando LEDs...")
            self.led_controller.test_sequence()
            
        except Exception as e:
            print(f"\n✗ Error inicializando componentes: {e}")
            raise
    
    def _on_button_press(self, button_id):
        """
        Callback para eventos de botón
        
        Args:
            button_id: ID del botón presionado (0-15)
        """
        print(f"Botón presionado: {button_id}")
        
        # Botones 0-7: Instrumentos/Pads
        if 0 <= button_id < 8:
            self._handle_instrument_button(button_id)
        
        # Botones 8-15: Funciones de control
        elif button_id == BTN_PLAY_STOP:
            self._handle_play_stop()
        elif button_id == BTN_MODE:
            self._handle_mode_change()
        elif button_id == BTN_TEMPO_DOWN:
            self._handle_tempo_change(-5)
        elif button_id == BTN_TEMPO_UP:
            self._handle_tempo_change(5)
        elif button_id == BTN_PATTERN:
            self._handle_pattern_change()
        elif button_id == BTN_CLEAR:
            self._handle_clear()
        elif button_id == BTN_SAVE:
            self._handle_save()
        elif button_id == BTN_STEP_SELECT:
            self._handle_step_select()
    
    def _handle_instrument_button(self, instrument_id):
        """Manejar botones de instrumento (0-7)"""
        if self.mode == MODE_PAD:
            # Modo PAD: Tocar instrumento directamente
            self.audio_engine.play_sample(instrument_id)
            self.selected_instrument = instrument_id
            print(f"♪ Tocando: {INSTRUMENTS[instrument_id]}")
            
            # Parpadear LED azul al tocar
            self.led_controller.pulse_led('blue', 0.1)
        
        elif self.mode == MODE_SEQUENCER:
            # Modo SEQUENCER: Toggle nota en el paso seleccionado
            self.sequencer.toggle_step(self.selected_step, instrument_id)
            print(f"Toggle: Paso {self.selected_step}, Instrumento {INSTRUMENTS[instrument_id]}")
    
    def _handle_play_stop(self):
        """Manejar botón Play/Stop"""
        self.sequencer.toggle_play()
        self._update_playing_led()
    
    def _handle_mode_change(self):
        """Cambiar entre modo PAD y SEQUENCER"""
        if self.mode == MODE_PAD:
            self.mode = MODE_SEQUENCER
            print("Modo: SECUENCIADOR")
        else:
            self.mode = MODE_PAD
            print("Modo: PAD")
        
        self._update_mode_leds()
    
    def _handle_tempo_change(self, delta):
        """Cambiar tempo"""
        new_bpm = self.sequencer.bpm + delta
        self.sequencer.set_bpm(new_bpm)
        print(f"BPM: {self.sequencer.bpm}")
    
    def _handle_pattern_change(self):
        """Cambiar al siguiente patrón"""
        next_pattern = (self.sequencer.current_pattern_id % MAX_PATTERNS) + 1
        
        # Intentar cargar, si no existe, limpiar
        if not self.sequencer.load_pattern(next_pattern):
            self.sequencer.current_pattern_id = next_pattern
            self.sequencer.clear_pattern()
        
        print(f"Patrón: {self.sequencer.current_pattern_id}")
    
    def _handle_clear(self):
        """Limpiar patrón actual"""
        self.sequencer.clear_pattern()
        print("Patrón limpiado")
    
    def _handle_save(self):
        """Guardar patrón actual"""
        if self.sequencer.save_pattern():
            print(f"✓ Patrón {self.sequencer.current_pattern_id} guardado")
            # Pulso en LED blanco para confirmar
            self.led_controller.pulse_led('white', 0.5)
        else:
            print("✗ Error guardando patrón")
    
    def _handle_step_select(self):
        """Seleccionar siguiente paso en modo secuenciador"""
        self.selected_step = (self.selected_step + 1) % 16
        print(f"Paso seleccionado: {self.selected_step}")
    
    def _update_mode_leds(self):
        """Actualizar LEDs de modo"""
        if self.mode == MODE_PAD:
            self.led_controller.set_led('red', True)
            self.led_controller.set_led('green', False)
        else:
            self.led_controller.set_led('red', False)
            self.led_controller.set_led('green', True)
    
    def _update_playing_led(self):
        """Actualizar LED de reproducción"""
        if self.sequencer.is_playing:
            self.led_controller.set_led('yellow', True)
        else:
            self.led_controller.set_led('yellow', False)
    
    def _update_beat_led(self):
        """Actualizar LED de beat (parpadea con el tempo)"""
        # Si está reproduciendo y estamos en el primer paso
        if self.sequencer.is_playing and self.sequencer.current_step % 4 == 0:
            self.led_controller.pulse_led('blue', 0.1)
    
    def _read_potentiometers(self):
        """Leer y procesar potenciómetros"""
        # Leer todos los canales
        values = self.adc_reader.read_all_channels()
        
        # Pot 0: Tempo (60-200 BPM)
        tempo = int(BPM_MIN + values[POT_TEMPO] * (BPM_MAX - BPM_MIN))
        if abs(tempo - self.sequencer.bpm) > 2:  # Evitar ajustes muy pequeños
            self.sequencer.set_bpm(tempo)
        
        # Pot 1: Swing (0-75%)
        swing = int(values[POT_SWING] * 75)
        if abs(swing - self.sequencer.swing) > 2:
            self.sequencer.set_swing(swing)
        
        # Pot 2: Master Volume
        master_vol = values[POT_MASTER_VOL]
        self.audio_engine.set_master_volume(master_vol)
        
        # Pot 3: Kick Volume
        self.audio_engine.set_instrument_volume(0, values[POT_KICK_VOL])
        
        # Pot 4: Snare Volume
        self.audio_engine.set_instrument_volume(1, values[POT_SNARE_VOL])
        
        # Pot 5: Hi-Hats Volume (controla ambos)
        hh_vol = values[POT_HIHATS_VOL]
        self.audio_engine.set_instrument_volume(2, hh_vol)  # CHH
        self.audio_engine.set_instrument_volume(3, hh_vol)  # OHH
        
        # Pot 6: Toms Volume (controla ambos)
        tom_vol = values[POT_TOMS_VOL]
        self.audio_engine.set_instrument_volume(4, tom_vol)  # Tom 1
        self.audio_engine.set_instrument_volume(5, tom_vol)  # Tom 2
        
        # Pot 7: Cymbals Volume (Crash + Ride)
        cym_vol = values[POT_CYMBALS_VOL]
        self.audio_engine.set_instrument_volume(6, cym_vol)  # Crash
        self.audio_engine.set_instrument_volume(7, cym_vol)  # Ride
    
    def _update_display(self):
        """Actualizar display LED"""
        if self.mode == MODE_SEQUENCER:
            # Mostrar grid del secuenciador
            pattern = self.sequencer.get_pattern()
            current_step = self.sequencer.current_step if self.sequencer.is_playing else -1
            self.led_matrix.draw_sequencer_grid(pattern, current_step)
        
        # Siempre mostrar info en la tercera sección
        mode_str = 'PAD' if self.mode == MODE_PAD else 'SEQ'
        self.led_matrix.draw_info(
            self.sequencer.bpm,
            self.sequencer.current_pattern_id,
            mode_str,
            self.sequencer.is_playing
        )
    
    def run(self):
        """Loop principal de la drum machine"""
        print("\n" + "=" * 50)
        print("DRUM MACHINE INICIADA")
        print("=" * 50)
        print("\nControles:")
        print("- Botones 1-8: Instrumentos/Pads")
        print("- Botón 9: Play/Stop")
        print("- Botón 10: Cambiar Modo (PAD/SEQ)")
        print("- Botón 11/12: Tempo -/+")
        print("- Botón 13: Cambiar Patrón")
        print("- Botón 14: Limpiar Patrón")
        print("- Botón 15: Guardar Patrón")
        print("- Botón 16: Seleccionar Paso")
        print("\nPresiona Ctrl+C para salir\n")
        
        frame_time = 1.0 / MAIN_LOOP_FPS
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Escanear botones
                self.button_matrix.scan()
                
                # Leer potenciómetros (no cada frame, cada 5 frames)
                if int(loop_start * 10) % 5 == 0:
                    self._read_potentiometers()
                
                # Actualizar display
                self._update_display()
                
                # Actualizar LEDs
                self._update_playing_led()
                self._update_beat_led()
                
                # Esperar para mantener FPS constante
                elapsed = time.time() - loop_start
                sleep_time = max(0, frame_time - elapsed)
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\nDeteniendo Drum Machine...")
            self.cleanup()
    
    def cleanup(self):
        """Limpiar y liberar recursos"""
        print("Limpiando recursos...")
        
        self.running = False
        
        # Detener secuenciador
        if hasattr(self, 'sequencer'):
            self.sequencer.cleanup()
        
        # Limpiar audio
        if hasattr(self, 'audio_engine'):
            self.audio_engine.cleanup()
        
        # Limpiar hardware
        if hasattr(self, 'led_controller'):
            self.led_controller.cleanup()
        
        if hasattr(self, 'led_matrix'):
            self.led_matrix.cleanup()
        
        if hasattr(self, 'adc_reader'):
            self.adc_reader.cleanup()
        
        if hasattr(self, 'button_matrix'):
            self.button_matrix.cleanup()
        
        print("✓ Drum Machine cerrada correctamente")


def main():
    """Función principal"""
    try:
        drum_machine = DrumMachine()
        drum_machine.run()
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

