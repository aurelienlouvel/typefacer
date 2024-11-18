# src/data/processors/tensor_processor.py
import torch
from typing import Dict, List
from pathlib import Path
from fontTools.ttLib import TTFont

class TensorProcessor:
    """Processeur pour convertir les données de police en tenseurs"""

    def __init__(self):
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    def process_font_to_tensor(self, font_data: Dict) -> Dict[str, torch.Tensor]:
        """
        Convertit une police complète en tenseurs.

        Args:
            font_data: Données de la police depuis FontProcessor

        Returns:
            Dict contenant les tenseurs pour l'entraînement
        """
        return {
            'glyphs': self._convert_glyphs_to_tensor(font_data['font']),
            'style_embedding': self._create_style_embedding(font_data.get('description', {})),
            'variations': self._convert_variations_to_tensor(font_data.get('variation_axes', []))
        }

    def _convert_glyphs_to_tensor(self, font: TTFont) -> torch.Tensor:
        """Convertit tous les glyphes en un seul tenseur avec padding"""
        glyph_tensors = []
        max_points = 0

        # Stocker la référence à la table glyf
        self.glyf_table = font['glyf']
        print(f"\nNombre total de glyphes: {len(self.glyf_table.glyphs)}")

        for glyph_name in self.glyf_table.glyphs:
            try:
                glyph = self.glyf_table[glyph_name]
                if glyph.numberOfContours > 0:
                    points = self._normalize_points(glyph)
                    max_points = max(max_points, len(points))
            except Exception:
                continue

        print(f"Taille maximum de points trouvée: {max_points}")

        # Deuxième passage pour créer des tenseurs uniformes
        for glyph_name in self.glyf_table.glyphs:
            try:
                glyph = self.glyf_table[glyph_name]
                if glyph.numberOfContours > 0:
                    points = self._normalize_points(glyph)
                    if points:
                        # Padding avec des zéros
                        padded_points = points + [0.0] * (max_points - len(points))
                        glyph_tensors.append(torch.tensor(padded_points, dtype=torch.float32))
            except Exception as e:
                print(f"Erreur avec le glyphe {glyph_name}: {str(e)}")
                continue

        print(f"Nombre de glyphes traités avec succès: {len(glyph_tensors)}")

        if glyph_tensors:
            return torch.stack(glyph_tensors).to(self.device)
        return torch.tensor([]).to(self.device)

    def _normalize_points(self, glyph) -> List[float]:
        """Normalise les points du glyphe entre -1 et 1"""
        try:
            points = []
            if hasattr(glyph, 'numberOfContours') and glyph.numberOfContours > 0:
                # Obtenir les coordonnées
                coordinates = glyph.getCoordinates(self.glyf_table)
                # coordinates est un tuple (points, endPts)
                coords = coordinates[0]  # Prendre juste les points

                # Traiter chaque coordonnée
                for coord in coords:
                    x, y = coord  # Maintenant on peut unpack correctement
                    points.extend([float(x)/1000.0, float(y)/1000.0])

                return points
            return []

        except Exception as e:
            print(f"Erreur de normalisation détaillée: {str(e)}")
            return []



    def _create_style_embedding(self, description: Dict) -> torch.Tensor:
        """
        Crée un embedding à partir de la description.
        Pour l'instant un simple vecteur aléatoire, à améliorer plus tard.
        """
        return torch.randn(256).to(self.device)

    def _convert_variations_to_tensor(self, axes: List) -> torch.Tensor:
        """Convertit les axes de variation en tenseur"""
        variations = []
        for axis in axes:
            variations.extend([
                axis['min_value']/1000,
                axis['default_value']/1000,
                axis['max_value']/1000
            ])
        if not variations:
            variations = [0.0]
        return torch.tensor(variations, dtype=torch.float32).to(self.device)

if __name__ == "__main__":
    # Test du processor
    font_path = Path("data/fonts/train/RethinkSans-VariableFont_wght.ttf")

    if font_path.exists():
        font = TTFont(font_path)

        tensor_processor = TensorProcessor()
        tensor_data = tensor_processor.process_font_to_tensor({'font': font})

        
        # Print first glyph tensor
        if tensor_data['glyphs'].shape[0] > 0:
            first_glyph = tensor_data['glyphs'][4].cpu().numpy()
            print("\nPremier glyphe (276 points) :")
            print(first_glyph)