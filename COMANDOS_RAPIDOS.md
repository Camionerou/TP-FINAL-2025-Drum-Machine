# 🚀 Comandos Rápidos - Drum Machine RPi

## 📤 Subir a GitHub (desde tu Mac)

```bash
cd /Users/enzosaldivia/DRUMMACHINE

# Primera vez: configurar remoto
git remote add origin https://github.com/TU_USUARIO/TP-FINAL-2025-Drum-Machine.git
git branch -M main
git push -u origin main

# Actualizaciones posteriores:
git add .
git commit -m "Descripción de cambios"
git push
```

---

## 💻 Instalar en Raspberry Pi

```bash
# 1. Conectar
ssh pi@IP_DE_TU_RPI

# 2. Clonar
git clone https://github.com/TU_USUARIO/TP-FINAL-2025-Drum-Machine.git
cd TP-FINAL-2025-Drum-Machine

# 3. Instalar
./install.sh

# 4. Habilitar SPI
sudo raspi-config
# → Interface Options → SPI → Enable → Reboot

# 5. Agregar samples WAV a la carpeta samples/
# kick.wav, snare.wav, chh.wav, ohh.wav, tom1.wav, tom2.wav, crash.wav, ride.wav

# 6. Probar hardware
python3 test_hardware.py

# 7. Ejecutar
python3 main.py
```

---

## 🎮 Ejecutar la Drum Machine

```bash
cd ~/TP-FINAL-2025-Drum-Machine
python3 main.py
```

**Salir:** `Ctrl+C`

---

## 🔧 Comandos Útiles RPi

```bash
# Ver dispositivos SPI
ls /dev/spi*

# Probar audio
speaker-test -t wav -c 2

# Ver uso de GPIO
gpio readall

# Ver temperatura RPi
vcgencmd measure_temp

# Reiniciar
sudo reboot

# Apagar
sudo shutdown -h now
```

---

## 📋 Copiar samples desde Mac a RPi

```bash
# Desde tu Mac
cd /ruta/donde/estan/tus/samples
scp *.wav pi@IP_RPI:~/TP-FINAL-2025-Drum-Machine/samples/
```

---

## 🐛 Solución Rápida de Problemas

```bash
# Reinstalar dependencias
pip3 install -r requirements.txt

# Verificar que SPI esté habilitado
lsmod | grep spi

# Ver logs de errores
python3 main.py 2>&1 | tee error.log
```

