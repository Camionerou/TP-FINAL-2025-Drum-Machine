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
    
    def process(self, audio_data):
        """
        Aplicar cadena de efectos al audio con mix e intensidad
        
        Args:
            audio_data: numpy array del audio
            
        Returns:
            Audio procesado con efectos
        """
        if audio_data is None or len(audio_data) == 0:
            return audio_data
        
        # Si intensidad es 0, no aplicar efectos
        if self.intensity <= 0:
            return audio_data
        
        # Calcular factor de intensidad (0-1)
        intensity_factor = self.intensity / 100.0
        
        # Audio original (dry) y procesado (wet)
        dry = audio_data.copy()
        wet = audio_data.copy()
        
        # Aplicar efectos solo si tienen mix > 0
        # 1. Compressor
        if self.compressor_mix > 0:
            wet = self._apply_compressor(wet)
        
        # 2. Saturation
        if self.saturation_mix > 0:
            wet = self._apply_saturation(wet)
        
        # 3. Filter
        if self.filter_mix > 0:
            wet = self._apply_filter(wet)
        
        # 4. Delay
        if self.delay_mix > 0:
            wet = self._apply_delay(wet)
        
        # 5. Reverb
        if self.reverb_mix > 0:
            wet = self._apply_reverb(wet)
        
        # Mix dry/wet con intensidad general
        # Cada efecto contribuye según su mix individual
        # Intensidad general controla el balance total
        processed = dry * (1.0 - intensity_factor) + wet * intensity_factor
        
        return processed
    
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
        wet = self.reverb_level
        dry = 1.0 - wet * 0.5  # No reducir tanto el dry
        
        return audio * dry + reverb_signal * wet
    
    def set_reverb(self, level):
        """Establecer nivel de reverb (0.0-1.0)"""
        self.reverb_level = max(0.0, min(1.0, level))
    
    def set_delay(self, time, feedback=None):
        """
        Establecer delay
        
        Args:
            time: Tiempo de delay (0.0-1.0)
            feedback: Feedback (0.0-0.9), None mantiene actual
        """
        self.delay_time = max(0.0, min(1.0, time))
        if feedback is not None:
            self.delay_feedback = max(0.0, min(0.9, feedback))
    
    def set_compressor(self, threshold=None, ratio=None):
        """
        Configurar compresor
        
        Args:
            threshold: Umbral (0.0-1.0)
            ratio: Ratio de compresión (1.0-10.0)
        """
        if threshold is not None:
            self.compressor_threshold = max(0.0, min(1.0, threshold))
        if ratio is not None:
            self.compressor_ratio = max(1.0, min(10.0, ratio))
    
    def set_filter(self, cutoff, filter_type='lowpass'):
        """
        Configurar filtro
        
        Args:
            cutoff: Frecuencia de corte (0.0-1.0)
            filter_type: 'lowpass' o 'highpass'
        """
        self.filter_cutoff = max(0.0, min(1.0, cutoff))
        self.filter_type = filter_type
    
    def set_saturation(self, drive):
        """Establecer saturación (0.0-1.0)"""
        self.saturation_drive = max(0.0, min(1.0, drive))
    
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
        self.reverb_level = 0.0
        self.delay_time = 0.0
        self.filter_cutoff = 1.0
        self.saturation_drive = 0.0
        self.compressor_ratio = 1.0
        self.delay_buffer.fill(0)

