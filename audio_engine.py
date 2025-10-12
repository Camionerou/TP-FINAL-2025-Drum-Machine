"""
Motor de audio para la Drum Machine usando pygame
Maneja la carga y reproducción de samples de batería
"""

import pygame
import os
from config import (
    INSTRUMENTS, SAMPLES_DIR, SAMPLE_RATE, AUDIO_BUFFER_SIZE, 
    AUDIO_CHANNELS, MASTER_VOLUME_DEFAULT, INSTRUMENT_VOLUME_DEFAULT
)


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
        
        # Cargar samples
        self.samples = {}
        self._load_samples()
        
        print(f"Audio Engine inicializado: {SAMPLE_RATE}Hz, buffer {AUDIO_BUFFER_SIZE}")
    
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
        Reproducir un instrumento
        
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
        
        # Reproducir el sample
        sound = self.samples[instrument_id]
        sound.set_volume(final_volume)
        sound.play()
    
    def set_master_volume(self, volume):
        """
        Establecer volumen master
        
        Args:
            volume: Volumen (0.0-1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_instrument_volume(self, instrument_id, volume):
        """
        Establecer volumen de un instrumento específico
        
        Args:
            instrument_id: ID del instrumento (0-7)
            volume: Volumen (0.0-1.0)
        """
        if 0 <= instrument_id < len(INSTRUMENTS):
            self.instrument_volumes[instrument_id] = max(0.0, min(1.0, volume))
    
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

