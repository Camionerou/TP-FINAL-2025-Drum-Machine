#!/bin/bash
# Script de instalación para Raspberry Pi Drum Machine

echo "================================================"
echo "  INSTALACIÓN RASPBERRY PI DRUM MACHINE"
echo "================================================"
echo ""

# Verificar que estamos en Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Advertencia: No parece ser una Raspberry Pi"
    read -p "¿Continuar de todas formas? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

echo "1. Actualizando sistema..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "2. Instalando dependencias del sistema..."
sudo apt install -y python3-pip python3-pygame portaudio19-dev git

echo ""
echo "3. Instalando dependencias Python..."
pip3 install -r requirements.txt

echo ""
echo "4. Verificando SPI..."
if lsmod | grep -q spi_bcm2835; then
    echo "✓ SPI ya está habilitado"
else
    echo "⚠️  SPI no está habilitado"
    echo "Ejecuta: sudo raspi-config"
    echo "Luego: Interface Options → SPI → Enable"
    echo "Y reinicia el sistema"
fi

echo ""
echo "5. Creando directorios..."
mkdir -p samples
mkdir -p patterns

echo ""
echo "6. Configurando permisos..."
# Agregar usuario al grupo GPIO si existe
if getent group gpio > /dev/null 2>&1; then
    sudo usermod -a -G gpio $USER
    echo "✓ Usuario agregado al grupo GPIO"
fi

# Agregar usuario al grupo SPI si existe
if getent group spi > /dev/null 2>&1; then
    sudo usermod -a -G spi $USER
    echo "✓ Usuario agregado al grupo SPI"
fi

echo ""
echo "================================================"
echo "  INSTALACIÓN COMPLETADA"
echo "================================================"
echo ""
echo "Próximos pasos:"
echo "1. Agregar tus samples WAV al directorio 'samples/'"
echo "2. Conectar todo el hardware según README.md"
echo "3. Si cambiaste grupos, hacer logout/login o reiniciar"
echo "4. Ejecutar: python3 main.py"
echo ""
echo "¡Disfruta tu Drum Machine! 🥁"

