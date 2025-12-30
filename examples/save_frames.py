import time
import os
import argparse
import numpy as np
from PIL import Image
import RPi.GPIO as GPIO
from pmw3901 import BG_CS_BACK_BCM, BG_CS_FRONT_BCM, PAA5100, PMW3901

print("""salvar_imagem.py - Salva frames como PNG (Versão Engenharia V3)""")

parser = argparse.ArgumentParser()
parser.add_argument("--board", type=str, choices=["pmw3901", "paa5100"], required=True, help="Modelo do sensor")
parser.add_argument("--rotation", type=int, default=0, choices=[0, 90, 180, 270], help="Rotação da imagem")
parser.add_argument("--spi-slot", type=str, default="front", choices=["front", "back"], help="Slot SPI (cs)")
parser.add_argument("--output-dir", type=str, default="capturas", help="Pasta de saída")
parser.add_argument("--spi-speed", type=int, default=1000000, help="Velocidade SPI em Hz (padrão seguro: 1MHz)")

args = parser.parse_args()

SensorClass = PMW3901 if args.board == "pmw3901" else PAA5100
spi_cs_pin = BG_CS_FRONT_BCM if args.spi_slot == "front" else BG_CS_BACK_BCM

try:
    flo = SensorClass(spi_port=0, spi_cs=spi_cs_pin)
    
    if hasattr(flo, '_spi'):
        flo._spi.max_speed_hz = args.spi_speed
        print(f"Velocidade SPI ajustada internamente para: {args.spi_speed} Hz")
    elif hasattr(flo, 'spi'):
        flo.spi.max_speed_hz = args.spi_speed
        print(f"Velocidade SPI ajustada internamente para: {args.spi_speed} Hz")
    else:
        print("AVISO: Não foi possível ajustar a velocidade do SPI via código.")
        print("Se der timeout, você precisará editar o arquivo da biblioteca manualmente.")

    flo.set_rotation(args.rotation)
    print("Sensor Inicializado com Sucesso!")

except Exception as e:
    print(f"Erro fatal na inicialização: {e}")
    exit(1)

os.makedirs(args.output_dir, exist_ok=True)
print(f"Salvando em ./{args.output_dir}/ ... (CTRL+C para parar)")

count = 0
try:
    while True:
        try:
            raw_data = flo.frame_capture()
            
            matrix = np.array(raw_data, dtype=np.uint8).reshape((35, 35))
            img = Image.fromarray(matrix, 'L')
            img = img.resize((350, 350), Image.NEAREST)

            fname = os.path.join(args.output_dir, f"frame_{count:03d}.png")
            img.save(fname)
            print(f"Salvo: {fname}")
            
            count += 1
            time.sleep(0.2) 

        except RuntimeError as e:
            print(f"Aviso: Timeout na captura ({e}). O SPI pode estar instável. Tentando novamente...")
            time.sleep(0.1)
            continue

except KeyboardInterrupt:
    print("\nParando captura.")
    pass
