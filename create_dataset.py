"""
Dataset Creator dla ForYou Drop Website
========================================
Przetwarza zdjęcia produktów i tworzy zoptymalizowany dataset w formacie WebP.
Automatycznie generuje plik items.json z listą produktów dla strony.

Użycie:
    python create_dataset.py                    # Przetwarza z domyślnej lokalizacji
    python create_dataset.py --scan             # Tylko skanuje istniejący dataset
    python create_dataset.py --input <ścieżka>  # Przetwarza z podanej lokalizacji
"""

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Moduł PIL (Pillow) nie jest zainstalowany.")
    print("   Zainstaluj: pip install Pillow")
    print("   Tryb skanowania nadal dostępny.\n")


# === KONFIGURACJA ===
SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_INPUT = Path(r"D:\Windows_Newest_BackUp\SharedFiles\ForYou\ForYou_Items\Items")
OUTPUT_DIR = SCRIPT_DIR / "Items_Dataset"
ITEMS_JSON = SCRIPT_DIR / "items.json"

MAX_SIZE = (1920, 1080)
WEBP_QUALITY = 85
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


@dataclass
class ProductItem:
    """Reprezentacja pojedynczego produktu."""
    id: int
    name: str
    folder: str
    images: list[str]


class DatasetCreator:
    """Główna klasa do tworzenia datasetu produktów."""
    
    def __init__(self, input_root: Path, output_root: Path):
        self.input_root = input_root
        self.output_root = output_root
        self.products: list[ProductItem] = []
        self.stats = {"processed": 0, "skipped": 0, "errors": 0}
    
    def _convert_to_rgb(self, img: "Image.Image") -> "Image.Image":
        """Konwertuje obraz do RGB."""
        if img.mode in ("RGBA", "P", "LA"):
            return img.convert("RGB")
        if img.mode != "RGB":
            return img.convert("RGB")
        return img
    
    def _resize_if_needed(self, img: "Image.Image") -> "Image.Image":
        """Zmniejsza obraz jeśli przekracza MAX_SIZE."""
        if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
            img.thumbnail(MAX_SIZE, Image.LANCZOS)
        return img
    
    def process_image(self, src: Path, dst: Path) -> bool:
        """
        Przetwarza pojedynczy obraz: konwersja do RGB, resize, zapis jako WebP.
        Zwraca True jeśli sukces.
        """
        if not PIL_AVAILABLE:
            return False
            
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            with Image.open(src) as img:
                img = self._convert_to_rgb(img)
                img = self._resize_if_needed(img)
                
                dst_webp = dst.with_suffix(".webp")
                img.save(dst_webp, format="WEBP", quality=WEBP_QUALITY, method=6)
            
            return True
        except Exception as e:
            print(f"  ❌ Błąd: {src.name} - {e}")
            return False
    
    @staticmethod
    def extract_product_id(folder_name: str) -> int:
        """Wyciąga numer produktu z nazwy folderu."""
        match = re.match(r"^(\d+)", folder_name)
        return int(match.group(1)) if match else 0
    
    @staticmethod
    def extract_product_name(folder_name: str) -> str:
        """Wyciąga nazwę produktu (bez numeru)."""
        match = re.match(r"^\d+\s+(.+)$", folder_name)
        return match.group(1).strip() if match else folder_name
    
    def process_product(self, product_dir: Path) -> Optional[ProductItem]:
        """
        Przetwarza folder produktu.
        Szuka obrazów w podfolderze InstagramPost.
        """
        instagram_dir = product_dir / "InstagramPost"
        if not instagram_dir.is_dir():
            self.stats["skipped"] += 1
            return None
        
        folder_name = product_dir.name
        product_id = self.extract_product_id(folder_name)
        product_name = self.extract_product_name(folder_name)
        output_dir = self.output_root / folder_name
        
        print(f"\n📁 [{product_id:02d}] {product_name}")
        
        processed_images = []
        
        for img_file in sorted(instagram_dir.iterdir()):
            if not img_file.is_file():
                continue
            if img_file.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            
            dst_file = output_dir / img_file.name
            
            if self.process_image(img_file, dst_file):
                webp_name = img_file.stem + ".webp"
                processed_images.append(webp_name)
                print(f"  ✅ {webp_name}")
                self.stats["processed"] += 1
            else:
                self.stats["errors"] += 1
        
        if not processed_images:
            self.stats["skipped"] += 1
            return None
        
        return ProductItem(
            id=product_id,
            name=product_name,
            folder=folder_name,
            images=processed_images
        )
    
    def run(self) -> list[ProductItem]:
        """Uruchamia przetwarzanie całego datasetu."""
        print("=" * 50)
        print("🚀 ForYou Dataset Creator")
        print("=" * 50)
        print(f"📥 Źródło:  {self.input_root}")
        print(f"📤 Wynik:   {self.output_root}")
        
        if not self.input_root.is_dir():
            print(f"\n❌ Katalog źródłowy nie istnieje: {self.input_root}")
            return []
        
        # Sortuj foldery według numeru produktu
        product_dirs = sorted(
            [d for d in self.input_root.iterdir() if d.is_dir()],
            key=lambda p: self.extract_product_id(p.name)
        )
        
        for product_dir in product_dirs:
            product = self.process_product(product_dir)
            if product:
                self.products.append(product)
        
        # Sortuj produkty według ID
        self.products.sort(key=lambda p: p.id)
        
        self._print_summary()
        return self.products
    
    def _print_summary(self):
        """Wyświetla podsumowanie."""
        print("\n" + "=" * 50)
        print("📊 PODSUMOWANIE")
        print("=" * 50)
        print(f"  ✅ Przetworzonych obrazów: {self.stats['processed']}")
        print(f"  ⏭️  Pominiętych folderów:  {self.stats['skipped']}")
        print(f"  ❌ Błędów:                 {self.stats['errors']}")
        print(f"  📦 Produktów w datasecie: {len(self.products)}")


class DatasetScanner:
    """Skanuje istniejący dataset w katalogu Items_Dataset."""
    
    def __init__(self, dataset_dir: Path):
        self.dataset_dir = dataset_dir
        self.products: list[ProductItem] = []
    
    def scan(self) -> list[ProductItem]:
        """Skanuje istniejące foldery w datasecie."""
        print("=" * 50)
        print("🔍 ForYou Dataset Scanner")
        print("=" * 50)
        print(f"📂 Skanowanie: {self.dataset_dir}")
        
        if not self.dataset_dir.is_dir():
            print(f"\n❌ Katalog nie istnieje: {self.dataset_dir}")
            return []
        
        # Znajdź wszystkie foldery produktów
        product_dirs = sorted(
            [d for d in self.dataset_dir.iterdir() if d.is_dir()],
            key=lambda p: DatasetCreator.extract_product_id(p.name)
        )
        
        for product_dir in product_dirs:
            folder_name = product_dir.name
            product_id = DatasetCreator.extract_product_id(folder_name)
            product_name = DatasetCreator.extract_product_name(folder_name)
            
            # Znajdź wszystkie obrazy WebP
            images = sorted([
                f.name for f in product_dir.iterdir()
                if f.is_file() and f.suffix.lower() == ".webp"
            ])
            
            if images:
                self.products.append(ProductItem(
                    id=product_id,
                    name=product_name,
                    folder=folder_name,
                    images=images
                ))
                print(f"  📁 [{product_id:02d}] {product_name} ({len(images)} zdjęć)")
        
        print(f"\n📦 Znaleziono {len(self.products)} produktów")
        return self.products


def save_items_json(products: list[ProductItem], output_path: Path):
    """Zapisuje listę produktów do pliku JSON."""
    data = {
        "products": [asdict(p) for p in products],
        "folders": [p.folder for p in products]
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Zapisano: {output_path}")


def generate_js_array(products: list[ProductItem]) -> str:
    """Generuje tablicę JS z folderami do wklejenia w index.html."""
    folders = [f'                    "{p.folder}"' for p in products]
    return "                let folders = [\n" + ",\n".join(folders) + "\n                ];"


def parse_args():
    """Parsuje argumenty linii poleceń."""
    parser = argparse.ArgumentParser(
        description="ForYou Dataset Creator - przetwarza zdjęcia produktów",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Ścieżka do katalogu źródłowego (domyślnie: {DEFAULT_INPUT})"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Ścieżka do katalogu wyjściowego (domyślnie: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--scan", "-s",
        action="store_true",
        help="Tylko skanuj istniejący dataset (bez przetwarzania)"
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Nie zapisuj pliku items.json"
    )
    return parser.parse_args()


def main():
    """Główna funkcja programu."""
    args = parse_args()
    
    if args.scan:
        # Tryb skanowania - tylko czytaj istniejący dataset
        scanner = DatasetScanner(args.output)
        products = scanner.scan()
    else:
        # Tryb tworzenia - przetwarzaj obrazy
        if not PIL_AVAILABLE:
            print("❌ Moduł Pillow jest wymagany do przetwarzania obrazów.")
            print("   Użyj --scan aby tylko zeskanować istniejący dataset.")
            return
        
        creator = DatasetCreator(args.input, args.output)
        products = creator.run()
    
    if products:
        # Zapisz JSON z metadanymi
        if not args.no_json:
            save_items_json(products, ITEMS_JSON)
        
        # Pokaż tablicę JS do skopiowania
        print("\n" + "=" * 50)
        print("📋 Tablica JS do index.html:")
        print("=" * 50)
        print(generate_js_array(products))
    
    print("\n✨ Gotowe!")


if __name__ == "__main__":
    main()
