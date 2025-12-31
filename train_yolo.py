"""
Nom du fichier: train_yolo.py
Auteur: Étienne-Théodore PRIN
Date: 2024-02-02

Description:
Ce module effectue l'entrainement d'un yolo v8 pour labeliser des images

Dépendances:
    -ultralytics
"""

from ultralytics import YOLO


if __name__ == '__main__':
    # Load a model
    model = YOLO('yolov8s.pt')  # load a pretrained model
    # Train the model
    results = model.train(data='/home/oussama.messai/Desktop/Hackathon/Bot-Clash-Royal/dataset/data.yaml', patience=100, epochs=500, imgsz=800, flipud=0.5, fliplr=0.5)