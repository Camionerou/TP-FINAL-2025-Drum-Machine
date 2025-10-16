"""
Programa principal de Raspberry Pi Drum Machine con Sistema de Vistas Dinámicas
Integra todos los componentes con UI mejorada y controles inteligentes
"""

import time
import sys
import numpy as np
from .config import (
    MODE_PAD, MODE_SEQUENCER,
    BTN_PLAY_STOP, BTN_MODE, BTN_PATTERN_PREV, BTN_PATTERN_NEXT,
    BTN_CLEAR, BTN_SAVE, BTN_COPY, BTN_MUTE,
    POT_SCROLL, POT_TEMPO, POT_SWING, POT_MASTER,
    POT_VOL_DRUMS, POT_VOL_HATS, POT_VOL_TOMS, POT_VOL_CYMS,
    MAIN_LOOP_FPS, BPM_MIN, BPM_MAX, NUM_INSTRUMENTS, INSTRUMENTS,
    MAX_PATTERNS, DOUBLE_CLICK_TIME, HOLD_TIME, LONG_HOLD_TIME,
    VIEW_TIMEOUT, VIEW_INACTIVITY_TIMEOUT, NUM_STEPS
)

from .audio_engine import AudioEngine
from .sequencer import Sequencer
from hardware import ButtonMatrix, LEDMatrix, ADCReader, LEDController
from ui import ViewManager, ViewType, ButtonHandler
from features import TapTempo, MIDIHandler, BluetoothAudio


class DrumMachine:
    """Drum Machine principal optimizado con sistema de vistas dinámicas"""
    
    def __init__(self):
        """Inicializar drum machine"""
        print("=" * 60)
        print("  RASPBERRY PI DRUM MACHINE v2.0 - SISTEMA DE VISTAS")
        print("=" * 60)
        
        # Estado principal
        self.mode = MODE_SEQUENCER
        self.mode_locked = False
        self.selected_step = 0  # Paso seleccionado por POT_SCROLL (0-31)
        self.running = True
        
        # Estado de copy/paste
        self.copied_step = None
        
        # Estado de mute/solo
        self.muted_instruments = set()
        self.solo_instrument = None
        
        # Tap Tempo
        self.tap_tempo = TapTempo(min_taps=2, max_taps=6, timeout=3.0)
        self.tap_tempo_active = False
        
        # Effects view mode
        self.effects_view_active = False
        
        # Valores anteriores de potenciómetros para detectar cambios
        # Inicializar con 1.0 (100%) para que todos los volúmenes estén al máximo por defecto
        self.prev_pot_values = {
            POT_VOL_DRUMS: 1.0,
            POT_VOL_HATS: 1.0,
            POT_VOL_TOMS: 1.0,
            POT_VOL_CYMS: 1.0
        }
        
        print("\nInicializando componentes...")
        
        try:
            # Audio
            self.audio_engine = AudioEngine()
            
            # Inicializar todos los volúmenes al 100% por defecto
            for i in range(8):
                self.audio_engine.set_instrument_volume(i, 1.0)
            
            # Secuenciador
            self.sequencer = Sequencer(self.audio_engine)
            
            # Hardware
            self.button_matrix = ButtonMatrix()
            self.led_matrix = LEDMatrix()
            self.adc_reader = ADCReader()
            self.led_controller = LEDController()
            
            # Sistema de vistas
            self.view_manager = ViewManager(
                default_timeout=VIEW_TIMEOUT,
                inactivity_timeout=VIEW_INACTIVITY_TIMEOUT
            )
            
            # Manejador de botones
            self.button_handler = ButtonHandler(
                double_click_time=DOUBLE_CLICK_TIME,
                hold_time=HOLD_TIME
            )
            
            # MIDI Handler (opcional)
            try:
                self.midi = MIDIHandler(enable_clock=True, enable_notes=True)
                if self.midi.enabled:
                    print("✓ MIDI Output habilitado")
                else:
                    self.midi = None
            except Exception as e:
                print(f"⚠️ MIDI no disponible: {e}")
                self.midi = None
            
            # Bluetooth Audio (opcional)
            try:
                self.bluetooth = BluetoothAudio()
                if self.bluetooth.enabled:
                    print("✓ Bluetooth disponible")
                    # Intentar reconectar al último dispositivo automáticamente
                    print("🔄 Intentando reconectar a último dispositivo Bluetooth...")
                    if self.bluetooth.quick_connect_last():
                        print("✓ Reconectado a Bluetooth automáticamente")
                else:
                    self.bluetooth = None
            except Exception as e:
                print(f"⚠️ Bluetooth no disponible: {e}")
                self.bluetooth = None
            
            # Registrar callbacks de botones
            self.button_handler.register_callbacks(
                on_press=self._on_button_press,
                on_double_click=self._on_button_double_click,
                on_hold=self._on_button_hold,
                on_release=self._on_button_release,
                on_combination=self._on_button_combination
            )
            
            print("✓ Todos los componentes inicializados")
            
            # Inicializar LEDs de estado
            self._update_mode_leds()
            
            # Mostrar pantalla inicial
            self.led_matrix.test_pattern()
            time.sleep(0.5)
            self.view_manager.show_view(ViewType.SEQUENCER)
            
            # Test de LEDs
            print("\nProbando LEDs indicadores...")
            self.led_controller.test_sequence()
            
        except Exception as e:
            print(f"\n✗ Error inicializando componentes: {e}")
            raise
    
    # ===== CALLBACKS DE BOTONES =====
    
    def _on_button_press(self, button_id):
        """Callback para click simple de botón"""
        self.view_manager.register_interaction()
        
        # Botones 0-7: Instrumentos
        if 0 <= button_id < 8:
            self._handle_instrument_button(button_id)
        
        # Botón 8: PLAY/STOP
        elif button_id == BTN_PLAY_STOP:
            self._handle_play_stop()
        
        # Botón 9: MODE
        elif button_id == BTN_MODE:
            if not self.mode_locked:
                self._handle_mode_change()
        
        # Botón 10: PATTERN_PREV
        elif button_id == BTN_PATTERN_PREV:
            self._handle_pattern_change(-1)
        
        # Botón 11: PATTERN_NEXT / TAP TEMPO
        elif button_id == BTN_PATTERN_NEXT:
            if self.tap_tempo_active:
                # En modo tap, registrar tap
                self._handle_tap()
            else:
                # Modo normal, cambiar patrón
                self._handle_pattern_change(1)
        
        # Botón 12: CLEAR (click simple) o EFFECTS (hold)
        elif button_id == BTN_CLEAR:
            if not self.effects_view_active:
                self._handle_clear_step()
        
        # Botón 13: SAVE
        elif button_id == BTN_SAVE:
            self._handle_save()
        
        # Botón 14: COPY
        elif button_id == BTN_COPY:
            self._handle_copy()
        
        # Botón 15: MUTE
        elif button_id == BTN_MUTE:
            # Mute/unmute paso actual
            pass  # Implementar si es necesario
    
    def _on_button_double_click(self, button_id):
        """Callback para doble-click"""
        self.view_manager.register_interaction()
        
        # BTN 8: PLAY/STOP → Doble click: Reset a paso 0
        if button_id == BTN_PLAY_STOP:
            self.sequencer.current_step = 0
            print("Secuenciador reseteado a paso 0")
        
        # BTN 11: PATTERN_NEXT → Doble click: Activar Tap Tempo
        elif button_id == BTN_PATTERN_NEXT:
            self._activate_tap_tempo()
        
        # BTN 12: CLEAR → Doble: Clear instrumento en todos los pasos
        elif button_id == BTN_CLEAR:
            # Requiere combinación con botón de instrumento
            print("Doble-click Clear: Mantén un botón de instrumento")
        
        # BTN 15: MUTE → Doble: Solo del instrumento
        elif button_id == BTN_MUTE:
            # Toggle solo mode
            pass
    
    def _on_button_hold(self, button_id, duration):
        """Callback para botón mantenido"""
        self.view_manager.register_interaction()
        
        # BTN 9: MODE → Hold 2s: Bloquear/desbloquear modo
        if button_id == BTN_MODE and duration >= 2.0:
            self.mode_locked = not self.mode_locked
            status = "bloqueado" if self.mode_locked else "desbloqueado"
            print(f"Modo {status}")
            self.led_controller.pulse_led('white' if self.mode_locked else 'blue', 0.3)
        
        # BTN 12: CLEAR → Hold 1s: Vista EFFECTS | Hold 3s: Clear patrón
        elif button_id == BTN_CLEAR:
            if duration >= LONG_HOLD_TIME:
                # Hold 3s: Clear patrón
                self.sequencer.clear_pattern()
                print("Patrón completo limpiado")
                for _ in range(3):
                    self.led_controller.set_led('white', True)
                    time.sleep(0.1)
                    self.led_controller.set_led('white', False)
                    time.sleep(0.1)
            elif duration >= HOLD_TIME:
                # Hold 1s: Toggle vista EFFECTS
                self.effects_view_active = not self.effects_view_active
                if self.effects_view_active:
                    print("🎛️ Modo EFFECTS activado - Pots 0-2: Efectos individuales")
                    print("  Pot 0: Compresor, Pot 1: EQ, Pot 2: Intensidad")
                    self._show_effects_view()
                else:
                    print("Vista EFFECTS desactivada")
                    self.view_manager.show_view(ViewType.SEQUENCER)
        
        # BTN 15: MUTE → Hold 2s: Toggle Bluetooth Audio
        elif button_id == BTN_MUTE and duration >= 2.0:
            if hasattr(self, 'bluetooth') and self.bluetooth:
                if self.bluetooth.is_connected():
                    print("🔌 Desconectando Bluetooth...")
                    self.bluetooth.disconnect()
                    self.led_controller.pulse_led('red', 0.5)
                else:
                    print("🔌 Conectando Bluetooth...")
                    if self.bluetooth.quick_connect_last():
                        print("✓ Conectado a Bluetooth")
                        self.led_controller.pulse_led('green', 0.5)
                    else:
                        print("❌ No se pudo conectar a Bluetooth")
                        self.led_controller.pulse_led('red', 0.5)
            else:
                print("⚠️ Bluetooth no disponible")
                self.led_controller.pulse_led('yellow', 0.5)
    
    def _on_button_release(self, button_id, duration):
        """Callback para liberación de botón"""
        pass
    
    def _on_button_combination(self, button_ids):
        """Callback para combinación de botones"""
        self.view_manager.register_interaction()
        
        # Verificar si hay hold+press para operaciones especiales
        held_buttons = self.button_handler.get_held_buttons()
        
        # BTN_SAVE mantenido + PATTERN_PREV/NEXT: Guardar en patrón específico
        if BTN_SAVE in held_buttons:
            if BTN_PATTERN_PREV in button_ids:
                # Guardar en patrón anterior
                prev_pattern = ((self.sequencer.current_pattern_id - 2) % MAX_PATTERNS) + 1
                self.sequencer.save_pattern(prev_pattern)
                self.view_manager.show_view(ViewType.SAVE, duration=1.5)
                print(f"Guardado en patrón {prev_pattern}")
            elif BTN_PATTERN_NEXT in button_ids:
                # Guardar en patrón siguiente
                next_pattern = (self.sequencer.current_pattern_id % MAX_PATTERNS) + 1
                self.sequencer.save_pattern(next_pattern)
                self.view_manager.show_view(ViewType.SAVE, duration=1.5)
                print(f"Guardado en patrón {next_pattern}")
        
        # BTN_COPY mantenido + PATTERN_PREV/NEXT: Pegar en paso
        elif BTN_COPY in held_buttons and self.copied_step is not None:
            if BTN_PATTERN_PREV in button_ids and self.selected_step > 0:
                self.selected_step -= 1
                self._paste_step()
            elif BTN_PATTERN_NEXT in button_ids and self.selected_step < NUM_STEPS - 1:
                self.selected_step += 1
                self._paste_step()
        
        # BTN_MUTE mantenido + instrumento: Mute/unmute global
        elif BTN_MUTE in held_buttons:
            for btn_id in button_ids:
                if 0 <= btn_id < 8:
                    if btn_id in self.muted_instruments:
                        self.muted_instruments.remove(btn_id)
                        print(f"Unmute: {INSTRUMENTS[btn_id]}")
                    else:
                        self.muted_instruments.add(btn_id)
                        print(f"Mute: {INSTRUMENTS[btn_id]}")
    
    # ===== MANEJADORES DE ACCIONES =====
    
    def _handle_instrument_button(self, instrument_id):
        """Manejar botones de instrumento (0-7)"""
        if self.mode == MODE_PAD:
            # Modo PAD: Tocar instrumento
            if instrument_id not in self.muted_instruments:
                self.audio_engine.play_sample(instrument_id)
                
                # MIDI note out
                if self.midi and self.midi.enabled:
                    self.midi.send_note_on(INSTRUMENTS[instrument_id], velocity=127)
            
            # LED azul parpadea
            self.led_controller.pulse_led('blue', 0.1)
        
        elif self.mode == MODE_SEQUENCER:
            # Modo SEQUENCER: Toggle nota en paso seleccionado
            self.sequencer.toggle_step(self.selected_step, instrument_id)
            print(f"Toggle: Paso {self.selected_step}, {INSTRUMENTS[instrument_id]}")
    
    def _activate_tap_tempo(self):
        """Activar modo Tap Tempo"""
        self.tap_tempo_active = True
        self.tap_tempo.reset()
        print("\n🎵 TAP TEMPO ACTIVADO - Golpea BTN 11 al ritmo deseado")
        self.led_controller.pulse_led('yellow', 0.2)
    
    def _handle_tap(self):
        """Manejar tap en modo Tap Tempo"""
        if not self.tap_tempo_active:
            return
        
        # Registrar tap y obtener BPM
        bpm = self.tap_tempo.tap()
        tap_count = self.tap_tempo.get_tap_count()
        
        # Feedback visual
        self.led_controller.pulse_led('blue', 0.1)
        
        if bpm is not None:
            # Actualizar BPM
            self.sequencer.set_bpm(bpm)
            confidence = self.tap_tempo.get_confidence()
            print(f"  Tap {tap_count}: BPM = {bpm} (confianza: {confidence:.0%})")
            
            # Mostrar vista BPM
            self.view_manager.show_view(
                ViewType.BPM,
                {'bpm': bpm}
            )
        else:
            print(f"  Tap {tap_count}: Necesitas {self.tap_tempo.min_taps - tap_count} tap(s) más")
        
        # Desactivar después de timeout o si tenemos suficientes taps
        if tap_count >= 4:
            # Suficientes taps, desactivar
            import threading
            def deactivate_later():
                import time
                time.sleep(2.0)
                self.tap_tempo_active = False
                print("✓ Tap Tempo desactivado - BPM establecido")
            
            threading.Thread(target=deactivate_later, daemon=True).start()
    
    def _handle_play_stop(self):
        """Play/Stop secuenciador"""
        self.sequencer.toggle_play()
        
        # MIDI start/stop
        if self.midi and self.midi.enabled:
            if self.sequencer.is_playing:
                self.midi.send_start()
            else:
                self.midi.send_stop()
        
        self._update_playing_led()
        print(f"Secuenciador: {'PLAY' if self.sequencer.is_playing else 'STOP'}")
    
    def _handle_mode_change(self):
        """Cambiar entre modo PAD y SEQUENCER"""
        if self.mode == MODE_PAD:
            self.mode = MODE_SEQUENCER
            print("Modo: SECUENCIADOR")
        else:
            self.mode = MODE_PAD
            print("Modo: PAD")
        
        self._update_mode_leds()
    
    def _handle_pattern_change(self, direction):
        """Cambiar patrón (direction: -1 o +1)"""
        if direction < 0:
            # Patrón anterior
            new_pattern = ((self.sequencer.current_pattern_id - 2) % MAX_PATTERNS) + 1
        else:
            # Patrón siguiente
            new_pattern = (self.sequencer.current_pattern_id % MAX_PATTERNS) + 1
        
        # Intentar cargar, si no existe, crear nuevo
        if not self.sequencer.load_pattern(new_pattern):
            self.sequencer.current_pattern_id = new_pattern
            self.sequencer.clear_pattern()
        
        # Mostrar vista PATTERN detallada
        self.view_manager.show_view(
            ViewType.PATTERN,
            {
                'pattern_num': new_pattern,
                'bpm': self.sequencer.bpm,
                'steps': NUM_STEPS
            },
            duration=2.0
        )
        
        print(f"Patrón: {new_pattern}")
    
    def _handle_clear_step(self):
        """Limpiar paso actual"""
        for instrument in range(NUM_INSTRUMENTS):
            self.sequencer.set_step(self.selected_step, instrument, False)
        print(f"Paso {self.selected_step} limpiado")
    
    def _handle_save(self):
        """Guardar patrón actual"""
        if self.sequencer.save_pattern():
            print(f"✓ Patrón {self.sequencer.current_pattern_id} guardado")
            # Mostrar vista de guardado
            self.view_manager.show_view(
                ViewType.SAVE,
                {'pattern_num': self.sequencer.current_pattern_id},
                duration=1.5
            )
            self.led_controller.pulse_led('white', 0.5)
        else:
            print("✗ Error guardando patrón")
    
    def _handle_copy(self):
        """Copiar paso actual"""
        self.copied_step = [
            self.sequencer.get_step(self.selected_step, inst)
            for inst in range(NUM_INSTRUMENTS)
        ]
        print(f"Paso {self.selected_step} copiado")
        self.led_controller.pulse_led('blue', 0.2)
    
    def _paste_step(self):
        """Pegar paso copiado"""
        if self.copied_step is not None:
            for inst in range(NUM_INSTRUMENTS):
                self.sequencer.set_step(self.selected_step, inst, self.copied_step[inst])
            print(f"Paso pegado en {self.selected_step}")
            self.led_controller.pulse_led('green', 0.2)
    
    # ===== CONTROL DE LEDS =====
    
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
        """Actualizar LED de beat"""
        if self.sequencer.is_playing and self.sequencer.current_step % 4 == 0:
            self.led_controller.pulse_led('blue', 0.05)
    
    # ===== EFECTOS =====
    
    def _show_effects_view(self):
        """Mostrar vista de efectos inicial (intensidad general)"""
        if hasattr(self.audio_engine.processor, 'effects') and self.audio_engine.processor.effects:
            effects = self.audio_engine.processor.effects
            intensity = effects.get_intensity()
            self.view_manager.show_view(
                ViewType.EFFECT_INTENSITY, 
                {'intensity': intensity}, 
                duration=None
            )
    
    # ===== LECTURA DE POTENCIÓMETROS =====
    
    def _read_potentiometers(self):
        """Leer y procesar potenciómetros con detección de cambios"""
        values = self.adc_reader.read_all_channels()
        
        # Modo EFFECTS: Pots controlan efectos individuales
        if self.effects_view_active and hasattr(self.audio_engine.processor, 'effects'):
            effects = self.audio_engine.processor.effects
            if effects:
                # Detectar qué pot cambió más significativamente
                if not hasattr(self, '_last_effects_values'):
                    self._last_effects_values = np.array(values).copy()
                
                # Calcular cambios (asegurar que ambos sean arrays de numpy)
                values_array = np.array(values)
                changes = np.abs(values_array - self._last_effects_values)
                max_change_idx = np.argmax(changes)
                
                # Mostrar vista si hay cambio significativo (>5%) o si es la primera vez
                first_time = not hasattr(self, '_effects_view_shown')
                if changes[max_change_idx] > 0.05 or first_time:  # Threshold más alto para reducir procesamiento
                    self._effects_view_shown = True
                    
                    if max_change_idx == 0:  # Pot 0: Compresor
                        compressor_mix = values[0] * 100
                        effects.set_compressor_mix(compressor_mix)
                        print(f"🎛️ Compresor: {compressor_mix:.1f}%")
                        self.view_manager.show_view(
                            ViewType.EFFECT_COMPRESSOR,
                            {'compressor_mix': compressor_mix}
                        )
                    elif max_change_idx == 1:  # Pot 1: EQ
                        eq_mix = values[1] * 100
                        effects.set_eq_mix(eq_mix)
                        print(f"🎛️ EQ: {eq_mix:.1f}%")
                        self.view_manager.show_view(
                            ViewType.EFFECT_EQ,
                            {'eq_mix': eq_mix}
                        )
                    elif max_change_idx == 2:  # Pot 2: Intensidad
                        intensity = values[2] * 100
                        effects.set_intensity(intensity)
                        print(f"🎛️ Intensidad: {intensity:.1f}%")
                        self.view_manager.show_view(
                            ViewType.EFFECT_INTENSITY,
                            {'intensity': intensity}
                        )
                
                # Actualizar valores de referencia
                self._last_effects_values = values_array.copy()
            return  # No procesar pots normales en modo effects
        
        # POT_SCROLL (0): Seleccionar paso (0-31)
        scroll_value = values[POT_SCROLL]
        new_selected_step = int(scroll_value * NUM_STEPS)
        if new_selected_step >= NUM_STEPS:
            new_selected_step = NUM_STEPS - 1
        if new_selected_step != self.selected_step:
            self.selected_step = new_selected_step
            self.view_manager.register_interaction()
        
        # POT_TEMPO (1): BPM
        tempo_value = values[POT_TEMPO]
        new_bpm = int(BPM_MIN + tempo_value * (BPM_MAX - BPM_MIN))
        if abs(new_bpm - self.sequencer.bpm) > 2:
            self.sequencer.set_bpm(new_bpm)
            # Trigger vista BPM
            self.view_manager.show_view(
                ViewType.BPM,
                {'bpm': new_bpm}
            )
        
        # POT_SWING (2): Swing
        swing_value = values[POT_SWING]
        new_swing = int(swing_value * 75)
        if abs(new_swing - self.sequencer.swing) > 2:
            self.sequencer.set_swing(new_swing)
            # Trigger vista SWING
            self.view_manager.show_view(
                ViewType.SWING,
                {'swing': new_swing}
            )
        
        # POT_MASTER (3): Master Volume
        master_vol = values[POT_MASTER]
        old_master = self.audio_engine.master_volume
        if abs(master_vol - old_master) > 0.05:
            self.audio_engine.set_master_volume(master_vol)
            # Trigger vista VOLUME
            self.view_manager.show_view(
                ViewType.VOLUME,
                {'volume': int(master_vol * 100)}
            )
        
        # POT_VOL_DRUMS (4): Kick + Snare
        drums_vol = values[POT_VOL_DRUMS]
        old_drums = self.prev_pot_values.get(POT_VOL_DRUMS, drums_vol)
        if abs(drums_vol - old_drums) > 0.05:
            self.audio_engine.set_instrument_volume(0, drums_vol)  # Kick
            self.audio_engine.set_instrument_volume(1, drums_vol)  # Snare
            self.prev_pot_values[POT_VOL_DRUMS] = drums_vol
            # Trigger vista VOL_DRUMS
            self.view_manager.show_view(
                ViewType.VOL_DRUMS,
                {'volume': drums_vol}
            )
        
        # POT_VOL_HATS (5): CHH + OHH
        hats_vol = values[POT_VOL_HATS]
        old_hats = self.prev_pot_values.get(POT_VOL_HATS, hats_vol)
        if abs(hats_vol - old_hats) > 0.05:
            self.audio_engine.set_instrument_volume(2, hats_vol)  # CHH
            self.audio_engine.set_instrument_volume(3, hats_vol)  # OHH
            self.prev_pot_values[POT_VOL_HATS] = hats_vol
            # Trigger vista VOL_HATS
            self.view_manager.show_view(
                ViewType.VOL_HATS,
                {'volume': hats_vol}
            )
        
        # POT_VOL_TOMS (6): Tom1 + Tom2
        toms_vol = values[POT_VOL_TOMS]
        old_toms = self.prev_pot_values.get(POT_VOL_TOMS, toms_vol)
        if abs(toms_vol - old_toms) > 0.05:
            self.audio_engine.set_instrument_volume(4, toms_vol)  # Tom1
            self.audio_engine.set_instrument_volume(5, toms_vol)  # Tom2
            self.prev_pot_values[POT_VOL_TOMS] = toms_vol
            # Trigger vista VOL_TOMS
            self.view_manager.show_view(
                ViewType.VOL_TOMS,
                {'volume': toms_vol}
            )
        
        # POT_VOL_CYMS (7): Crash + Ride
        cyms_vol = values[POT_VOL_CYMS]
        old_cyms = self.prev_pot_values.get(POT_VOL_CYMS, cyms_vol)
        if abs(cyms_vol - old_cyms) > 0.05:
            self.audio_engine.set_instrument_volume(6, cyms_vol)  # Crash
            self.audio_engine.set_instrument_volume(7, cyms_vol)  # Ride
            self.prev_pot_values[POT_VOL_CYMS] = cyms_vol
            # Trigger vista VOL_CYMS
            self.view_manager.show_view(
                ViewType.VOL_CYMS,
                {'volume': cyms_vol}
            )
    
    # ===== LOOP PRINCIPAL =====
    
    def run(self):
        """Loop principal de la drum machine"""
        print("\n" + "=" * 60)
        print("  DRUM MACHINE INICIADA - SISTEMA DE VISTAS DINÁMICAS")
        print("=" * 60)
        print("\nControles:")
        print("  Botones 1-8: Instrumentos (PAD) / Toggle notas (SEQ)")
        print("  Botón 9: Play/Stop (Doble: Reset)")
        print("  Botón 10: Cambiar Modo (Hold 2s: Bloquear)")
        print("  Botón 11/12: Patrón -/+")
        print("  Botón 13: Clear paso (Doble: Clear inst, Hold 3s: Clear todo)")
        print("  Botón 14: Guardar (Hold+11/12: Guardar en patrón específico)")
        print("  Botón 15: Copiar paso (Hold+11/12: Pegar)")
        print("  Botón 16: Mute (Hold+1-8: Mute global)")
        print("\nPotenciómetros:")
        print("  Pot 0: Scroll pasos (0-31)")
        print("  Pot 1: Tempo | Pot 2: Swing | Pot 3: Master Vol")
        print("  Pot 4-7: Volúmenes grupales")
        print("\nPresiona Ctrl+C para salir\n")
        
        frame_time = 1.0 / MAIN_LOOP_FPS
        pot_update_counter = 0
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Escanear botones
                pressed_buttons = self.button_matrix.scan()
                
                # Actualizar manejador de botones
                self.button_handler.update(pressed_buttons)
                
                # Leer potenciómetros (cada 5 frames para reducir carga de CPU)
                pot_update_counter += 1
                if pot_update_counter >= 5:
                    self._read_potentiometers()
                    pot_update_counter = 0
                
                # Actualizar vista manager (timeouts)
                self.view_manager.update()
                
                # Renderizar vista actual
                self.view_manager.render(
                    self.led_matrix,
                    self.sequencer,
                    self.selected_step
                )
                
                # Actualizar LEDs
                self._update_playing_led()
                self._update_beat_led()
                
                # Mantener FPS constante
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
        
        if hasattr(self, 'sequencer'):
            self.sequencer.cleanup()
        
        if hasattr(self, 'audio_engine'):
            self.audio_engine.cleanup()
        
        if hasattr(self, 'midi') and self.midi:
            self.midi.cleanup()
        
        if hasattr(self, 'bluetooth') and self.bluetooth:
            if self.bluetooth.is_connected():
                print("Desconectando Bluetooth...")
                self.bluetooth.disconnect()
        
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

