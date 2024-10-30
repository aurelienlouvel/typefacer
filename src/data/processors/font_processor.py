from fontTools import ttLib
from pathlib import Path
from typing import Dict, Any

class FontProcessor:
    """Processeur pour les fichiers TTF"""

    def __init__(self):
        self.supported_formats = ['.ttf']

    def process_font(self, font_path: Path) -> Dict[str, Any]:
        """Traite un fichier de police TTF."""
        if font_path.suffix not in self.supported_formats:
            raise ValueError(f"Format non supporté: {font_path.suffix}")

        try:
            font = ttLib.TTFont(font_path)
        except Exception as e:
            raise Exception(f"Erreur lors du chargement de {font_path}: {str(e)}")

        return {
            'metadata': self._extract_metadata(font),
            'glyph_set': font.getGlyphSet()
        }

    def _extract_metadata(self, font: ttLib.TTFont) -> Dict[str, Any]:
        """Extrait les métadonnées de la police"""
        return {
            'name': font['name'].getDebugName(1),
            'version': font['head'].fontRevision,
            'units_per_em': font['head'].unitsPerEm,
            'ascent': font['hhea'].ascent,
            'descent': font['hhea'].descent,
            'x_height': font['OS/2'].sxHeight if 'OS/2' in font else None,
            'cap_height': font['OS/2'].sCapHeight if 'OS/2' in font else None
        }

if __name__ == "__main__":
    # Test avec un fichier TTF
    processor = FontProcessor()

    # Liste tous les fichiers TTF dans le dossier train
    font_dir = Path("data/fonts/train")
    ttf_files = list(font_dir.glob("*.ttf"))

    print(f"Fichiers TTF trouvés : {len(ttf_files)}")

    if ttf_files:
        # Test avec le premier fichier
        test_font = ttf_files[0]
        print(f"\nTest avec : {test_font.name}")

        result = processor.process_font(test_font)
        print("\nMétadonnées extraites :")
        for key, value in result['metadata'].items():
            print(f"{key}: {value}")
        print(f"\nNombre de glyphes : {len(result['glyph_set'])}")
