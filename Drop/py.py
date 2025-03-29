import os
from PIL import Image

# Lista folderów
folders = [
    "2 One Peace Pants", "3 One Peace Pants", "4 One Peace Pants", "5 Dusty Rose", 
    "6 Safari Mesh Pants", "7 Rusty Mesh Pants", "8 Angel Guardian Pants", 
    "9 Rusty Garden Pants", "10 Dusty Plate Pants", "11 Dusty Plate Pants", 
    "12 Industrial Mesh Pants", "13 Anarchy Pants", "14 Rusty Oil Pants",
    "15 Rusty Oil Pants", "16 One Peace Pants", "17 Rusty Oil Pants",
    "18 Rusty Oil Pants"
]

# Ścieżka bazowa
base_path = os.path.dirname(os.path.abspath(__file__))

# Obsługiwane formaty obrazów
target_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

# Sprawdzenie istniejących folderów
existing_folders = [f for f in folders if os.path.isdir(os.path.join(base_path, f))]
missing_folders = [f for f in folders if not os.path.isdir(os.path.join(base_path, f))]

if missing_folders:
    print("Brakujące foldery:", missing_folders)

for folder in existing_folders:
    folder_path = os.path.join(base_path, folder)
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        file_name, file_ext = os.path.splitext(file)
        
        if file_ext.lower() in target_extensions:
            try:
                img = Image.open(file_path)
                webp_path = os.path.join(folder_path, f"{file_name}.webp")
                img.save(webp_path, "WEBP")
                print(f"Zapisano: {webp_path}")
            except Exception as e:
                print(f"Błąd podczas konwersji {file_path}: {e}")