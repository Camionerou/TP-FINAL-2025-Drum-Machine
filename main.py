#!/usr/bin/env python3
"""
Raspberry Pi Drum Machine v2.5
Punto de entrada principal
"""

from core.drum_machine import DrumMachine

def main():
    """Función principal"""
    try:
        drum_machine = DrumMachine()
        drum_machine.run()
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
