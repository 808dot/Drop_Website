import os

def create_folders(base_path, names):
    folder_path = os.path.join(base_path, "skrypt")
    os.makedirs(folder_path, exist_ok=True)
    
    for index, name in enumerate(names, start=2):
        folder_name = f"#{index} {name}"
        folder_full_path = os.path.join(folder_path, folder_name)
        os.makedirs(folder_full_path, exist_ok=True)
        print(f"Utworzono folder: {folder_full_path}")

if __name__ == "__main__":
    names_list = [
        "One Peace Pants", "One Peace Pants", "One Peace Pants", "Dusty Rose", "Safari Mesh Pants", 
        "Rusty Mesh Pants", "Angel Guardian Pants", "Rusty Garden Pants", "Dusty Plate Pants", 
        "Dusty Plate Pants", "Industrial Mesh Pants", "Anarchy Pants"
    ]  # Lista nazw folderów
    base_directory = os.getcwd()  # Możesz zmienić na inną ścieżkę
    create_folders(base_directory, names_list)