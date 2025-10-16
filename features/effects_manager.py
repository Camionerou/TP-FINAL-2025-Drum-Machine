"""
Effects Manager - Sistema de efectos simplificado
Solo Compresor y Reverb de alta calidad
"""

import numpy as np


class EffectsManager:
    """Gestor de efectos de audio simplificado - Solo Compresor y Reverb"""
    
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
        
        # Control de frecuencia de procesamiento
        self.last_process_time = 0
        self.process_interval = 0.05  # 50ms para mejor responsividad
        
        # Buffers para reverb
        self.reverb_buffer = np.zeros(int(0.5 * sample_rate))  # 500ms buffer
        self.reverb_pos = 0
    
    def has_active_effects(self):
        """Verificar si hay efectos activos"""
        return self.intensity > 5 or self.compressor_mix > 5 or self.reverb_mix > 5
    
    def get_intensity(self):
        """Obtener intensidad actual"""
        return self.intensity
    
    def set_compressor_mix(self, mix):
        """Establecer mix del compresor (0-100)"""
        self.compressor_mix = max(0, min(100, mix))
    
    def set_reverb_mix(self, mix):
        """Establecer mix del reverb (0-100)"""
        self.reverb_mix = max(0, min(100, mix))
    
    def set_intensity(self, intensity):
        """Establecer intensidad general (0-100)"""
        self.intensity = max(0, min(100, intensity))
    
    def process(self, audio_data):
        """
        Aplicar efectos al audio de forma optimizada
        
        Args:
            audio_data: numpy array del audio
            
        Returns:
            Audio procesado con efectos
        """
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        
        # Control de frecuencia de procesamiento
        import time
        current_time = time.time()
        if current_time - self.last_process_time < self.process_interval:
            return audio_data
        
        self.last_process_time = current_time
        
        # Si intensidad es muy baja, no aplicar efectos
        if self.intensity <= 5:
            return audio_data
        
        # Calcular factor de intensidad (0-1)
        intensity_factor = self.intensity / 100.0
        
        # Solo procesar si hay efectos activos significativos
        total_mix = (self.compressor_mix + self.reverb_mix) / 100.0
        
        if total_mix < 0.1:
            return audio_data
        
        # Preservar dimensiones originales del audio
        original_shape = audio_data.shape
        
        # Audio original (dry) y procesado (wet)
        dry = audio_data.copy()
        wet = audio_data.copy()
        
        # Aplicar compresor primero
        if self.compressor_mix > 10:
            wet = self._apply_compressor(wet)
        
        # Aplicar reverb después
        if self.reverb_mix > 10:
            wet = self._apply_reverb(wet)
        
        # Mix dry/wet con intensidad general
        processed = dry * (1.0 - intensity_factor) + wet * intensity_factor
        
        return processed
    
    def _apply_compressor(self, audio):
        """Compresor de alta calidad"""
        # Preservar dimensiones originales
        original_shape = audio.shape
        
        # Trabajar con audio plano para procesamiento
        if audio.ndim > 1:
            audio_flat = audio.flatten()
        else:
            audio_flat = audio
        
        # Compresor con lookahead y suavizado
        threshold = self.compressor_threshold
        ratio = self.compressor_ratio
        attack = 0.01  # 10ms attack
        release = 0.1  # 100ms release
        
        # Calcular ganancia de compresión
        gain_reduction = np.zeros_like(audio_flat)
        
        for i in range(len(audio_flat)):
            # Detectar nivel de señal
            level = abs(audio_flat[i])
            
            if level > threshold:
                # Calcular reducción de ganancia
                excess = level - threshold
                reduction = excess * (1 - 1/ratio)
                
                # Aplicar attack/release
                if i > 0:
                    prev_reduction = gain_reduction[i-1]
                    if reduction > prev_reduction:
                        # Attack
                        gain_reduction[i] = prev_reduction + (reduction - prev_reduction) * attack
                    else:
                        # Release
                        gain_reduction[i] = prev_reduction + (reduction - prev_reduction) * release
                else:
                    gain_reduction[i] = reduction
            else:
                if i > 0:
                    # Release cuando está por debajo del threshold
                    gain_reduction[i] = gain_reduction[i-1] * (1 - release)
                else:
                    gain_reduction[i] = 0
        
        # Aplicar compresión
        compressed = audio_flat.copy()
        mask = gain_reduction > 0
        if np.any(mask):
            compressed[mask] = np.sign(audio_flat[mask]) * (
                np.abs(audio_flat[mask]) - gain_reduction[mask]
            )
        
        # Mix con el original
        wet = self.compressor_mix / 100.0
        processed_flat = audio_flat * (1.0 - wet) + compressed * wet
        
        # Restaurar dimensiones originales
        return processed_flat.reshape(original_shape)
    
    def _apply_reverb(self, audio):
        """Reverb de alta calidad con algoritmo de sala"""
        # Preservar dimensiones originales
        original_shape = audio.shape
        
        # Trabajar con audio plano para procesamiento
        if audio.ndim > 1:
            audio_flat = audio.flatten()
        else:
            audio_flat = audio
        
        # Parámetros del reverb
        room_size = self.reverb_room_size
        damping = self.reverb_damping
        
        # Calcular delays para diferentes reflexiones
        delays = [
            int(0.03 * self.sample_rate),  # 30ms
            int(0.05 * self.sample_rate),  # 50ms
            int(0.07 * self.sample_rate),  # 70ms
            int(0.11 * self.sample_rate),  # 110ms
            int(0.13 * self.sample_rate),  # 130ms
        ]
        
        # Aplicar reverb con múltiples delays
        reverb_out = np.zeros_like(audio_flat)
        
        for delay_samples in delays:
            if delay_samples < len(audio_flat):
                # Crear señal retardada
                delayed = np.concatenate([
                    np.zeros(delay_samples),
                    audio_flat[:-delay_samples]
                ])
                
                # Aplicar damping (filtro pasa-bajos)
                if len(delayed) > 1:
                    alpha = damping
                    filtered = np.zeros_like(delayed)
                    filtered[0] = delayed[0]
                    
                    for i in range(1, len(delayed)):
                        filtered[i] = alpha * delayed[i] + (1 - alpha) * filtered[i-1]
                    
                    delayed = filtered
                
                # Mix con la señal original
                reverb_out += delayed * room_size * 0.2
        
        # Limitar el reverb para evitar feedback excesivo
        reverb_out = np.clip(reverb_out, -1.0, 1.0)
        
        # Mix con el original
        wet = self.reverb_mix / 100.0
        processed_flat = audio_flat * (1.0 - wet) + reverb_out * wet
        
        # Restaurar dimensiones originales
        return processed_flat.reshape(original_shape)
    
    def reset_all(self):
        """Resetear todos los efectos"""
        self.compressor_mix = 0.0
        self.reverb_mix = 0.0
        self.intensity = 0.0
        self.reverb_buffer.fill(0)
        self.reverb_pos = 0