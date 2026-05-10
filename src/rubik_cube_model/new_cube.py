'''Construct a Cube from explicit corner and edge color sequences.'''

from collections.abc import Sequence
from random import randrange, shuffle

from .model import (
  Color,
  CornerSticker,
  Cube,
  EdgeSticker,
  Side,
)
from .utils import even_permutation, rand_elt, to_radix

_OPPOSITE: dict[Color, Color] = {
  Color.WHITE:  Color.YELLOW,
  Color.YELLOW: Color.WHITE,
  Color.RED:    Color.ORANGE,
  Color.ORANGE: Color.RED,
  Color.BLUE:   Color.GREEN,
  Color.GREEN:  Color.BLUE,
}

def new_cube(
  corners:     Sequence[tuple[Color, Color, Color]],
  edges:       Sequence[tuple[Color, Color]],
  front_color: Color,
  top_color:   Color,
  initial:     Cube | None = None,
) -> Cube:
  '''Construct a Cube from explicit corner and edge color sequences.

  corners is 8 tuples: the 4 front-face corners starting at home
  clockwise, then the 4 back-face corners starting at the corner
  opposite home clockwise when facing the back. The first element
  of each tuple is the color of the sticker on the front or back
  face.

  edges is 12 tuples: 4 front-face edges starting just after home
  clockwise, then 4 middle-layer edges starting next to the home
  corner then clockwise when facing the front, then 4 back-face
  edges starting just after the corner opposite home clockwise when
  facing the back. The first element of each tuple is the color of
  the sticker touching the front or back face, or the leading
  sticker for the middle layer.

  If initial is supplied, its sticker objects are reused instead of
  allocating new ones. Each directed sticker is uniquely identified
  by (sticker.color, sticker.other.color).
  '''
  existing_edges:   dict[tuple[Color, Color], EdgeSticker]
  existing_corners: dict[tuple[Color, Color], CornerSticker]
  if initial is not None:
    existing_edges = {
      (es.color, es.other.color): es
      for es in initial.next_corner.keys()
    }
    existing_corners = {
      (cs.color, cs.other.color): cs
      for cs in initial.next_edge.keys()
    }
  else:
    existing_edges   = {}
    existing_corners = {}

  edge_stickers: dict[tuple[Color, Color], EdgeSticker] = {}
  corner_stickers: dict[tuple[Color, Color], CornerSticker] = {}

  def make_edge(a: Color, b: Color) -> None:
    '''Create or reuse one edge cubie with two stickers.'''
    if (a, b) in existing_edges:
      s_ab: EdgeSticker = existing_edges[(a, b)]
      s_ba: EdgeSticker = existing_edges[(b, a)]
    else:
      s_ab = EdgeSticker(a)
      s_ba = EdgeSticker(b)
      s_ab._rewire(s_ba)
      s_ba._rewire(s_ab)
    edge_stickers[(a, b)] = s_ab
    edge_stickers[(b, a)] = s_ba

  et: tuple[Color, Color]
  for et in edges:
    make_edge(*et)

  next_edge:   dict[CornerSticker, EdgeSticker] = {}
  next_corner: dict[EdgeSticker, CornerSticker] = {}

  def make_corner(a: Color, b: Color, c: Color) -> CornerSticker:
    '''Create or reuse a corner cubie with three stickers. Return
    the first sticker of the cubie.'''
    if (a, b) in existing_corners:
      s: tuple[CornerSticker, CornerSticker, CornerSticker] = (
        existing_corners[(a, b)],
        existing_corners[(b, c)],
        existing_corners[(c, a)],
      )
    else:
      s = (
        CornerSticker(a),
        CornerSticker(b),
        CornerSticker(c),
      )
      s[0]._rewire(s[1])
      s[1]._rewire(s[2])
      s[2]._rewire(s[0])
    corner_stickers[(a, b)] = s[0]
    corner_stickers[(b, c)] = s[1]
    corner_stickers[(c, a)] = s[2]
    return s[0]

  home: CornerSticker = make_corner(*corners[0])
  ct: tuple[Color, Color, Color]
  for ct in corners[1:]:
    make_corner(*ct)

  cs: CornerSticker
  es: EdgeSticker
  i: int

  # wire next links along front face
  for i in range(4):
    ct = corners[i]
    cs = corner_stickers[ct[:2]]

    et = edges[i]
    es = edge_stickers[et]
    next_edge[cs] = es
    next_corner[es.other] = cs.other.other

    et = edges[(i + 3) % 4]
    es = edge_stickers[et]
    next_edge[cs.other] = es.other
    next_corner[es] = cs

    et = edges[i + 4]
    es = edge_stickers[et]
    next_edge[cs.other.other] = es
    next_corner[es.other] = cs.other

  # wire next links along back face
  for i in range(4, 8):
    ct = corners[i]
    cs = corner_stickers[ct[:2]]

    et = edges[i + 4]
    es = edge_stickers[et]
    next_edge[cs] = es
    next_corner[es.other] = cs.other.other

    et = edges[(i + 3) % 4 + 8]
    es = edge_stickers[et]
    next_edge[cs.other] = es.other
    next_corner[es] = cs

    et = edges[3 * i % 4 + 4]
    es = edge_stickers[et]
    next_edge[cs.other.other] = es.other
    next_corner[es] = cs.other

  return Cube(
    home=home,
    front_color=front_color,
    top_color=top_color,
    next_edge=next_edge,
    next_corner=next_corner,
  )

# Solved-state sequences.
# Corners: front face CW from home, then back face CW facing back
# from opposite-home. Tuple[0] is the front or back face sticker.
_SOLVED_CORNERS: list[tuple[Color, Color, Color]] = [
  (Color.GREEN,  Color.ORANGE, Color.WHITE),
  (Color.GREEN,  Color.WHITE,  Color.RED),
  (Color.GREEN,  Color.RED,    Color.YELLOW),
  (Color.GREEN,  Color.YELLOW, Color.ORANGE),
  (Color.BLUE,   Color.WHITE,  Color.ORANGE),
  (Color.BLUE,   Color.ORANGE, Color.YELLOW),
  (Color.BLUE,   Color.YELLOW, Color.RED),
  (Color.BLUE,   Color.RED,    Color.WHITE),
]

# Edges: front face CW after home, middle layer CW facing front from
# next-to-home, back face CW after opposite-home. Tuple[0] is the
# front/back sticker or the leading middle-layer sticker.
_SOLVED_EDGES: list[tuple[Color, Color]] = [
  (Color.GREEN,  Color.WHITE),
  (Color.GREEN,  Color.RED),
  (Color.GREEN,  Color.YELLOW),
  (Color.GREEN,  Color.ORANGE),
  (Color.WHITE,  Color.ORANGE),
  (Color.RED,    Color.WHITE),
  (Color.YELLOW, Color.RED),
  (Color.ORANGE, Color.YELLOW),
  (Color.BLUE,   Color.ORANGE),
  (Color.BLUE,   Color.YELLOW),
  (Color.BLUE,   Color.RED),
  (Color.BLUE,   Color.WHITE),
]

_ALL_COLORS: list[Color] = list(Color)

_GB: frozenset[Color] = frozenset({Color.GREEN,  Color.BLUE  })
_OR: frozenset[Color] = frozenset({Color.ORANGE, Color.RED   })
_WY: frozenset[Color] = frozenset({Color.WHITE,  Color.YELLOW})

def center_parity_even(front_color: Color, top_color: Color) -> bool:
  '''Return True if the center orientation is an even permutation.

  The center permutation is even when the front and top colors are in
  one of the three cyclic-neighbor pairs: (GB, WY), (WY, OR), (OR, GB),
  where GB = {Green, Blue}, WY = {White, Yellow}, OR = {Orange, Red}.
  '''
  return (
       front_color in _GB and top_color in _WY
    or front_color in _WY and top_color in _OR
    or front_color in _OR and top_color in _GB)

def solved(initial: Cube | None = None) -> Cube:
  '''Construct a solved cube.

  If initial is supplied, reuse its sticker objects instead of
  allocating new ones.
  '''
  return new_cube(
    corners=_SOLVED_CORNERS,
    edges=_SOLVED_EDGES,
    front_color=Color.GREEN,
    top_color=Color.WHITE,
    initial=initial,
  )

def shuffled(initial: Cube | None = None) -> Cube:
  '''Construct a solvable randomly shuffled cube.

  The front color is chosen uniformly at random. To ensure a valid
  cube, the top color is chosen uniformly at random only from the
  four colors that are neither the front color nor its opposite.

  Corners and edges are permuted randomly. To ensure solvability, the
  first two edges are transposed if needed so that the corner, edge,
  and center permutation parities satisfy the three-way XOR invariant.

  Edge orientations: a random integer in [0, 2**11) determines which
  of the first 11 edges are flipped. To ensure solvability, the 12th
  is flipped if needed to keep the total number of flips even.

  Corner orientations: a random integer in [0, 3**7) is interpreted
  in base 3 to twist the first 7 corners. To ensure solvability,
  the 8th corner is twisted so that the total twist sum is
  divisible by 3.

  If initial is supplied, its sticker objects are reused.

  '''
  front_color: Color = rand_elt(_ALL_COLORS)
  top_color: Color = rand_elt([c for c in _ALL_COLORS
    if c is not front_color
    and c is not _OPPOSITE[front_color]])

  corners: list[tuple[Color, Color, Color]] = list(_SOLVED_CORNERS)
  edges:   list[tuple[Color, Color]]        = list(_SOLVED_EDGES)

  shuffle(corners)
  shuffle(edges)

  corner_even: bool = even_permutation(corners, _SOLVED_CORNERS)
  edge_even: bool = even_permutation(edges, _SOLVED_EDGES)
  center_even: bool = center_parity_even(front_color, top_color)
  if not (corner_even ^ edge_even ^ center_even):
    edges[0], edges[1] = edges[1], edges[0]

  edge_bits: int = randrange(2 ** 11)
  flips: int = 0
  for i in range(11):
    if edge_bits & (1 << i):
      edges[i] = (edges[i][1], edges[i][0])
      flips += 1
  if flips % 2 == 1:
    edges[11] = (edges[11][1], edges[11][0])

  twists: list[int] = list(to_radix(3, randrange(3 ** 7)))
  twists.append(2 * sum(twists) % 3)
  for i, twist in enumerate(twists):
    match twist:
      case 1:
        a, b, c = corners[i]
        corners[i] = (c, a, b)
      case 2:
        a, b, c = corners[i]
        corners[i] = (b, c, a)

  return new_cube(
    corners=corners,
    edges=edges,
    front_color=front_color,
    top_color=top_color,
    initial=initial,
  )
