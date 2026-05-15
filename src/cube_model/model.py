'''Core cube model: colors, sides, stickers, and the Cube dataclass.'''

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto

class Color(Enum):
  '''Enumeration of the six cube colors.'''
  WHITE = auto()
  YELLOW = auto()
  RED = auto()
  ORANGE = auto()
  BLUE = auto()
  GREEN = auto()

class Side(Enum):
  '''Enumeration of the six cube sides.'''
  FRONT = auto()
  BACK = auto()
  LEFT = auto()
  RIGHT = auto()
  TOP = auto()
  BOTTOM = auto()

@dataclass(eq=False)
class Sticker(ABC):
  '''Abstract sticker with a color and cyclic partner.'''
  color: Color
  other: Sticker = field(init=False)
  _hash: int = field(init=False, repr=False, compare=False)

  def __post_init__(self) -> None:
    '''Initialize as a self-loop before wiring.'''
    self._rewire(self)

  def _rewire(self, other: Sticker) -> None:
    '''Set partner and recompute hash.'''
    self.other = other
    self._hash = hash((self.color, other.color))

  def __eq__(self, other: object) -> bool:
    '''Equality based on color pair.'''
    if not isinstance(other, Sticker):
      return NotImplemented
    return (
      self.color == other.color
      and self.other.color == other.other.color
    )

  def __hash__(self) -> int:
    '''Hash based on this sticker's color and its partner's color.'''
    return self._hash

@dataclass(eq=False)
class CornerSticker(Sticker):
  '''Corner sticker linked in a 3-cycle.'''
  other: CornerSticker = field(init=False)

@dataclass(eq=False)
class EdgeSticker(Sticker):
  '''Edge sticker linked in a 2-cycle.'''
  other: EdgeSticker = field(init=False)

@dataclass
class Cube:
  '''Cube defined by one corner and cyclic adjacency maps.'''
  home: CornerSticker
  front_color: Color
  top_color: Color
  next_edge:   dict[CornerSticker, EdgeSticker]
  next_corner: dict[EdgeSticker, CornerSticker]

# Opposite face for each side.
opp_side: dict[Side, Side] = {
    Side.LEFT:   Side.RIGHT,
    Side.RIGHT:  Side.LEFT,
    Side.BOTTOM: Side.TOP,
    Side.TOP:    Side.BOTTOM,
    Side.BACK:   Side.FRONT,
    Side.FRONT:  Side.BACK,
}

def shallow_copy(cube: Cube) -> Cube:
  '''Return a new Cube sharing all sticker objects but with new dicts.

  Moves only reassign dict values (which sticker a key maps to); they
  never mutate sticker objects themselves. A shallow copy therefore
  gives full independence between the two cubes without allocating new
  sticker objects.
  '''
  return Cube(
    home=cube.home,
    front_color=cube.front_color,
    top_color=cube.top_color,
    next_edge=dict(cube.next_edge),
    next_corner=dict(cube.next_corner),
  )
