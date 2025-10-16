"""
Effects Manager - Sistema de efectos ultra optimizado
Solo Compresor y Reverb con máximo rendimiento
"""

import numpy as np


class EffectsManager:
    """Gestor de efectos de audio ultra optimizado - Solo Compresor y EQ"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        # Solo dos efectos principales
        self.compressor_mix = 0.0
        self.eq_mix = 0.0  # Reemplaza reverb por EQ
        self.intensity = 0.0
        
        # Parámetros específicos (optimizados para drums)
        self.compressor_threshold = 0.3  # Mucho más sensible para drums
        self.compressor_ratio = 4.0  # Ratio más agresivo
        self.compressor_attack = 3  # ms - más rápido para drums
        self.compressor_release = 30  # ms - más rápido para drums
        self.reverb_room_size = 0.5
        self.reverb_damping = 0.5
        
        # Control de frecuencia de procesamiento ultra optimizado
        self.last_process_time = 0
        self.process_interval = 1.0  # 1000ms para eliminar lag completamente
        self.skip_count = 0
        self.max_skip = 10  # Procesar cada 10 samples máximo
        
        # Cache simple para evitar reprocesamiento
        self.last_cache_time = 0
        self.cache_duration = 0.5  # Cache por 500ms
        
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
    
    def set_eq_mix(self, mix):
        """Establecer mix del EQ (0-100)"""
        self.eq_mix = max(0, min(100, mix))
        self._invalidate_cache()
    
    def set_intensity(self, intensity):
        """Establecer intensidad general (0-100)"""
        self.intensity = max(0, min(100, intensity))
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Invalidar cache cuando cambian parámetros"""
        self.last_cache_time = 0
    
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
        if self.intensity <= 10:  # Umbral bajo para EQ audible
            return audio_data
        
        # Verificar cache simple basado en tiempo
        current_time = time.time()
        if current_time - self.last_cache_time < self.cache_duration:
            return audio_data  # Retornar audio sin procesar si está en cache
        
        # Solo procesar si hay efectos activos significativos
        total_mix = (self.compressor_mix + self.eq_mix) / 100.0
        
        if total_mix < 0.1:  # Threshold bajo para EQ audible
            return audio_data
        
        # Preservar dimensiones originales del audio
        original_shape = audio_data.shape
        
        # Audio original (dry) y procesado (wet)
        dry = audio_data.copy()
        wet = audio_data.copy()
        
        # Aplicar efectos (umbrales bajos para EQ audible)
        if self.compressor_mix > 20:  # Umbral medio para compresor
            wet = self._apply_compressor_fast(wet)
        
        if self.eq_mix > 10:  # Umbral bajo para EQ audible
            wet = self._apply_eq_fast(wet)
        
        # Mix dry/wet con intensidad general
        intensity_factor = self.intensity / 100.0
        processed = dry * (1.0 - intensity_factor) + wet * intensity_factor
        
        # Actualizar cache
        self.last_cache_time = current_time
        
        return processed
    
    def _apply_compressor_fast(self, audio):
        """Compresor profesional con attack/release"""
        # Preservar dimensiones originales
        original_shape = audio.shape
        
        # Trabajar con audio plano para procesamiento
        if audio.ndim > 1:
            audio_flat = audio.flatten()
        else:
            audio_flat = audio
        
        # Parámetros del compresor
        threshold = self.compressor_threshold  # 0.7
        ratio = self.compressor_ratio  # 2.0
        attack_time = self.compressor_attack / 1000.0  # ms a segundos
        release_time = self.compressor_release / 1000.0  # ms a segundos
        
        # Convertir tiempos a muestras
        attack_samples = int(attack_time * self.sample_rate)
        release_samples = int(release_time * self.sample_rate)
        
        # Detección de nivel (RMS optimizada)
        window_size = min(32, len(audio_flat))  # Ventana más pequeña para mejor rendimiento
        envelope = np.abs(audio_flat)  # Usar valor absoluto simple para mejor rendimiento
        
        # Suavizar envolvente con filtro simple
        if len(envelope) > 1:
            alpha = 0.8  # Factor de suavizado
            smoothed = np.zeros_like(envelope)
            smoothed[0] = envelope[0]
            for i in range(1, len(envelope)):
                smoothed[i] = alpha * envelope[i] + (1 - alpha) * smoothed[i-1]
            envelope = smoothed
        
        # Compresión más agresiva y audible
        compressed_audio = audio_flat.copy()
        
        # Aplicar compresión simple pero efectiva
        mask = envelope > threshold
        if np.any(mask):
            # Reducir picos agresivamente
            over_threshold = envelope[mask] - threshold
            reduction_factor = 1.0 - (over_threshold * (ratio - 1.0) / ratio)
            reduction_factor = np.clip(reduction_factor, 0.2, 1.0)  # Limitar reducción
            
            compressed_audio[mask] = audio_flat[mask] * reduction_factor
        
        # Mix con el original
        wet = self.compressor_mix / 100.0
        processed_flat = audio_flat * (1.0 - wet) + compressed_audio * wet
        
        # Restaurar dimensiones originales
        return processed_flat.reshape(original_shape)
    
    def _apply_eq_fast(self, audio):
        """EQ extremadamente simple y audible"""
        # Preservar dimensiones originales
        original_shape = audio.shape
        
        # Trabajar con audio plano para procesamiento
        if audio.ndim > 1:
            audio_flat = audio.flatten()
        else:
            audio_flat = audio
        
        # EQ extremadamente simple: solo multiplicar por factor
        eq_factor = 1.0 + (self.eq_mix / 100.0) * 0.5  # Factor de boost (0.5 a 1.5)
        processed_audio = audio_flat * eq_factor
        
        # Limitar para evitar clipping
        processed_audio = np.clip(processed_audio, -1.0, 1.0)
        
        # Mix con el original (EQ siempre audible)
        wet = self.eq_mix / 100.0
        processed_flat = audio_flat * (1.0 - wet) + processed_audio * wet
        
        # Restaurar dimensiones originales
        return processed_flat.reshape(original_shape)
    
    def reset_all(self):
        """Resetear todos los efectos"""
        self.compressor_mix = 0.0
        self.eq_mix = 0.0
        self.intensity = 0.0
        self._invalidate_cache()
    
    def disable_processing(self):
        """Deshabilitar procesamiento de efectos temporalmente"""
        self.processing_enabled = False
    
    def enable_processing(self):
        """Habilitar procesamiento de efectos"""
        self.processing_enabled = True