"""
Manejador avanzado de eventos de botones
Soporta: click simple, doble-click, botón mantenido y combinaciones
"""

import time


class ButtonEvent:
    """Tipos de eventos de botón"""
    PRESS = "press"
    DOUBLE_CLICK = "double_click"
    HOLD = "hold"
    RELEASE = "release"


class ButtonHandler:
    """Manejador de eventos avanzados de botones"""
    
    def __init__(self, double_click_time=0.3, hold_time=0.8):
        """
        Inicializar manejador de botones
        
        Args:
            double_click_time: Tiempo máximo entre clicks para doble-click (segundos)
            hold_time: Tiempo mínimo para considerar botón mantenido (segundos)
        """
        self.double_click_time = double_click_time
        self.hold_time = hold_time
        
        # Estado de cada botón
        self.button_states = {}  # button_id: {'pressed': bool, 'press_time': float, 'last_click_time': float}
        self.held_buttons = set()  # Botones actualmente mantenidos
        self.click_counts = {}  # button_id: count
        
        # Callbacks
        self.on_press = None
        self.on_double_click = None
        self.on_hold = None
        self.on_release = None
        self.on_combination = None
        
        print("ButtonHandler inicializado")
    
    def register_callbacks(self, on_press=None, on_double_click=None, on_hold=None, 
                          on_release=None, on_combination=None):
        """
        Registrar callbacks para eventos
        
        Args:
            on_press: callback(button_id)
            on_double_click: callback(button_id)
            on_hold: callback(button_id, duration)
            on_release: callback(button_id, duration)
            on_combination: callback(button_ids_set)
        """
        self.on_press = on_press
        self.on_double_click = on_double_click
        self.on_hold = on_hold
        self.on_release = on_release
        self.on_combination = on_combination
    
    def update(self, pressed_buttons):
        """
        Actualizar estado de botones y detectar eventos
        
        Args:
            pressed_buttons: Lista de IDs de botones actualmente presionados
        """
        current_time = time.time()
        pressed_set = set(pressed_buttons)
        
        # Detectar combinaciones (2 o más botones simultáneos)
        if len(pressed_set) >= 2 and self.on_combination:
            # Solo trigger si todos están recién presionados (no mantenidos previamente)
            if not any(btn in self.held_buttons for btn in pressed_set):
                self.on_combination(pressed_set)
                # Marcar como procesados
                self.held_buttons.update(pressed_set)
        
        # Procesar cada botón
        all_buttons = set(self.button_states.keys()) | pressed_set
        
        for button_id in all_buttons:
            is_pressed = button_id in pressed_set
            
            # Inicializar estado si es nuevo
            if button_id not in self.button_states:
                self.button_states[button_id] = {
                    'pressed': False,
                    'press_time': 0,
                    'last_click_time': 0,
                    'hold_triggered': False
                }
            
            state = self.button_states[button_id]
            
            # Botón recién presionado
            if is_pressed and not state['pressed']:
                state['pressed'] = True
                state['press_time'] = current_time
                state['hold_triggered'] = False
                
                # Verificar doble-click
                time_since_last_click = current_time - state['last_click_time']
                
                if time_since_last_click < self.double_click_time:
                    # Doble-click detectado
                    if self.on_double_click:
                        self.on_double_click(button_id)
                    state['last_click_time'] = 0  # Reset
                else:
                    # Click simple (puede convertirse en doble)
                    state['last_click_time'] = current_time
                    if self.on_press and len(pressed_set) == 1:  # Solo si no es combinación
                        self.on_press(button_id)
            
            # Botón mantenido
            elif is_pressed and state['pressed']:
                hold_duration = current_time - state['press_time']
                
                # Trigger evento hold una sola vez
                if hold_duration >= self.hold_time and not state['hold_triggered']:
                    state['hold_triggered'] = True
                    self.held_buttons.add(button_id)
                    if self.on_hold:
                        self.on_hold(button_id, hold_duration)
            
            # Botón liberado
            elif not is_pressed and state['pressed']:
                duration = current_time - state['press_time']
                state['pressed'] = False
                
                if button_id in self.held_buttons:
                    self.held_buttons.remove(button_id)
                
                if self.on_release:
                    self.on_release(button_id, duration)
    
    def is_held(self, button_id):
        """Verificar si un botón está siendo mantenido"""
        return button_id in self.held_buttons
    
    def get_held_buttons(self):
        """Obtener conjunto de botones actualmente mantenidos"""
        return self.held_buttons.copy()
    
    def reset(self):
        """Resetear estado del manejador"""
        self.button_states.clear()
        self.held_buttons.clear()
        self.click_counts.clear()

