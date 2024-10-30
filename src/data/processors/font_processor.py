# src/data/processors/font_processor.py
import yaml
from fontTools import ttLib
from pathlib import Path
from typing import Dict, Any, List

class FontProcessor:

    def __init__(self):
        self.supported_formats = ['.ttf']
        try:
            with open('configs/data/font_descriptions.yaml') as f:
                self.font_descriptions = yaml.safe_load(f)['fonts']
        except (FileNotFoundError, KeyError):
            self.font_descriptions = {}



    def process_font(self, font_path: Path) -> Dict[str, Any]:
        if font_path.suffix not in self.supported_formats:
            raise ValueError(f"Format non supporté: {font_path.suffix}")

        try:
            font = ttLib.TTFont(font_path)
        except Exception as e:
            raise Exception(f"Erreur lors du chargement de {font_path}: {str(e)}")

        return {
            'font': font,
            'metadata': self._extract_metadata(font),
            'description': self._get_font_description(font_path.name),
            'variation_axes': self._extract_variation_axes(font),
            'instances': self._extract_instances(font),
            'glyph_set': font.getGlyphSet()
        }

    def _extract_metadata(self, font: ttLib.TTFont) -> Dict[str, Any]:
        return {
            'name': font['name'].getDebugName(1),
            'version': font['head'].fontRevision,
            'units_per_em': font['head'].unitsPerEm,
            'ascent': font['hhea'].ascent,
            'descent': font['hhea'].descent,
            'x_height': font['OS/2'].sxHeight if 'OS/2' in font else None,
            'cap_height': font['OS/2'].sCapHeight if 'OS/2' in font else None,
            'is_variable': 'fvar' in font
        }

    def _get_font_description(self, font_name: str) -> Dict:
            return self.font_descriptions.get(font_name, {
                'description': '',
                'tags': [],
                'characteristics': {}
            })

    def _extract_variation_axes(self, font: ttLib.TTFont) -> List[Dict[str, Any]]:
        if 'fvar' not in font:
            return []

        axes = []
        for axis in font['fvar'].axes:
            axes.append({
                'tag': axis.axisTag,
                'name': axis.axisNameID,
                'min_value': axis.minValue,
                'default_value': axis.defaultValue,
                'max_value': axis.maxValue
            })
        return axes

    def _extract_instances(self, font: ttLib.TTFont) -> List[Dict[str, Any]]:
        if 'fvar' not in font:
            return []

        instances = []
        for instance in font['fvar'].instances:
            # Récupérer le vrai nom de l'instance
            instance_name = font['name'].getDebugName(instance.subfamilyNameID)

            coordinates = {}
            for i, axis in enumerate(font['fvar'].axes):
                coordinates[axis.axisTag] = instance.coordinates.get(axis.axisTag, 0)

            instances.append({
                'name': instance_name,  # Nom réel au lieu de l'ID
                'coordinates': coordinates
            })
        return instances



if __name__ == "__main__":
    # Test avec un fichier TTF
    processor = FontProcessor()

    font_dir = Path("data/fonts/train")
    ttf_files = list(font_dir.glob("*.ttf"))

    print(f"Fichiers TTF trouvés : {len(ttf_files)}")

    if ttf_files:
        test_font = ttf_files[0]
        print(f"\nTest avec : {test_font.name}")

        result = processor.process_font(test_font)
        print("\nMétadonnées extraites :")
        for key, value in result['metadata'].items():
            print(f"{key}: {value}")

        print("\nDescription de la font :")
        desc = result['description']
        print(f"Description: {desc['description']}")
        print("Tags:", ", ".join(desc['tags']))
        print("Caractéristiques:")
        for key, value in desc['characteristics'].items():
            print(f"  {key}: {value}")

        print("\nAxes de variation :")
        for axis in result['variation_axes']:
            print(f"\nAxe: {axis['tag']}")
            print(f"  Min: {axis['min_value']}")
            print(f"  Default: {axis['default_value']}")
            print(f"  Max: {axis['max_value']}")

        print("\nInstances prédéfinies :")
        for instance in result['instances']:
            print(f"\nInstance: {instance['name']}")
            print("  Coordonnées :")
            for axis, value in instance['coordinates'].items():
                print(f"    {axis}: {value}")

        print(f"\nNombre de glyphes : {len(result['glyph_set'])}")
