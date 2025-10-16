"""
Sistema de procesamiento de audio para la Drum Machine
Permite control fino de volumen, ganancia, limitador y futuros efectos
"""

import numpy as np
import pygame

try:
    from features.effects_manager import EffectsManager
    EFFECTS_AVAILABLE = True
except ImportError:
    EFFECTS_AVAILABLE = False
    print("⚠️ EffectsManager no disponible")


class AudioProcessor:
    """Procesador de audio optimizado con ganancia, limitador y efectos"""
    
    def __init__(self):
        """Inicializar procesador de audio optimizado"""
        self.master_gain = 2.0
        self.limiter_threshold = 0.95
        self.limiter_enabled = True
        
        # Effects manager optimizado
        if EFFECTS_AVAILABLE:
            self.effects = EffectsManager(sample_rate=44100)
            print("✅ AudioProcessor + EffectsManager (Compresor + Reverb) inicializados")
        else:
            self.effects = None
            print("⚠️ AudioProcessor sin efectos")
        
        # Cache para optimización
        self._last_processed_shape = None
        self._processing_cache = {}
    
    def apply_gain(self, audio_data, gain):
        """
        Aplicar ganancia a datos de audio
        
        Args:
            audio_data: Array numpy con datos de audio
            gain: Factor de ganancia (1.0 = sin cambio, 2.0 = doble)
            
        Returns:
            Audio con ganancia aplicada
        """
        return audio_data * gain
    
    def soft_limiter(self, audio_data, threshold=0.95):
        """
        Limitador suave para evitar clipping
        Usa compresión suave en lugar de hard clipping
        
        Args:
            audio_data: Array numpy con datos de audio
            threshold: Umbral (0.0-1.0)
            
        Returns:
            Audio limitado
        """
        # Soft clipping usando tanh (más musical que hard clip)
        limited = np.tanh(audio_data / threshold) * threshold
        return limited
    
    def hard_limiter(self, audio_data, threshold=1.0):
        """
        Limitador duro (hard clipping)
        
        Args:
            audio_data: Array numpy
            threshold: Umbral máximo
            
        Returns:
            Audio limitado
        """
        return np.clip(audio_data, -threshold, threshold)
    
    def process_sample(self, sound, volume, gain=1.0):
        """
        Procesar un sample antes de reproducirlo (ultra optimizado)
        Aplica volumen, ganancia, limitador y efectos
        
        Args:
            sound: pygame.mixer.Sound object
            volume: Volumen (0.0-1.0)
            gain: Ganancia adicional (default 1.0)
            
        Returns:
            Sound procesado listo para reproducir
        """
        # Calcular ganancia total
        total_gain = volume * gain * self.master_gain
        
        # Si la ganancia es muy baja, usar método simple
        if total_gain < 0.01:
            sound.set_volume(min(1.0, total_gain))
            return sound
        
        # Si no hay efectos activos, usar procesamiento simple
        if not self.effects or not self.effects.has_active_effects():
            sound.set_volume(min(1.0, total_gain))
            return sound
        
        # Obtener datos del sample como array numpy
        try:
            sound_array = pygame.sndarray.array(sound)
            
            # Verificar tamaño del sample para evitar procesar samples muy largos
            if len(sound_array) > 44100:  # Más de 1 segundo
                sound.set_volume(min(1.0, total_gain))
                return sound
            
            # Convertir a float normalizado (-1.0 a 1.0) - ultra optimizado
            if sound_array.dtype == np.int16:
                audio_float = sound_array.astype(np.float32) * (1.0 / 32768.0)
            elif sound_array.dtype == np.uint8:
                audio_float = (sound_array.astype(np.float32) - 128.0) * (1.0 / 128.0)
            else:
                # Fallback simple
                sound.set_volume(min(1.0, total_gain))
                return sound
            
            # Aplicar volumen y ganancia
            processed = audio_float * total_gain
            
            # Aplicar limitador optimizado
            if self.limiter_enabled:
                processed = np.clip(processed, -self.limiter_threshold, self.limiter_threshold)
            else:
                processed = np.clip(processed, -1.0, 1.0)
            
            # Aplicar efectos master si están disponibles y activos
            if self.effects and self.effects.has_active_effects():
                processed = self.effects.process(processed)
            
            # Convertir de vuelta a formato original - ultra optimizado
            if sound_array.dtype == np.int16:
                processed_int = (processed * 32767.0).astype(np.int16)
            else:
                processed_int = (processed * 128.0 + 128.0).astype(np.uint8)
            
            # Crear nuevo Sound con audio procesado
            processed_sound = pygame.sndarray.make_sound(processed_int)
            
            return processed_sound
            
        except Exception as e:
            # Si falla el procesamiento, usar método simple
            print(f"Advertencia: Procesamiento avanzado falló ({e}), usando método simple")
            sound.set_volume(min(1.0, total_gain))
            return sound
    
    def set_master_gain(self, gain):
        """
        Establecer ganancia master
        
        Args:
            gain: Factor de ganancia (puede ser > 1.0)
        """
        self.master_gain = max(0.1, min(10.0, gain))  # Limitar entre 0.1x y 10x
    
    def set_limiter_threshold(self, threshold):
        """
        Establecer threshold del limitador
        
        Args:
            threshold: Umbral (0.0-1.0)
        """
        self.limiter_threshold = max(0.5, min(1.0, threshold))
    
    def enable_limiter(self, enabled):
        """Habilitar/deshabilitar limitador"""
        self.limiter_enabled = enabled

