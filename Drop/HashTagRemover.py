import os

# Funkcja do przejścia przez wszystkie foldery i pliki i zmiany ich nazw
def rename_folders_and_files_in_directory(root_dir):
    # Przechodzimy przez wszystkie foldery i pliki w katalogu
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):  # topdown=False aby najpierw zmienić pliki, potem foldery
        # Zmiana nazw folderów
        for dirname in dirnames:
            old_path = os.path.join(dirpath, dirname)
            new_dirname = dirname.replace('#', '')  # Usuwamy znak '#'
            new_path = os.path.join(dirpath, new_dirname)

            # Zmieniamy nazwę folderu
            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    print(f"Zmieniono nazwę folderu: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Nie udało się zmienić nazwy folderu {old_path}: {e}")
        
        # Zmiana nazw plików
        for filename in filenames:
            old_path = os.path.join(dirpath, filename)
            new_filename = filename.replace('#', '')  # Usuwamy znak '#'
            new_path = os.path.join(dirpath, new_filename)

            # Zmieniamy nazwę pliku
            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    print(f"Zmieniono nazwę pliku: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Nie udało się zmienić nazwy pliku {old_path}: {e}")

# Przykład użycia
root_directory = '.'  # '.' oznacza bieżący katalog
rename_folders_and_files_in_directory(root_directory)