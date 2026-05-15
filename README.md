# cube-model

An orientation-independent cube model in strictly typed Python.

## Highlights

- Strict typing (`mypy --strict`)
- Orientation-independent cube state
- `Color` and `Side` are enums
- `CornerSticker` objects form circular linked lists of size 3
- `EdgeSticker` objects form circular linked lists of size 2
- `Cube.next_edge` and `Cube.next_corner` encode clockwise sticker order on faces

## Install

```bash
pip install cube-model
```

## Example

```python
from cube_model import Color, Move, Multiplicity, Side, solved, move

cube = solved()
assert cube.front_color is Color.GREEN

move(Move(Side.FRONT, Multiplicity.CW), cube)
```

