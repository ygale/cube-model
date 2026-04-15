# rubik-cube-model

A Poetry-based Python package that models a Rubik's Cube using linked sticker
objects and per-face clockwise adjacency mappings.

## Highlights

- Strict typing (`mypy --strict`)
- Orientation-independent cube state
- `Color` and `Side` are enums
- `CornerSticker` objects form circular linked lists of size 3
- `EdgeSticker` objects form circular linked lists of size 2
- `Cube.next_edge` and `Cube.next_corner` encode clockwise sticker order on faces

## Install

```bash
poetry install
```

## Example

```python
from rubik_cube_model import Color, Cube

cube = Cube.solved(front_color=Color.GREEN, top_color=Color.WHITE)
assert cube.home.color is Color.GREEN
```
