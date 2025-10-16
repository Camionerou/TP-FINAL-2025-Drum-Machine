"""
Effects Manager - Sistema de efectos de audio master
Reverb, Delay, Compressor, Filter, Distortion
"""

import numpy as np


class EffectsManager:
    """Gestor de efectos de audio para salida master"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        # Mix de cada efecto (0-100%)
        self.reverb_mix = 0.0
        self.delay_mix = 0.0
        self.compressor_mix = 0.0
        self.filter_mix = 0.0
        self.saturation_mix = 0.0
        
        # Intensidad general (0-100%)
        self.intensity = 0.0
        
        # Parámetros internos de efectos
        self.delay_time = 0.3          # 300ms fijo
        self.delay_feedback = 0.3
        self.compressor_threshold = 0.7
        self.compressor_ratio = 2.0
        self.filter_cutoff = 0.7       # 7kHz fijo
        self.filter_type = 'lowpass'
        self.saturation_drive = 0.5    # Drive fijo
        
        # Buffer para delay
        self.delay_buffer_size = int(0.5 * sample_rate)  # 500ms max
        self.delay_buffer = np.zeros(self.delay_buffer_size)
        self.delay_write_pos = 0
        
        # Control de frecuencia de procesamiento para evitar lag
        self.last_process_time = 0
        self.process_interval = 0.1  # Procesar máximo cada 100ms
    
    def process(self, audio_data):
        """
        Aplicar cadena de efectos al audio de forma optimizada
        
        Args:
            audio_data: numpy array del audio
            
        Returns:
            Audio procesado con efectos
        """
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        
        # Control de frecuencia de procesamiento para evitar lag
        import time
        current_time = time.time()
        if current_time - self.last_process_time < self.process_interval:
            return audio_data  # Saltar procesamiento si es muy frecuente
        
        self.last_process_time = current_time
        
        # Si intensidad es muy baja, no aplicar efectos para evitar lag
        if self.intensity <= 5:
            return audio_data
        
        # Calcular factor de intensidad (0-1)
        intensity_factor = self.intensity / 100.0
        
        # Solo procesar si hay efectos activos significativos
        total_mix = (self.reverb_mix + self.delay_mix + self.compressor_mix + 
                    self.filter_mix + self.saturation_mix) / 100.0
        
        if total_mix < 0.1:  # Menos del 10% de mix total
            return audio_data
        
        # Asegurar que el audio sea 1D
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()
        
        # Audio original (dry) y procesado (wet)
        dry = audio_data.copy()
        wet = audio_data.copy()
        
        # Aplicar efectos de forma optimizada (máximo 3 efectos simultáneos)
        effects_applied = 0
        max_effects = 3  # Aumentar a 3 para incluir más efectos
        
        # Priorizar efectos más importantes
        if self.reverb_mix > 10 and effects_applied < max_effects:
            wet = self._apply_reverb_simple(wet)
            effects_applied += 1
        
        if self.delay_mix > 10 and effects_applied < max_effects:
            wet = self._apply_delay_simple(wet)
            effects_applied += 1
        
        if self.compressor_mix > 10 and effects_applied < max_effects:
            wet = self._apply_compressor_simple(wet)
            effects_applied += 1
        
        if self.filter_mix > 10 and effects_applied < max_effects:
            wet = self._apply_filter_simple(wet)
            effects_applied += 1
        
        if self.saturation_mix > 10 and effects_applied < max_effects:
            wet = self._apply_saturation_simple(wet)
            effects_applied += 1
        
        # Mix dry/wet con intensidad general
        processed = dry * (1.0 - intensity_factor) + wet * intensity_factor
        
        return processed
    
    def _apply_reverb_simple(self, audio):
        """Reverb simplificado para evitar lag"""
        # Asegurar que sea 1D
        if audio.ndim > 1:
            audio = audio.flatten()
        
        # Reverb muy simple: solo un delay corto con feedback bajo
        delay_samples = int(0.03 * self.sample_rate)  # 30ms
        delay_samples = min(delay_samples, len(audio) - 1)
        
        if delay_samples > 0:
            # Aplicar delay simple
            delayed = np.concatenate([np.zeros(delay_samples), audio[:-delay_samples]])
            # Mix con feedback bajo
            feedback = 0.3
            wet = self.reverb_mix / 100.0
            return audio * (1.0 - wet) + delayed * wet * feedback
        
        return audio
    
    def _apply_delay_simple(self, audio):
        """Delay simplificado para evitar lag"""
        # Asegurar que sea 1D
        if audio.ndim > 1:
            audio = audio.flatten()
        
        # Delay simple sin buffer circular
        delay_samples = int(self.delay_time * 0.3 * self.sample_rate)  # Max 300ms
        delay_samples = min(delay_samples, len(audio) - 1)
        
        if delay_samples > 0:
            # Aplicar delay simple
            delayed = np.concatenate([np.zeros(delay_samples), audio[:-delay_samples]])
            # Mix con feedback bajo
            feedback = 0.2
            wet = self.delay_mix / 100.0
            return audio * (1.0 - wet) + delayed * wet * feedback
        
        return audio
    
    def _apply_compressor_simple(self, audio):
        """Compresor simplificado para evitar lag"""
        # Asegurar que sea 1D
        if audio.ndim > 1:
            audio = audio.flatten()
        
        # Compresión simple: reducir picos altos
        threshold = 0.7
        ratio = 2.0
        
        # Aplicar compresión solo a picos altos
        compressed = audio.copy()
        mask = np.abs(audio) > threshold
        
        if np.any(mask):
            # Reducir picos por el ratio
            compressed[mask] = np.sign(audio[mask]) * (
                threshold + (np.abs(audio[mask]) - threshold) / ratio
            )
        
        # Mix con el original
        wet = self.compressor_mix / 100.0
        return audio * (1.0 - wet) + compressed * wet
    
    def _apply_filter_simple(self, audio):
        """Filtro simplificado para evitar lag"""
        # Asegurar que sea 1D
        if audio.ndim > 1:
            audio = audio.flatten()
        
        # Filtro low-pass simple de un polo
        cutoff_hz = 200 + (self.filter_cutoff * 7800)  # 200Hz - 8kHz
        alpha = min(2.0 * np.pi * cutoff_hz / self.sample_rate, 1.0)
        
        # Aplicar filtro simple
        filtered = np.zeros_like(audio)
        filtered[0] = audio[0]
        
        for i in range(1, len(audio)):
            filtered[i] = alpha * audio[i] + (1 - alpha) * filtered[i-1]
        
        # Mix con el original
        wet = self.filter_mix / 100.0
        return audio * (1.0 - wet) + filtered * wet
    
    def _apply_saturation_simple(self, audio):
        """Saturación simplificada para evitar lag"""
        # Asegurar que sea 1D
        if audio.ndim > 1:
            audio = audio.flatten()
        
        # Saturación simple usando tanh
        drive = 1.0 + (self.saturation_drive * 2.0)  # 1.0 a 3.0
        driven = audio * drive
        
        # Aplicar saturación
        saturated = np.tanh(driven) / np.tanh(drive)
        
        # Mix con el original
        wet = self.saturation_mix / 100.0
        return audio * (1.0 - wet) + saturated * wet
    
    def _apply_compressor(self, audio):
        """Compresor dinámico simple"""
        threshold = self.compressor_threshold
        ratio = self.compressor_ratio
        
        # Detectar envolvente
        envelope = np.abs(audio)
        
        # Aplicar compresión solo sobre threshold
        mask = envelope > threshold
        compressed = audio.copy()
        
        if np.any(mask):
            # Reducir ganancia sobre threshold
            over_amount = envelope[mask] - threshold
            reduction = over_amount * (1 - 1/ratio)
            compressed[mask] = np.sign(audio[mask]) * (threshold + over_amount - reduction)
        
        return compressed
    
    def _apply_saturation(self, audio):
        """Saturación/distorsión suave"""
        drive = 1.0 + (self.saturation_drive * 3.0)  # 1.0 a 4.0
        driven = audio * drive
        return np.tanh(driven) / np.tanh(drive)  # Normalizar
    
    def _apply_filter(self, audio):
        """Filtro simple low-pass"""
        # Cutoff mapea a frecuencia (200Hz - 8kHz)
        cutoff_hz = 200 + (self.filter_cutoff * 7800)
        
        # Simple one-pole low-pass filter
        alpha = 2.0 * np.pi * cutoff_hz / self.sample_rate
        alpha = min(alpha, 1.0)
        
        filtered = np.zeros_like(audio)
        filtered[0] = audio[0]
        
        for i in range(1, len(audio)):
            filtered[i] = filtered[i-1] + alpha * (audio[i] - filtered[i-1])
        
        return filtered
    
    def _apply_delay(self, audio):
        """Delay con feedback"""
        delay_samples = int(self.delay_time * 0.5 * self.sample_rate)  # Max 500ms
        delay_samples = max(1, min(delay_samples, self.delay_buffer_size - 1))
        
        output = audio.copy()
        
        for i in range(len(audio)):
            # Leer del buffer con delay
            read_pos = (self.delay_write_pos - delay_samples) % self.delay_buffer_size
            delayed_sample = self.delay_buffer[read_pos]
            
            # Mix con señal original
            output[i] = audio[i] + delayed_sample * 0.5
            
            # Escribir al buffer con feedback
            self.delay_buffer[self.delay_write_pos] = (
                audio[i] + delayed_sample * self.delay_feedback
            )
            
            self.delay_write_pos = (self.delay_write_pos + 1) % self.delay_buffer_size
        
        return output
    
    def _apply_reverb(self, audio):
        """Reverb simple basado en comb filters"""
        # Delays para simular reverb (en samples)
        delays = [
            int(0.0297 * self.sample_rate),
            int(0.0371 * self.sample_rate),
            int(0.0411 * self.sample_rate),
            int(0.0437 * self.sample_rate)
        ]
        
        decays = [0.7, 0.6, 0.5, 0.4]
        
        reverb_signal = np.zeros_like(audio)
        
        for delay, decay in zip(delays, decays):
            if delay < len(audio):
                delayed = np.concatenate([np.zeros(delay), audio[:-delay]])
                reverb_signal += delayed * decay
        
        # Mix dry/wet
        wet = self.reverb_mix / 100.0
        dry = 1.0 - wet * 0.5  # No reducir tanto el dry
        
        return audio * dry + reverb_signal * wet
    
    
    # Métodos para control de mix e intensidad
    def set_reverb_mix(self, mix):
        """Establecer mix de reverb (0-100%)"""
        self.reverb_mix = max(0.0, min(100.0, mix))
    
    def set_delay_mix(self, mix):
        """Establecer mix de delay (0-100%)"""
        self.delay_mix = max(0.0, min(100.0, mix))
    
    def set_compressor_mix(self, mix):
        """Establecer mix de compressor (0-100%)"""
        self.compressor_mix = max(0.0, min(100.0, mix))
    
    def set_filter_mix(self, mix):
        """Establecer mix de filter (0-100%)"""
        self.filter_mix = max(0.0, min(100.0, mix))
    
    def set_saturation_mix(self, mix):
        """Establecer mix de saturation (0-100%)"""
        self.saturation_mix = max(0.0, min(100.0, mix))
    
    def set_intensity(self, intensity):
        """Establecer intensidad general (0-100%)"""
        self.intensity = max(0.0, min(100.0, intensity))
    
    def get_intensity(self):
        """Obtener intensidad general actual"""
        return self.intensity
    
    def has_active_effects(self):
        """Verificar si hay algún efecto activo"""
        return (self.reverb_mix > 1.0 or
                self.delay_mix > 1.0 or
                self.saturation_mix > 1.0 or
                self.filter_mix > 1.0 or
                self.compressor_mix > 1.0 or
                self.intensity > 1.0)
    
    def get_status(self):
        """Obtener estado de todos los efectos"""
        return {
            'reverb_mix': int(self.reverb_mix),
            'delay_mix': int(self.delay_mix),
            'compressor_mix': int(self.compressor_mix),
            'filter_mix': int(self.filter_mix),
            'saturation_mix': int(self.saturation_mix),
            'intensity': int(self.intensity)
        }
    
    def reset_all(self):
        """Resetear todos los efectos a 0"""
        self.reverb_mix = 0.0
        self.delay_mix = 0.0
        self.compressor_mix = 0.0
        self.filter_mix = 0.0
        self.saturation_mix = 0.0
        self.intensity = 0.0
        self.compressor_ratio = 1.0
        self.delay_buffer.fill(0)

