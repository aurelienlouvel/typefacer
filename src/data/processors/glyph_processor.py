# src/data/processors/glyph_processor.py

from fontTools.pens.basePen import BasePen
from typing import Dict, List, Any

class GlyphProcessor:
    """Processeur pour extraire et normaliser les données des glyphes"""

    def process_glyph(self, glyph) -> Dict[str, Any]:
        """
        Traite un glyphe individuel.

        Args:
            glyph: Le glyphe à traiter

        Returns:
            Dict contenant les données du glyphe
        """
        return {
            'contours': self._extract_contours(glyph),
            'metrics': self._extract_metrics(glyph),
            'control_points': self._extract_control_points(glyph),
            'bounds': self._extract_bounds(glyph)
        }

    def _extract_metrics(self, glyph) -> Dict[str, float]:
        """Extrait les métriques du glyphe"""
        return {
            'width': glyph.width,
            'height': getattr(glyph, 'height', None),
            'advance_width': getattr(glyph, 'advance', glyph.width)
        }

    def _extract_bounds(self, glyph) -> Dict[str, float]:
        """Extrait les limites du glyphe"""
        try:
            bounds = glyph.getBounds()
            return {
                'xMin': bounds[0],
                'yMin': bounds[1],
                'xMax': bounds[2],
                'yMax': bounds[3]
            }
        except:
            return {'xMin': 0, 'yMin': 0, 'xMax': 0, 'yMax': 0}

    def _extract_contours(self, glyph) -> List[Dict]:
        """Extrait les contours du glyphe"""
        pen = GlyphPointPen()
        glyph.draw(pen)
        return pen.get_contours()

    def _extract_control_points(self, glyph) -> List[Dict]:
        """Extrait les points de contrôle"""
        pen = GlyphPointPen()
        glyph.draw(pen)
        return pen.get_points()

class GlyphPointPen(BasePen):
    """Pen personnalisé pour extraire les points des glyphes"""

    def __init__(self):
        super().__init__(None)
        self.contours = []
        self.current_contour = []
        self.points = []

    def _moveTo(self, pt):
        """Point de départ d'un nouveau contour"""
        if self.current_contour:
            self.contours.append(self.current_contour)
            self.current_contour = []
        self._add_point(pt, 'move')

    def _lineTo(self, pt):
        """Ligne droite vers un point"""
        self._add_point(pt, 'line')

    def _curveToOne(self, pt1, pt2, pt3):
        """Courbe de Bézier cubique"""
        self._add_point(pt1, 'control1')
        self._add_point(pt2, 'control2')
        self._add_point(pt3, 'curve')

    def _add_point(self, pt, type_):
        """Ajoute un point avec son type"""
        point = {
            'x': pt[0],
            'y': pt[1],
            'type': type_
        }
        self.current_contour.append(point)
        self.points.append(point)

    def get_contours(self):
        """Retourne tous les contours"""
        if self.current_contour:
            self.contours.append(self.current_contour)
        return self.contours

    def get_points(self):
        """Retourne tous les points"""
        return self.points

if __name__ == "__main__":
    # Test du processor
    from font_processor import FontProcessor
    from pathlib import Path

    # Charger une police
    font_processor = FontProcessor()
    glyph_processor = GlyphProcessor()

    # Trouver le premier fichier TTF
    font_dir = Path("data/fonts/train")
    ttf_files = list(font_dir.glob("*.ttf"))

    if ttf_files:
        # Charger la police
        font_data = font_processor.process_font(ttf_files[0])

        # Traiter le glyphe 'A' comme exemple
        glyph_set = font_data['glyph_set']
        if 'A' in glyph_set:
            glyph = glyph_set['A']
            result = glyph_processor.process_glyph(glyph)

            print("\nAnalyse du glyphe 'A':")
            print("\nMétriques:")
            for key, value in result['metrics'].items():
                print(f"  {key}: {value}")

            print("\nLimites:")
            for key, value in result['bounds'].items():
                print(f"  {key}: {value}")

            print(f"\nNombre de contours: {len(result['contours'])}")
            print(f"Nombre total de points: {len(result['control_points'])}")

            # Afficher plus de détails sur les points
            print("\nDétails des points:")
            for i, point in enumerate(result['control_points']):
                print(f"Point {i+1}: type={point['type']}, x={point['x']}, y={point['y']}")
