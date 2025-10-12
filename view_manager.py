"""
Sistema de gestión de vistas dinámicas para la Drum Machine
Maneja transiciones automáticas entre diferentes vistas en la matriz LED
"""

import time
from enum import Enum


class ViewType(Enum):
    """Tipos de vistas disponibles"""
    SEQUENCER = "sequencer"
    BPM = "bpm"
    VOLUME = "volume"
    SWING = "swing"
    PATTERN = "pattern"
    SAVE = "save"
    PAD = "pad"


class ViewManager:
    """Gestor de vistas con transiciones automáticas"""
    
    def __init__(self, default_timeout=2.0, inactivity_timeout=3.0):
        """
        Inicializar el gestor de vistas
        
        Args:
            default_timeout: Tiempo en segundos antes de volver a vista principal
            inactivity_timeout: Tiempo de inactividad para forzar vista SEQUENCER
        """
        self.current_view = ViewType.SEQUENCER
        self.default_timeout = default_timeout
        self.inactivity_timeout = inactivity_timeout
        
        # Control de timeouts
        self.view_start_time = 0
        self.view_duration = 0
        self.last_interaction_time = time.time()
        
        # Datos específicos de cada vista
        self.view_data = {}
        
        # Frame de animación para vistas animadas
        self.animation_frame = 0
        self.last_animation_update = time.time()
        
        print("ViewManager inicializado")
    
    def show_view(self, view_type, data=None, duration=None):
        """
        Mostrar una vista específica
        
        Args:
            view_type: ViewType a mostrar
            data: Datos específicos para la vista
            duration: Duración en segundos (None usa default, 0 = permanente)
        """
        self.current_view = view_type
        self.view_data = data or {}
        self.view_start_time = time.time()
        self.last_interaction_time = time.time()
        
        if duration is None:
            self.view_duration = self.default_timeout
        else:
            self.view_duration = duration
        
        # Reset animation frame
        self.animation_frame = 0
        
        # Debug
        # print(f"Vista cambiada a: {view_type.value}")
    
    def update(self):
        """
        Actualizar el estado del gestor de vistas
        Maneja timeouts y vuelve a vista principal si es necesario
        """
        current_time = time.time()
        
        # Actualizar frame de animación cada 100ms
        if current_time - self.last_animation_update > 0.1:
            self.animation_frame += 1
            self.last_animation_update = current_time
        
        # Si estamos en vista temporal y ha pasado el timeout
        if self.current_view != ViewType.SEQUENCER and self.view_duration > 0:
            elapsed = current_time - self.view_start_time
            if elapsed >= self.view_duration:
                self.return_to_sequencer()
        
        # Timer de inactividad (solo si estamos en SEQUENCER)
        if self.current_view == ViewType.SEQUENCER:
            inactive_time = current_time - self.last_interaction_time
            if inactive_time >= self.inactivity_timeout:
                # Ya estamos en sequencer, solo reseteamos el timer
                self.last_interaction_time = current_time
    
    def return_to_sequencer(self):
        """Volver a la vista principal (SEQUENCER)"""
        if self.current_view != ViewType.SEQUENCER:
            self.current_view = ViewType.SEQUENCER
            self.view_data = {}
            self.animation_frame = 0
    
    def register_interaction(self):
        """Registrar una interacción del usuario (resetea timer de inactividad)"""
        self.last_interaction_time = time.time()
    
    def get_current_view(self):
        """Obtener la vista actual"""
        return self.current_view
    
    def get_view_data(self):
        """Obtener los datos de la vista actual"""
        return self.view_data
    
    def get_animation_frame(self):
        """Obtener el frame de animación actual"""
        return self.animation_frame
    
    def is_sequencer_view(self):
        """Verificar si estamos en vista SEQUENCER"""
        return self.current_view == ViewType.SEQUENCER
    
    def render(self, led_matrix, sequencer, selected_step):
        """
        Renderizar la vista actual en la matriz LED
        
        Args:
            led_matrix: Instancia de LEDMatrix
            sequencer: Instancia de Sequencer
            selected_step: Paso actualmente seleccionado (POT_SCROLL)
        """
        if self.current_view == ViewType.SEQUENCER:
            # Vista principal: secuenciador completo
            pattern = sequencer.get_pattern()
            current_step = sequencer.current_step if sequencer.is_playing else -1
            led_matrix.draw_sequencer_grid(pattern, current_step, selected_step)
        
        elif self.current_view == ViewType.BPM:
            # Vista de tempo
            bpm = self.view_data.get('bpm', 120)
            beat_pulse = self.view_data.get('beat_pulse', False)
            led_matrix.draw_bpm_view(bpm, beat_pulse, self.animation_frame)
        
        elif self.current_view == ViewType.VOLUME:
            # Vista de volúmenes
            volumes = self.view_data.get('volumes', {})
            led_matrix.draw_volume_view(volumes)
        
        elif self.current_view == ViewType.SWING:
            # Vista de swing
            swing = self.view_data.get('swing', 0)
            led_matrix.draw_swing_view(swing, self.animation_frame)
        
        elif self.current_view == ViewType.PATTERN:
            # Vista de patrón
            pattern_num = self.view_data.get('pattern_num', 1)
            led_matrix.draw_pattern_view(pattern_num)
        
        elif self.current_view == ViewType.SAVE:
            # Vista de guardado (animación)
            led_matrix.draw_save_animation(self.animation_frame)
        
        elif self.current_view == ViewType.PAD:
            # Vista de pad
            instrument_id = self.view_data.get('instrument_id', 0)
            instrument_name = self.view_data.get('instrument_name', 'DRUM')
            led_matrix.draw_pad_view(instrument_id, instrument_name, self.animation_frame)

