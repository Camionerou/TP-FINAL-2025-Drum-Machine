"""
Bluetooth Audio Handler para Drum Machine
Gestiona conexión y salida de audio via Bluetooth
"""

import subprocess
import time
import os


class BluetoothAudio:
    """
    Manejador de audio Bluetooth para salida inalámbrica
    Usa PulseAudio y bluetoothctl para gestión
    """
    
    def __init__(self):
        """Inicializar gestor de Bluetooth"""
        self.connected_device = None
        self.connected_mac = None
        self.available_devices = []
        self.enabled = self._check_bluetooth_available()
        
        if self.enabled:
            print("✓ Bluetooth disponible")
        else:
            print("⚠️ Bluetooth no disponible")
    
    def _check_bluetooth_available(self):
        """Verificar si Bluetooth está disponible y activo"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'bluetooth'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error verificando Bluetooth: {e}")
            return False
    
    def _run_bluetoothctl_command(self, commands, timeout=10):
        """
        Ejecutar comando en bluetoothctl
        
        Args:
            commands: Lista de comandos o string único
            timeout: Timeout en segundos
            
        Returns:
            Salida del comando
        """
        if isinstance(commands, str):
            commands = [commands]
        
        try:
            # Crear script temporal
            script = '\n'.join(commands) + '\nexit\n'
            
            result = subprocess.run(
                ['bluetoothctl'],
                input=script,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result.stdout
        
        except subprocess.TimeoutExpired:
            print("⏱️ Timeout en comando Bluetooth")
            return ""
        except Exception as e:
            print(f"Error ejecutando bluetoothctl: {e}")
            return ""
    
    def scan_devices(self, duration=10):
        """
        Escanear dispositivos Bluetooth disponibles
        
        Args:
            duration: Duración del escaneo en segundos
            
        Returns:
            Lista de diccionarios con 'name' y 'mac'
        """
        if not self.enabled:
            return []
        
        print(f"🔍 Escaneando dispositivos Bluetooth ({duration}s)...")
        
        # Iniciar escaneo
        self._run_bluetoothctl_command('scan on', timeout=2)
        
        # Esperar durante el escaneo
        time.sleep(duration)
        
        # Detener escaneo y obtener dispositivos
        output = self._run_bluetoothctl_command(['scan off', 'devices'])
        
        # Parsear salida
        devices = []
        for line in output.split('\n'):
            if line.startswith('Device '):
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    devices.append({'mac': mac, 'name': name})
        
        self.available_devices = devices
        print(f"✓ Encontrados {len(devices)} dispositivo(s)")
        
        return devices
    
    def pair_device(self, mac_address):
        """
        Emparejar con dispositivo Bluetooth
        
        Args:
            mac_address: Dirección MAC del dispositivo
            
        Returns:
            bool: True si se emparejó exitosamente
        """
        if not self.enabled:
            return False
        
        print(f"🔗 Emparejando con {mac_address}...")
        
        output = self._run_bluetoothctl_command([
            f'pair {mac_address}',
            f'trust {mac_address}'
        ])
        
        success = 'Pairing successful' in output or 'already paired' in output.lower()
        
        if success:
            print(f"✓ Emparejado con {mac_address}")
        else:
            print(f"✗ Error emparejando: {output[:100]}")
        
        return success
    
    def connect_device(self, mac_address, device_name=None):
        """
        Conectar a dispositivo Bluetooth
        
        Args:
            mac_address: Dirección MAC del dispositivo
            device_name: Nombre del dispositivo (opcional, para logs)
            
        Returns:
            bool: True si se conectó exitosamente
        """
        if not self.enabled:
            return False
        
        device_str = device_name if device_name else mac_address
        print(f"📡 Conectando a {device_str}...")
        
        # Asegurar que esté emparejado
        self.pair_device(mac_address)
        
        # Conectar
        output = self._run_bluetoothctl_command(f'connect {mac_address}')
        
        success = 'Connection successful' in output or 'already connected' in output.lower()
        
        if success:
            self.connected_device = device_name
            self.connected_mac = mac_address
            print(f"✓ Conectado a {device_str}")
            
            # Configurar como sink de audio
            time.sleep(2)  # Esperar a que se establezca la conexión
            self._set_bluetooth_as_audio_sink()
        else:
            print(f"✗ Error conectando: {output[:100]}")
        
        return success
    
    def _set_bluetooth_as_audio_sink(self):
        """Configurar dispositivo Bluetooth como salida de audio"""
        try:
            # Usar pactl para redirigir audio a Bluetooth
            result = subprocess.run(
                ['pactl', 'list', 'short', 'sinks'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Buscar sink de Bluetooth
            for line in result.stdout.split('\n'):
                if 'bluez' in line.lower():
                    sink_name = line.split()[1]
                    
                    # Establecer como default
                    subprocess.run(
                        ['pactl', 'set-default-sink', sink_name],
                        timeout=5
                    )
                    
                    print(f"✓ Audio redirigido a Bluetooth: {sink_name}")
                    return True
            
            print("⚠️ No se encontró sink de Bluetooth")
            return False
        
        except Exception as e:
            print(f"Error configurando audio sink: {e}")
            return False
    
    def disconnect(self):
        """Desconectar dispositivo Bluetooth actual"""
        if not self.enabled or not self.connected_mac:
            return False
        
        print(f"🔌 Desconectando {self.connected_device}...")
        
        output = self._run_bluetoothctl_command(f'disconnect {self.connected_mac}')
        
        success = 'Successful' in output or 'not connected' in output.lower()
        
        if success:
            print(f"✓ Desconectado")
            self.connected_device = None
            self.connected_mac = None
            
            # Volver a audio local
            self._restore_local_audio()
        
        return success
    
    def _restore_local_audio(self):
        """Restaurar audio a salida local (jack 3.5mm)"""
        try:
            result = subprocess.run(
                ['pactl', 'list', 'short', 'sinks'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Buscar sink local (no bluez)
            for line in result.stdout.split('\n'):
                if line and 'bluez' not in line.lower():
                    sink_name = line.split()[1]
                    
                    subprocess.run(
                        ['pactl', 'set-default-sink', sink_name],
                        timeout=5
                    )
                    
                    print(f"✓ Audio restaurado a: {sink_name}")
                    return True
            
            return False
        
        except Exception as e:
            print(f"Error restaurando audio: {e}")
            return False
    
    def is_connected(self):
        """Verificar si hay dispositivo conectado"""
        return self.connected_mac is not None
    
    def get_connected_device(self):
        """Obtener nombre del dispositivo conectado"""
        return self.connected_device
    
    def get_status(self):
        """
        Obtener estado completo del Bluetooth
        
        Returns:
            dict: Estado con dispositivo conectado, disponibles, etc.
        """
        return {
            'enabled': self.enabled,
            'connected': self.is_connected(),
            'device': self.connected_device,
            'mac': self.connected_mac,
            'available_count': len(self.available_devices)
        }
    
    def quick_connect_last(self):
        """
        Conectar rápidamente al último dispositivo emparejado
        Útil para reconexión automática al arrancar
        """
        if not self.enabled:
            return False
        
        # Obtener dispositivos emparejados
        output = self._run_bluetoothctl_command('paired-devices')
        
        # Tomar el primero de la lista
        for line in output.split('\n'):
            if line.startswith('Device '):
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    return self.connect_device(mac, name)
        
        print("⚠️ No hay dispositivos emparejados")
        return False


# Test del módulo
if __name__ == "__main__":
    print("=== Test de Bluetooth Audio ===\n")
    
    bt = BluetoothAudio()
    
    if not bt.enabled:
        print("❌ Bluetooth no disponible en este sistema")
        exit(1)
    
    print("\n1. Escanear dispositivos...")
    devices = bt.scan_devices(duration=10)
    
    if devices:
        print(f"\n📱 Dispositivos encontrados:")
        for i, dev in enumerate(devices):
            print(f"  {i+1}. {dev['name']} ({dev['mac']})")
        
        # Conectar al primero (solo para test)
        if len(devices) > 0:
            print(f"\n2. Conectando al primer dispositivo...")
            bt.connect_device(devices[0]['mac'], devices[0]['name'])
    else:
        print("\n❌ No se encontraron dispositivos")
    
    print(f"\n Estado final: {bt.get_status()}")

