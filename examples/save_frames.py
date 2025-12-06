#!/usr/bin/env python
import argparse
import time
import os
import numpy as np
from PIL import Image
from pmw3901 import BG_CS_BACK_BCM, BG_CS_FRONT_BCM, PAA5100, PMW3901

print("""salvar_imagem.py - Salva frames como PNG""")

parser = argparse.ArgumentParser()
parser.add_argument("--board", type=str, choices=["pmw3901", "paa5100"], required=True)
parser.add_argument("--rotation", type=int, default=0, choices=[0, 90, 180, 270])
parser.add_argument("--spi-slot", type=str, default="front", choices=["front", "back"])
parser.add_argument("--output-dir", type=str, default="capturas")

args = parser.parse_args()
SensorClass = PMW3901 if args.board == "pmw3901" else PAA5100

try:
    flo = SensorClass(spi_port=0, spi_cs=BG_CS_FRONT_BCM if args.spi_slot == "front" else BG_CS_BACK_BCM)
    flo.set_rotation(args.rotation)
    print("Sensor OK!")
except Exception as e:
    print(f"Erro: {e}")
    exit(1)

os.makedirs(args.output_dir, exist_ok=True)
print(f"Salvando em ./{args.output_dir}/ ... (CTRL+C para parar)")

count = 0
try:
    while True:
        raw_data = flo.frame_capture()
        # Converte lista para array numpy e depois imagem
        matrix = np.array(raw_data, dtype=np.uint8).reshape((35, 35))
        img = Image.fromarray(matrix, 'L')
        # Aumenta 10x para visualização
        img = img.resize((350, 350), Image.NEAREST)

        fname = os.path.join(args.output_dir, f"frame_{count:03d}.png")
        img.save(fname)
        print(f"Salvo: {fname}")
        count += 1
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
