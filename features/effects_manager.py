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
        
        # Parámetros específicos (optimizados para drums)
        self.compressor_threshold = 0.5  # Más sensible para drums
        self.compressor_ratio = 3.0
        self.compressor_attack = 5  # ms - más rápido para drums
        self.compressor_release = 50  # ms - más rápido para drums
        self.reverb_room_size = 0.5
        self.reverb_damping = 0.5
        
        # Control de frecuencia de procesamiento ultra optimizado
        self.last_process_time = 0
        self.process_interval = 0.2  # 200ms para reducir carga
        self.skip_count = 0
        self.max_skip = 3  # Procesar cada 3 samples máximo
        
        # Cache simple para evitar reprocesamiento
        self.last_cache_time = 0
        self.cache_duration = 0.1  # Cache por 100ms
        
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
        if self.intensity <= 10:
            return audio_data
        
        # Verificar cache simple basado en tiempo
        current_time = time.time()
        if current_time - self.last_cache_time < self.cache_duration:
            return audio_data  # Retornar audio sin procesar si está en cache
        
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
        
        # Compresión con attack/release
        gain_reduction = np.zeros_like(audio_flat)
        current_gain = 1.0
        
        for i in range(len(audio_flat)):
            if envelope[i] > threshold:
                # Calcular reducción de ganancia necesaria
                over_threshold = envelope[i] - threshold
                target_gain = threshold / envelope[i] + (over_threshold / ratio) / envelope[i]
                target_gain = max(target_gain, 0.1)  # Limitar ganancia mínima
                
                # Attack: reducir ganancia rápidamente
                if target_gain < current_gain:
                    current_gain = max(target_gain, current_gain - (1.0 / attack_samples))
                else:
                    current_gain = target_gain
            else:
                # Release: recuperar ganancia gradualmente
                current_gain = min(1.0, current_gain + (1.0 / release_samples))
            
            gain_reduction[i] = current_gain
        
        # Aplicar compresión
        compressed_audio = audio_flat * gain_reduction
        
        # Mix con el original
        wet = self.compressor_mix / 100.0
        processed_flat = audio_flat * (1.0 - wet) + compressed_audio * wet
        
        # Restaurar dimensiones originales
        return processed_flat.reshape(original_shape)
    
    def _apply_reverb_fast(self, audio):
        """Reverb profesional con múltiples delays y feedback"""
        # Preservar dimensiones originales
        original_shape = audio.shape
        
        # Trabajar con audio plano para procesamiento
        if audio.ndim > 1:
            audio_flat = audio.flatten()
        else:
            audio_flat = audio
        
        # Múltiples delays para simular reflexiones naturales (optimizado)
        delay_times_ms = [40, 80, 120]  # ms - menos delays para mejor rendimiento
        feedback_gains = [0.6, 0.5, 0.4]  # Feedback más fuerte para reverb más audible
        
        processed_audio = audio_flat.copy()
        
        # Aplicar cada delay
        for delay_ms, feedback in zip(delay_times_ms, feedback_gains):
            delay_samples = int(delay_ms * 0.001 * self.sample_rate)
            delay_samples = min(delay_samples, len(audio_flat) - 1)
            
            if delay_samples > 0:
                # Crear señal retardada
                delayed = np.concatenate([
                    np.zeros(delay_samples),
                    audio_flat[:-delay_samples]
                ])
                
                # Aplicar feedback y sumar
                processed_audio += delayed * feedback
        
        # Filtro pasa-bajos para simular absorción (damping)
        alpha = 0.7  # Factor de suavizado
        filtered_audio = np.zeros_like(processed_audio)
        if len(processed_audio) > 0:
            filtered_audio[0] = processed_audio[0]
            for i in range(1, len(processed_audio)):
                filtered_audio[i] = alpha * processed_audio[i] + (1 - alpha) * filtered_audio[i-1]
        
        # Mix con el original (reverb más audible)
        wet = self.reverb_mix / 100.0
        processed_flat = audio_flat * (1.0 - wet) + filtered_audio * wet * 0.8
        
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