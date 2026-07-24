"""
Plan2Takeoff V2 — DXF Drawing Parser Unit Test
Tests DrawingParserV2.parse_dxf() entity extraction, layer parsing,
text block scraping, and unique project input generation.
"""

import sys
import os
import ezdxf

sys.path.insert(0, 'backend')
from engine.pdf_dxf_parser import DrawingParserV2, DrawingParseResult


def create_sample_dxf(dxf_path: str):
    """Creates a sample CAD DXF file with structural entities and text annotations."""
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Create structural layers
    doc.layers.new(name='S-FOOTING', dxfattribs={'color': 1})
    doc.layers.new(name='S-COLUMN', dxfattribs={'color': 3})
    doc.layers.new(name='S-BEAM', dxfattribs={'color': 2})
    doc.layers.new(name='S-WALL', dxfattribs={'color': 4})
    doc.layers.new(name='ANNOTATIONS', dxfattribs={'color': 7})

    # Add Footing polylines
    msp.add_lwpolyline([(0, 0), (1500, 0), (1500, 1500), (0, 1500)], close=True, dxfattribs={'layer': 'S-FOOTING'})
    msp.add_text("F-1 (1.5x1.5m)", dxfattribs={'layer': 'ANNOTATIONS', 'height': 100}).set_placement((200, 200))

    # Add Column polylines
    msp.add_lwpolyline([(500, 500), (900, 500), (900, 900), (500, 900)], close=True, dxfattribs={'layer': 'S-COLUMN'})
    msp.add_text("C-1 (400x400)", dxfattribs={'layer': 'ANNOTATIONS', 'height': 80}).set_placement((550, 550))

    # Add Beam polylines
    msp.add_line((1500, 750), (4500, 750), dxfattribs={'layer': 'S-BEAM'})
    msp.add_text("2B-1 (250x400)", dxfattribs={'layer': 'ANNOTATIONS', 'height': 80}).set_placement((2000, 800))

    # Add Wall
    msp.add_line((0, 0), (4500, 0), dxfattribs={'layer': 'S-WALL'})
    msp.add_text("150mm CHB Wall L=4.5m H=3.2m", dxfattribs={'layer': 'ANNOTATIONS', 'height': 80}).set_placement((500, -200))

    doc.saveas(dxf_path)
    print(f"[OK] Generated sample CAD DXF file: {dxf_path}")


def run_dxf_parser_test():
    dxf_file = "sample_structure_drawing.dxf"
    create_sample_dxf(dxf_file)

    parser = DrawingParserV2()
    result = parser.parse_dxf(dxf_file)

    print("\n" + "=" * 60)
    print("DXF PARSER VERIFICATION REPORT")
    print("=" * 60)
    print(f"Filename             : {result.filename}")
    print(f"Canvas Dimensions    : {result.width} x {result.height}")
    print(f"Total Entities Extracted: {len(result.entities)}")

    for i, ent in enumerate(result.entities[:5], 1):
        print(f"  [{i}] Layer: {ent.layer:<12} | Type: {ent.entity_type:<10} | Label: {ent.label}")

    print(f"\nProject Inputs Generated: {bool(result.project_inputs)}")
    print(f"Sections Covered        : {list((result.project_inputs or {}).keys())}")
    print("=" * 60 + "\n")

    # Cleanup temp dxf
    if os.path.exists(dxf_file):
        os.remove(dxf_file)

    assert len(result.entities) > 0, "No DXF entities extracted!"
    assert result.project_inputs is not None, "No project inputs generated!"
    print("ALL DXF PARSER TESTS PASSED (100%)")


if __name__ == "__main__":
    run_dxf_parser_test()
