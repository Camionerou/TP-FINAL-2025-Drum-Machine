"""
Motor de audio para la Drum Machine usando pygame
Maneja la carga y reproducción de samples de batería
"""

import pygame
import os
import numpy as np
from .config import (
    INSTRUMENTS, SAMPLES_DIR, SAMPLE_RATE, AUDIO_BUFFER_SIZE, 
    AUDIO_CHANNELS, MASTER_VOLUME_DEFAULT, INSTRUMENT_VOLUME_DEFAULT,
    AUDIO_GAIN_BOOST
)
from .audio_processor import AudioProcessor


class AudioEngine:
    """Motor de audio para reproducir samples de batería"""
    
    def __init__(self):
        """Inicializar pygame mixer y cargar samples"""
        # Inicializar pygame mixer con configuración de baja latencia
        pygame.mixer.pre_init(
            frequency=SAMPLE_RATE,
            size=-16,  # 16-bit signed
            channels=2,  # Stereo
            buffer=AUDIO_BUFFER_SIZE
        )
        pygame.mixer.init()
        pygame.mixer.set_num_channels(AUDIO_CHANNELS)
        
        # Volúmenes
        self.master_volume = MASTER_VOLUME_DEFAULT
        self.instrument_volumes = [INSTRUMENT_VOLUME_DEFAULT] * len(INSTRUMENTS)
        
        # Procesador de audio
        self.processor = AudioProcessor()
        self.processor.set_master_gain(AUDIO_GAIN_BOOST)
        
        # Cargar samples
        self.samples = {}
        self._load_samples()
        
        print(f"Audio Engine inicializado: {SAMPLE_RATE}Hz, buffer {AUDIO_BUFFER_SIZE}")
        print(f"AudioProcessor: Ganancia master {AUDIO_GAIN_BOOST}x, Limitador activo")
    
    def _load_samples(self):
        """Cargar todos los samples de audio desde el directorio"""
        for i, instrument in enumerate(INSTRUMENTS):
            sample_path = os.path.join(SAMPLES_DIR, f"{instrument}.wav")
            
            if os.path.exists(sample_path):
                try:
                    self.samples[i] = pygame.mixer.Sound(sample_path)
                    print(f"Sample cargado: {instrument} ({sample_path})")
                except Exception as e:
                    print(f"Error cargando {sample_path}: {e}")
                    # Crear sonido silencioso como fallback
                    self.samples[i] = None
            else:
                print(f"Advertencia: Sample no encontrado: {sample_path}")
                self.samples[i] = None
    
    def play_sample(self, instrument_id, volume=None):
        """
        Reproducir un instrumento con procesamiento de audio
        
        Args:
            instrument_id: ID del instrumento (0-7)
            volume: Volumen específico (0.0-1.0), None usa el volumen del instrumento
        """
        if instrument_id not in self.samples or self.samples[instrument_id] is None:
            return
        
        # Calcular volumen final
        if volume is None:
            volume = self.instrument_volumes[instrument_id]
        
        final_volume = volume * self.master_volume
        
        # Obtener sample original
        original_sound = self.samples[instrument_id]
        
        # Procesar con AudioProcessor (aplica ganancia y limitador)
        try:
            processed_sound = self.processor.process_sample(
                original_sound,
                final_volume,
                gain=1.0
            )
            processed_sound.play()
        except Exception as e:
            # Fallback: reproducir sin procesamiento
            print(f"Error procesando audio: {e}, usando fallback")
            original_sound.set_volume(min(1.0, final_volume))
            original_sound.play()
    
    def set_master_volume(self, volume):
        """
        Establecer volumen master
        Ahora puede ser > 1.0 gracias al procesador
        
        Args:
            volume: Volumen (0.0-2.0 o más)
        """
        self.master_volume = max(0.0, min(2.0, volume))
    
    def set_instrument_volume(self, instrument_id, volume):
        """
        Establecer volumen de un instrumento específico
        Ahora puede ser > 1.0
        
        Args:
            instrument_id: ID del instrumento (0-7)
            volume: Volumen (0.0-2.0 o más)
        """
        if 0 <= instrument_id < len(INSTRUMENTS):
            self.instrument_volumes[instrument_id] = max(0.0, min(2.0, volume))
    
    def get_instrument_volume(self, instrument_id):
        """Obtener volumen de un instrumento"""
        if 0 <= instrument_id < len(INSTRUMENTS):
            return self.instrument_volumes[instrument_id]
        return 0.0
    
    def stop_all(self):
        """Detener todos los sonidos"""
        pygame.mixer.stop()
    
    def cleanup(self):
        """Limpiar recursos de audio"""
        self.stop_all()
        pygame.mixer.quit()

