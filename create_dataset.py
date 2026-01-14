import os
from pathlib import Path
from PIL import Image

# ŚCIEŻKI – w razie potrzeby możesz zmienić
INPUT_ROOT = Path(r"D:\Windows_Newest_BackUp\SharedFiles\ForYou\ForYou_Items\Items")
OUTPUT_ROOT = INPUT_ROOT.parent / "Items_Dataset"

MAX_SIZE = (1920, 1080)  # Full HD
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def process_image(src_path: Path, dst_path: Path) -> None:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src_path) as img:
        # konwersja do RGB (niektóre PNG mają alpha / paletę)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        elif img.mode == "RGBA":
            img = img.convert("RGB")

        # nie powiększaj małych obrazków
        if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
            img.thumbnail(MAX_SIZE, Image.LANCZOS)

        dst_path = dst_path.with_suffix(".webp")
        img.save(dst_path, format="WEBP", quality=85, method=6)


def process_product(product_dir: Path) -> None:
    instagram_dir = product_dir / "InstagramPost"
    if not instagram_dir.is_dir():
        return  # brak folderu InstagramPost – pomiń

    product_name = product_dir.name
    output_product_dir = OUTPUT_ROOT / product_name

    for entry in instagram_dir.iterdir():
        if not entry.is_file():
            continue
        if entry.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        # nazwa pliku docelowego taka sama, ale z rozszerzeniem .webp
        dst_file = output_product_dir / entry.name
        try:
            print(f"Przetwarzanie: {entry}")
            process_image(entry, dst_file)
        except Exception as e:
            print(f"d Bfd przy {entry}: {e}")


def main():
    print(f"Wejbcie: {INPUT_ROOT}")
    print(f"Wyjbcie: {OUTPUT_ROOT}")
    if not INPUT_ROOT.is_dir():
        print("d Katalog wejbciowy nie istnieje.")
        return

    for product_dir in INPUT_ROOT.iterdir():
        if product_dir.is_dir():
            process_product(product_dir)

    print("Gotowe.")


if __name__ == "__main__":
    main()
