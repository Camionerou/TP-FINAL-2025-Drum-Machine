#!/bin/bash
# Script de instalación del servicio de autoarranque
# Ejecutar con: sudo ./install_service.sh

echo "==================================================="
echo "  Instalador de Autoarranque - Drum Machine v2.0"
echo "==================================================="

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ ERROR: Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# Directorio del proyecto
PROJECT_DIR="/home/pi/DRUMMACHINE"

# Verificar que existe el proyecto
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo "❌ ERROR: No se encuentra main.py en $PROJECT_DIR"
    exit 1
fi

# Copiar archivo de servicio
echo "📋 Copiando archivo de servicio..."
cp drummachine.service /etc/systemd/system/

# Recargar systemd
echo "🔄 Recargando systemd..."
systemctl daemon-reload

# Habilitar servicio
echo "✅ Habilitando servicio..."
systemctl enable drummachine.service

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "📌 Comandos útiles:"
echo "   Iniciar:     sudo systemctl start drummachine"
echo "   Detener:     sudo systemctl stop drummachine"
echo "   Estado:      sudo systemctl status drummachine"
echo "   Ver logs:    sudo journalctl -u drummachine -f"
echo "   Deshabilitar:sudo systemctl disable drummachine"
echo ""
echo "🚀 El servicio se iniciará automáticamente en el próximo arranque."
echo "   Para probarlo ahora: sudo systemctl start drummachine"

