"""
Features - Características opcionales (MIDI, Tap Tempo, Bluetooth, etc.)
"""

from .tap_tempo import TapTempo
from .midi_handler import MIDIHandler
from .bluetooth_audio import BluetoothAudio
from .effects_manager import EffectsManager

__all__ = ['TapTempo', 'MIDIHandler', 'BluetoothAudio', 'EffectsManager']

