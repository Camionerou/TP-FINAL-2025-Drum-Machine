"""
Tap Tempo - Detector de tempo por golpes rítmicos
Permite establecer el BPM golpeando un botón al ritmo deseado
"""

import time


class TapTempo:
    """
    Detector de tap tempo para drum machine
    Calcula BPM promedio basado en intervalos entre taps
    """
    
    def __init__(self, min_taps=2, max_taps=8, timeout=3.0, bpm_min=60, bpm_max=200):
        """
        Inicializar tap tempo
        
        Args:
            min_taps: Mínimo de taps para calcular BPM
            max_taps: Máximo de taps a promediar
            timeout: Segundos antes de limpiar taps antiguos
            bpm_min: BPM mínimo válido
            bpm_max: BPM máximo válido
        """
        self.tap_times = []
        self.min_taps = min_taps
        self.max_taps = max_taps
        self.timeout = timeout
        self.bpm_min = bpm_min
        self.bpm_max = bpm_max
        
        self.active = False
        self.last_bpm = None
    
    def tap(self):
        """
        Registrar un tap y calcular BPM si es posible
        
        Returns:
            int: BPM calculado (o None si no hay suficientes taps)
        """
        current_time = time.time()
        
        # Limpiar taps antiguos (fuera del timeout)
        self.tap_times = [t for t in self.tap_times 
                          if current_time - t < self.timeout]
        
        # Agregar nuevo tap
        self.tap_times.append(current_time)
        
        # Limitar cantidad de taps guardados
        if len(self.tap_times) > self.max_taps:
            self.tap_times.pop(0)
        
        # Calcular BPM si hay suficientes taps
        if len(self.tap_times) >= self.min_taps:
            bpm = self._calculate_bpm()
            if bpm is not None:
                self.last_bpm = bpm
                return bpm
        
        return None
    
    def _calculate_bpm(self):
        """
        Calcular BPM basado en intervalos entre taps
        
        Returns:
            int: BPM calculado y validado
        """
        # Calcular intervalos entre taps consecutivos
        intervals = []
        for i in range(len(self.tap_times) - 1):
            interval = self.tap_times[i + 1] - self.tap_times[i]
            intervals.append(interval)
        
        if not intervals:
            return None
        
        # Calcular intervalo promedio
        avg_interval = sum(intervals) / len(intervals)
        
        # Convertir intervalo a BPM
        # BPM = (60 segundos / intervalo en segundos)
        bpm = 60.0 / avg_interval
        
        # Validar rango
        if self.bpm_min <= bpm <= self.bpm_max:
            return int(round(bpm))
        
        return None
    
    def get_tap_count(self):
        """Obtener cantidad de taps válidos registrados"""
        current_time = time.time()
        valid_taps = [t for t in self.tap_times 
                      if current_time - t < self.timeout]
        return len(valid_taps)
    
    def get_confidence(self):
        """
        Calcular confianza del BPM calculado
        
        Returns:
            float: Confianza (0.0-1.0) basada en cantidad de taps
        """
        tap_count = self.get_tap_count()
        if tap_count < self.min_taps:
            return 0.0
        
        # Máxima confianza con max_taps
        confidence = min(1.0, tap_count / self.max_taps)
        return confidence
    
    def is_active(self):
        """Verificar si hay taps recientes (modo activo)"""
        if not self.tap_times:
            return False
        
        current_time = time.time()
        last_tap = self.tap_times[-1]
        return (current_time - last_tap) < self.timeout
    
    def reset(self):
        """Limpiar todos los taps"""
        self.tap_times = []
        self.last_bpm = None
        self.active = False
    
    def get_status(self):
        """
        Obtener estado completo del tap tempo
        
        Returns:
            dict: Estado con taps, BPM, confianza, etc.
        """
        return {
            'active': self.is_active(),
            'tap_count': self.get_tap_count(),
            'bpm': self.last_bpm,
            'confidence': self.get_confidence(),
            'min_taps': self.min_taps,
            'max_taps': self.max_taps
        }
    
    def __repr__(self):
        status = self.get_status()
        return (f"TapTempo(taps={status['tap_count']}, "
                f"bpm={status['bpm']}, "
                f"confidence={status['confidence']:.1%}, "
                f"active={status['active']})")


# Test del módulo
if __name__ == "__main__":
    print("=== Test de Tap Tempo ===\n")
    
    tap = TapTempo(min_taps=2, max_taps=6, timeout=3.0)
    
    print("Simular taps a 120 BPM (intervalo de 0.5s):")
    print("Presiona Enter para simular cada tap, o 'q' para salir\n")
    
    try:
        while True:
            user_input = input(f"Tap #{tap.get_tap_count() + 1}: ")
            
            if user_input.lower() == 'q':
                break
            
            bpm = tap.tap()
            status = tap.get_status()
            
            print(f"  Taps: {status['tap_count']}/{tap.max_taps}")
            
            if bpm:
                print(f"  BPM: {bpm} (confianza: {status['confidence']:.1%})")
            else:
                print(f"  BPM: --- (necesitas {tap.min_taps - status['tap_count']} tap(s) más)")
            
            print()
            
            # Timeout automático
            if not tap.is_active():
                print("⏱️  Timeout - taps limpiados\n")
    
    except KeyboardInterrupt:
        print("\n\nTest terminado.")
        print(f"Estado final: {tap}")

