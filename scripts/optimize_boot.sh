#!/bin/bash
# Script de optimización de boot para Raspberry Pi
# Ejecutar con: sudo ./optimize_boot.sh

echo "=================================================="
echo "  Optimizador de Boot - Drum Machine v2.0"
echo "=================================================="

# Verificar root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ ERROR: Ejecutar como root (sudo)"
    exit 1
fi

echo ""
echo "🚀 Optimizando servicios..."

# NOTA: Bluetooth se mantiene habilitado para salida de audio inalámbrica
# Solo deshabilitar servicios realmente innecesarios
systemctl disable avahi-daemon.service 2>/dev/null
systemctl disable triggerhappy.service 2>/dev/null

# Asegurar que Bluetooth esté habilitado
systemctl enable bluetooth.service 2>/dev/null

echo "✅ Servicios optimizados (Bluetooth habilitado)"

echo ""
echo "⚡ Optimizando configuración de boot..."

# Reducir timeout de boot
if ! grep -q "boot_delay=0" /boot/config.txt; then
    echo "boot_delay=0" >> /boot/config.txt
fi

# Deshabilitar splash screen de Raspberry Pi (más rápido)
if ! grep -q "disable_splash=1" /boot/config.txt; then
    echo "disable_splash=1" >> /boot/config.txt
fi

echo "✅ Config.txt optimizado"

echo ""
echo "💾 Optimizando configuración de audio..."

# Asegurar que audio está habilitado y optimizado
if ! grep -q "dtparam=audio=on" /boot/config.txt; then
    echo "dtparam=audio=on" >> /boot/config.txt
fi

echo "✅ Audio optimizado"

echo ""
echo "✅ ¡Optimización completada!"
echo ""
echo "📌 Mejoras aplicadas:"
echo "   ✓ Servicios innecesarios deshabilitados"
echo "   ✓ Timeout de boot reducido"
echo "   ✓ Splash screen deshabilitado"
echo "   ✓ Audio optimizado"
echo ""
echo "🔄 Reinicia la RPi para aplicar cambios: sudo reboot"

