"""
Effects Manager - Sistema de efectos ultra optimizado
Solo Compresor y Reverb con máximo rendimiento
"""

import numpy as np


class EffectsManager:
    """Gestor de efectos de audio ultra optimizado - Solo Compresor y Reverb"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        # Solo dos efectos principales
        self.compressor_mix = 0.0
        self.reverb_mix = 0.0
        self.intensity = 0.0
        
        # Parámetros específicos
        self.compressor_threshold = 0.7
        self.compressor_ratio = 3.0
        self.reverb_room_size = 0.5
        self.reverb_damping = 0.5
        
        # Control de frecuencia de procesamiento ultra optimizado
        self.last_process_time = 0
        self.process_interval = 0.2  # 200ms para reducir carga
        self.skip_count = 0
        self.max_skip = 3  # Procesar cada 3 samples máximo
        
        # Cache para evitar reprocesamiento
        self.last_audio_hash = None
        self.cached_result = None
        
        # Buffers optimizados para reverb
        self.reverb_buffer = np.zeros(int(0.1 * sample_rate))  # Buffer más pequeño
        self.reverb_pos = 0
        
        # Estado de procesamiento
        self.processing_enabled = True
    
    def has_active_effects(self):
        """Verificar si hay efectos activos"""
        return self.intensity > 10 and (self.compressor_mix > 10 or self.reverb_mix > 10)
    
    def get_intensity(self):
        """Obtener intensidad actual"""
        return self.intensity
    
    def set_compressor_mix(self, mix):
        """Establecer mix del compresor (0-100)"""
        self.compressor_mix = max(0, min(100, mix))
        self._invalidate_cache()
    
    def set_reverb_mix(self, mix):
        """Establecer mix del reverb (0-100)"""
        self.reverb_mix = max(0, min(100, mix))
        self._invalidate_cache()
    
    def set_intensity(self, intensity):
        """Establecer intensidad general (0-100)"""
        self.intensity = max(0, min(100, intensity))
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Invalidar cache cuando cambian parámetros"""
        self.last_audio_hash = None
        self.cached_result = None
    
    def _get_audio_hash(self, audio_data):
        """Obtener hash simple del audio para cache"""
        if len(audio_data) > 100:
            # Usar solo algunos puntos para el hash
            return hash(tuple(audio_data[::len(audio_data)//10]))
        return hash(tuple(audio_data))
    
    def process(self, audio_data):
        """
        Aplicar efectos al audio de forma ultra optimizada
        
        Args:
            audio_data: numpy array del audio
            
        Returns:
            Audio procesado con efectos
        """
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        
        # Deshabilitar procesamiento si es muy intensivo
        if not self.processing_enabled:
            return audio_data
        
        # Control de frecuencia ultra optimizado
        import time
        current_time = time.time()
        if current_time - self.last_process_time < self.process_interval:
            return audio_data
        
        # Skip processing para reducir carga
        self.skip_count += 1
        if self.skip_count < self.max_skip:
            return audio_data
        self.skip_count = 0
        
        self.last_process_time = current_time
        
        # Si intensidad es muy baja, no aplicar efectos
        if self.intensity <= 10:
            return audio_data
        
        # Verificar cache
        audio_hash = self._get_audio_hash(audio_data)
        if audio_hash == self.last_audio_hash and self.cached_result is not None:
            return self.cached_result
        
        # Solo procesar si hay efectos activos significativos
        total_mix = (self.compressor_mix + self.reverb_mix) / 100.0
        
        if total_mix < 0.2:  # Threshold más alto
            return audio_data
        
        # Preservar dimensiones originales del audio
        original_shape = audio_data.shape
        
        # Audio original (dry) y procesado (wet)
        dry = audio_data.copy()
        wet = audio_data.copy()
        
        # Aplicar efectos de forma ultra simplificada
        if self.compressor_mix > 20:
            wet = self._apply_compressor_fast(wet)
        
        if self.reverb_mix > 20:
            wet = self._apply_reverb_fast(wet)
        
        # Mix dry/wet con intensidad general
        intensity_factor = self.intensity / 100.0
        processed = dry * (1.0 - intensity_factor) + wet * intensity_factor
        
        # Cache del resultado
        self.last_audio_hash = audio_hash
        self.cached_result = processed.copy()
        
        return processed
    
    def _apply_compressor_fast(self, audio):
        """Compresor ultra rápido y simplificado"""
        # Preservar dimensiones originales
        original_shape = audio.shape
        
        # Trabajar con audio plano para procesamiento
        if audio.ndim > 1:
            audio_flat = audio.flatten()
        else:
            audio_flat = audio
        
        # Compresión ultra simple
        threshold = self.compressor_threshold
        ratio = self.compressor_ratio
        
        # Aplicar compresión solo a picos altos
        compressed = audio_flat.copy()
        mask = np.abs(audio_flat) > threshold
        
        if np.any(mask):
            # Reducir picos por el ratio
            compressed[mask] = np.sign(audio_flat[mask]) * (
                threshold + (np.abs(audio_flat[mask]) - threshold) / ratio
            )
        
        # Mix con el original
        wet = self.compressor_mix / 100.0
        processed_flat = audio_flat * (1.0 - wet) + compressed * wet
        
        # Restaurar dimensiones originales
        return processed_flat.reshape(original_shape)
    
    def _apply_reverb_fast(self, audio):
        """Reverb ultra rápido y simplificado"""
        # Preservar dimensiones originales
        original_shape = audio.shape
        
        # Trabajar con audio plano para procesamiento
        if audio.ndim > 1:
            audio_flat = audio.flatten()
        else:
            audio_flat = audio
        
        # Reverb ultra simple con un solo delay
        delay_samples = int(0.05 * self.sample_rate)  # 50ms fijo
        delay_samples = min(delay_samples, len(audio_flat) - 1)
        
        if delay_samples > 0:
            # Crear señal retardada
            delayed = np.concatenate([
                np.zeros(delay_samples),
                audio_flat[:-delay_samples]
            ])
            
            # Mix con la señal original
            wet = self.reverb_mix / 100.0
            processed_flat = audio_flat * (1.0 - wet) + delayed * wet * 0.3
        else:
            processed_flat = audio_flat
        
        # Restaurar dimensiones originales
        return processed_flat.reshape(original_shape)
    
    def reset_all(self):
        """Resetear todos los efectos"""
        self.compressor_mix = 0.0
        self.reverb_mix = 0.0
        self.intensity = 0.0
        self.reverb_buffer.fill(0)
        self.reverb_pos = 0
        self._invalidate_cache()
    
    def disable_processing(self):
        """Deshabilitar procesamiento de efectos temporalmente"""
        self.processing_enabled = False
    
    def enable_processing(self):
        """Habilitar procesamiento de efectos"""
        self.processing_enabled = True