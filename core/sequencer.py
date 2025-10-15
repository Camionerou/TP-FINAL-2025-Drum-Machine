"""
Secuenciador de 32 pasos para la Drum Machine
Maneja patrones, reproducción y guardado/carga de patrones
"""

import threading
import time
import json
import os
from .config import (
    NUM_STEPS, NUM_INSTRUMENTS, BPM_DEFAULT, BPM_MIN, BPM_MAX,
    SWING_MAX, PATTERNS_DIR, MAX_PATTERNS
)


class Sequencer:
    """Secuenciador de pasos para drum machine"""
    
    def __init__(self, audio_engine):
        """
        Inicializar secuenciador
        
        Args:
            audio_engine: Instancia de AudioEngine para reproducir sonidos
        """
        self.audio_engine = audio_engine
        
        # Patrón actual: 32 pasos x 8 instrumentos
        self.pattern = [[False] * NUM_INSTRUMENTS for _ in range(NUM_STEPS)]
        
        # Estado de reproducción
        self.is_playing = False
        self.current_step = 0
        self.bpm = BPM_DEFAULT
        self.swing = 0  # Porcentaje de swing (0-75)
        
        # Threading
        self.play_thread = None
        self.stop_event = threading.Event()
        
        # Patrones guardados
        self.current_pattern_id = 1
        
        print("Secuenciador inicializado")
    
    def toggle_step(self, step, instrument):
        """
        Activar/desactivar una nota en el patrón
        
        Args:
            step: Paso (0-15)
            instrument: ID del instrumento (0-7)
        """
        if 0 <= step < NUM_STEPS and 0 <= instrument < NUM_INSTRUMENTS:
            self.pattern[step][instrument] = not self.pattern[step][instrument]
    
    def set_step(self, step, instrument, state):
        """
        Establecer estado de una nota
        
        Args:
            step: Paso (0-15)
            instrument: ID del instrumento (0-7)
            state: True (activado) o False (desactivado)
        """
        if 0 <= step < NUM_STEPS and 0 <= instrument < NUM_INSTRUMENTS:
            self.pattern[step][instrument] = state
    
    def get_step(self, step, instrument):
        """Obtener estado de una nota"""
        if 0 <= step < NUM_STEPS and 0 <= instrument < NUM_INSTRUMENTS:
            return self.pattern[step][instrument]
        return False
    
    def clear_pattern(self):
        """Limpiar todo el patrón"""
        self.pattern = [[False] * NUM_INSTRUMENTS for _ in range(NUM_STEPS)]
        print("Patrón limpiado")
    
    def set_bpm(self, bpm):
        """
        Establecer tempo
        
        Args:
            bpm: Tempo en BPM (60-200)
        """
        self.bpm = max(BPM_MIN, min(BPM_MAX, int(bpm)))
    
    def set_swing(self, swing):
        """
        Establecer swing
        
        Args:
            swing: Porcentaje de swing (0-75)
        """
        self.swing = max(0, min(SWING_MAX, int(swing)))
    
    def _calculate_step_delay(self, step):
        """
        Calcular delay para un paso con swing
        
        Args:
            step: Número de paso
            
        Returns:
            Delay en segundos
        """
        # Tiempo base de un paso (16th note)
        base_delay = 60.0 / self.bpm / 4  # 4 pasos por beat
        
        # Aplicar swing a pasos impares
        if step % 2 == 1 and self.swing > 0:
            # El swing retrasa los pasos impares
            swing_factor = 1.0 + (self.swing / 100.0)
            return base_delay * swing_factor
        elif step % 2 == 0 and self.swing > 0:
            # Compensar los pasos pares para mantener el tempo general
            swing_factor = 1.0 - (self.swing / 200.0)
            return base_delay * swing_factor
        
        return base_delay
    
    def _play_loop(self):
        """Loop de reproducción del secuenciador"""
        self.current_step = 0
        
        while not self.stop_event.is_set():
            # Reproducir todas las notas del paso actual
            for instrument in range(NUM_INSTRUMENTS):
                if self.pattern[self.current_step][instrument]:
                    self.audio_engine.play_sample(instrument)
            
            # Calcular delay con swing
            step_delay = self._calculate_step_delay(self.current_step)
            
            # Avanzar al siguiente paso
            self.current_step = (self.current_step + 1) % NUM_STEPS
            
            # Esperar hasta el próximo paso
            self.stop_event.wait(step_delay)
    
    def play(self):
        """Iniciar reproducción del secuenciador"""
        if not self.is_playing:
            self.is_playing = True
            self.stop_event.clear()
            self.play_thread = threading.Thread(target=self._play_loop, daemon=True)
            self.play_thread.start()
            print("Secuenciador: PLAY")
    
    def stop(self):
        """Detener reproducción del secuenciador"""
        if self.is_playing:
            self.is_playing = False
            self.stop_event.set()
            if self.play_thread:
                self.play_thread.join(timeout=1.0)
            self.current_step = 0
            print("Secuenciador: STOP")
    
    def toggle_play(self):
        """Alternar entre play y stop"""
        if self.is_playing:
            self.stop()
        else:
            self.play()
    
    def save_pattern(self, pattern_id=None):
        """
        Guardar patrón actual a archivo JSON
        
        Args:
            pattern_id: ID del patrón (1-8), None usa el actual
            
        Returns:
            True si se guardó exitosamente
        """
        if pattern_id is None:
            pattern_id = self.current_pattern_id
        
        if not 1 <= pattern_id <= MAX_PATTERNS:
            print(f"ID de patrón inválido: {pattern_id}")
            return False
        
        # Crear directorio si no existe
        os.makedirs(PATTERNS_DIR, exist_ok=True)
        
        # Preparar datos
        data = {
            'pattern': self.pattern,
            'bpm': self.bpm,
            'swing': self.swing
        }
        
        # Guardar a archivo
        filename = os.path.join(PATTERNS_DIR, f'pattern_{pattern_id}.json')
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Patrón {pattern_id} guardado en {filename}")
            return True
        except Exception as e:
            print(f"Error guardando patrón: {e}")
            return False
    
    def load_pattern(self, pattern_id):
        """
        Cargar patrón desde archivo JSON
        
        Args:
            pattern_id: ID del patrón (1-8)
            
        Returns:
            True si se cargó exitosamente
        """
        if not 1 <= pattern_id <= MAX_PATTERNS:
            print(f"ID de patrón inválido: {pattern_id}")
            return False
        
        filename = os.path.join(PATTERNS_DIR, f'pattern_{pattern_id}.json')
        
        if not os.path.exists(filename):
            print(f"Patrón {pattern_id} no existe")
            return False
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.pattern = data.get('pattern', self.pattern)
            self.bpm = data.get('bpm', self.bpm)
            self.swing = data.get('swing', self.swing)
            self.current_pattern_id = pattern_id
            
            print(f"Patrón {pattern_id} cargado desde {filename}")
            return True
        except Exception as e:
            print(f"Error cargando patrón: {e}")
            return False
    
    def get_pattern(self):
        """Obtener patrón actual"""
        return self.pattern
    
    def cleanup(self):
        """Limpiar recursos"""
        self.stop()

