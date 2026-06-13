'''Tests for all 54 simple actions on a solved cube.

Checks both sticker colors via _colors and structural integrity
via check_cube_integrity for each action.
'''

import pytest
from cube_integrity import check_cube_integrity
from cube_model import all_colors, solved
from cube_model.action import Action, act, parse_actions
from cube_model.model import Color, Cube, Side

def _colors(cube: Cube) -> dict[str, str]:
  '''Summarise all_colors as a compact dict.

  Keys: first two chars of each Side name, lower-case.
  Values: concatenation of the first char of each Color name for
  the eight stickers returned by all_colors, in clockwise order.
  '''
  colors_map: dict[Side, list[Color]] = all_colors(cube)
  result: dict[str, str] = {}
  side: Side
  for side in Side:
    key: str = side.name[:2].lower()
    value: str = ''.join(c.name[0] for c in colors_map[side])
    result[key] = value
  return result

ACTION_COLORS: dict[str, dict[str, str]] = {
  'U':  {'fr': 'RRRGGGGG', 'ba': 'OBBBBBOO', 'le': 'GOOOOOGG',
         'ri': 'BBBRRRRR', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  "U'": {'fr': 'OOOGGGGG', 'ba': 'RBBBBBRR', 'le': 'BOOOOOBB',
         'ri': 'GGGRRRRR', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'U2': {'fr': 'BBBGGGGG', 'ba': 'GBBBBBGG', 'le': 'ROOOOORR',
         'ri': 'OOORRRRR', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'D':  {'fr': 'GGGGOOOG', 'ba': 'BBRRRBBB', 'le': 'OOBBBOOO',
         'ri': 'RRRRGGGR', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  "D'": {'fr': 'GGGGRRRG', 'ba': 'BBOOOBBB', 'le': 'OOGGGOOO',
         'ri': 'RRRRBBBR', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'D2': {'fr': 'GGGGBBBG', 'ba': 'BBGGGBBB', 'le': 'OORRROOO',
         'ri': 'RRRROOOR', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'F':  {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'YYYOOOOO',
         'ri': 'WRRRRRWW', 'to': 'OWWWWWOO', 'bo': 'RRRYYYYY'},
  "F'": {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'WWWOOOOO',
         'ri': 'YRRRRRYY', 'to': 'RWWWWWRR', 'bo': 'OOOYYYYY'},
  'F2': {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'RRROOOOO',
         'ri': 'ORRRRROO', 'to': 'YWWWWWYY', 'bo': 'WWWYYYYY'},
  'B':  {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOOWWWO',
         'ri': 'RRYYYRRR', 'to': 'WWRRRWWW', 'bo': 'YYYYOOOY'},
  "B'": {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOOYYYO',
         'ri': 'RRWWWRRR', 'to': 'WWOOOWWW', 'bo': 'YYYYRRRY'},
  'B2': {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOORRRO',
         'ri': 'RROOORRR', 'to': 'WWYYYWWW', 'bo': 'YYYYWWWY'},
  'L':  {'fr': 'WGGGGGWW', 'ba': 'YYYBBBBB', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'BBBWWWWW', 'bo': 'GYYYYYGG'},
  "L'": {'fr': 'YGGGGGYY', 'ba': 'WWWBBBBB', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'GGGWWWWW', 'bo': 'BYYYYYBB'},
  'L2': {'fr': 'BGGGGGBB', 'ba': 'GGGBBBBB', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'YYYWWWWW', 'bo': 'WYYYYYWW'},
  'R':  {'fr': 'GGYYYGGG', 'ba': 'BBBBWWWB', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWWGGGW', 'bo': 'YYBBBYYY'},
  "R'": {'fr': 'GGWWWGGG', 'ba': 'BBBBYYYB', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWWBBBW', 'bo': 'YYGGGYYY'},
  'R2': {'fr': 'GGBBBGGG', 'ba': 'BBBBGGGB', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWWYYYW', 'bo': 'YYWWWYYY'},
  'x':  {'fr': 'YYYYYYYY', 'ba': 'WWWWWWWW', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'GGGGGGGG', 'bo': 'BBBBBBBB'},
  "x'": {'fr': 'WWWWWWWW', 'ba': 'YYYYYYYY', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'BBBBBBBB', 'bo': 'GGGGGGGG'},
  'x2': {'fr': 'BBBBBBBB', 'ba': 'GGGGGGGG', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'YYYYYYYY', 'bo': 'WWWWWWWW'},
  'y':  {'fr': 'RRRRRRRR', 'ba': 'OOOOOOOO', 'le': 'GGGGGGGG',
         'ri': 'BBBBBBBB', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  "y'": {'fr': 'OOOOOOOO', 'ba': 'RRRRRRRR', 'le': 'BBBBBBBB',
         'ri': 'GGGGGGGG', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'y2': {'fr': 'BBBBBBBB', 'ba': 'GGGGGGGG', 'le': 'RRRRRRRR',
         'ri': 'OOOOOOOO', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'z':  {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'YYYYYYYY',
         'ri': 'WWWWWWWW', 'to': 'OOOOOOOO', 'bo': 'RRRRRRRR'},
  "z'": {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'WWWWWWWW',
         'ri': 'YYYYYYYY', 'to': 'RRRRRRRR', 'bo': 'OOOOOOOO'},
  'z2': {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'RRRRRRRR',
         'ri': 'OOOOOOOO', 'to': 'YYYYYYYY', 'bo': 'WWWWWWWW'},
  'M':  {'fr': 'GYGGGYGG', 'ba': 'BBBWBBBW', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWGWWWG', 'bo': 'YBYYYBYY'},
  "M'": {'fr': 'GWGGGWGG', 'ba': 'BBBYBBBY', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWBWWWB', 'bo': 'YGYYYGYY'},
  'M2': {'fr': 'GBGGGBGG', 'ba': 'BBBGBBBG', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWYWWWY', 'bo': 'YWYYYWYY'},
  'E':  {'fr': 'GGGRGGGR', 'ba': 'BOBBBOBB', 'le': 'OGOOOGOO',
         'ri': 'RRRBRRRB', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  "E'": {'fr': 'GGGOGGGO', 'ba': 'BRBBBRBB', 'le': 'OBOOOBOO',
         'ri': 'RRRGRRRG', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'E2': {'fr': 'GGGBGGGB', 'ba': 'BGBBBGBB', 'le': 'OROOOROO',
         'ri': 'RRRORRRO', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'S':  {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOYOOOY',
         'ri': 'RWRRRWRR', 'to': 'WOWWWOWW', 'bo': 'YYYRYYYR'},
  "S'": {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOWOOOW',
         'ri': 'RYRRRYRR', 'to': 'WRWWWRWW', 'bo': 'YYYOYYYO'},
  'S2': {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOROOOR',
         'ri': 'RORRRORR', 'to': 'WYWWWYWW', 'bo': 'YYYWYYYW'},
  'u':  {'fr': 'RRRRGGGR', 'ba': 'OOBBBOOO', 'le': 'GGOOOGGG',
         'ri': 'BBBBRRRB', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  "u'": {'fr': 'OOOOGGGO', 'ba': 'RRBBBRRR', 'le': 'BBOOOBBB',
         'ri': 'GGGGRRRG', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'u2': {'fr': 'BBBBGGGB', 'ba': 'GGBBBGGG', 'le': 'RROOORRR',
         'ri': 'OOOORRRO', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'd':  {'fr': 'GGGOOOOO', 'ba': 'BRRRRRBB', 'le': 'OBBBBBOO',
         'ri': 'RRRGGGGG', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  "d'": {'fr': 'GGGRRRRR', 'ba': 'BOOOOOBB', 'le': 'OGGGGGOO',
         'ri': 'RRRBBBBB', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'd2': {'fr': 'GGGBBBBB', 'ba': 'BGGGGGBB', 'le': 'ORRRRROO',
         'ri': 'RRROOOOO', 'to': 'WWWWWWWW', 'bo': 'YYYYYYYY'},
  'f':  {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'YYYYOOOY',
         'ri': 'WWRRRWWW', 'to': 'OOWWWOOO', 'bo': 'RRRRYYYR'},
  "f'": {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'WWWWOOOW',
         'ri': 'YYRRRYYY', 'to': 'RRWWWRRR', 'bo': 'OOOOYYYO'},
  'f2': {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'RRRROOOR',
         'ri': 'OORRROOO', 'to': 'YYWWWYYY', 'bo': 'WWWWYYYW'},
  'b':  {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOWWWWW',
         'ri': 'RYYYYYRR', 'to': 'WRRRRRWW', 'bo': 'YYYOOOOO'},
  "b'": {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOOYYYYY',
         'ri': 'RWWWWWRR', 'to': 'WOOOOOWW', 'bo': 'YYYRRRRR'},
  'b2': {'fr': 'GGGGGGGG', 'ba': 'BBBBBBBB', 'le': 'OOORRRRR',
         'ri': 'ROOOOORR', 'to': 'WYYYYYWW', 'bo': 'YYYWWWWW'},
  'l':  {'fr': 'WWGGGWWW', 'ba': 'YYYYBBBY', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'BBBBWWWB', 'bo': 'GGYYYGGG'},
  "l'": {'fr': 'YYGGGYYY', 'ba': 'WWWWBBBW', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'GGGGWWWG', 'bo': 'BBYYYBBB'},
  'l2': {'fr': 'BBGGGBBB', 'ba': 'GGGGBBBG', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'YYYYWWWY', 'bo': 'WWYYYWWW'},
  'r':  {'fr': 'GYYYYYGG', 'ba': 'BBBWWWWW', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWGGGGG', 'bo': 'YBBBBBYY'},
  "r'": {'fr': 'GWWWWWGG', 'ba': 'BBBYYYYY', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWBBBBB', 'bo': 'YGGGGGYY'},
  'r2': {'fr': 'GBBBBBGG', 'ba': 'BBBGGGGG', 'le': 'OOOOOOOO',
         'ri': 'RRRRRRRR', 'to': 'WWWYYYYY', 'bo': 'YWWWWWYY'},
}

_TOKENS: list[str] = list(ACTION_COLORS)

@pytest.mark.parametrize('token', _TOKENS)
def test_simple_action_colors(token: str) -> None:
  '''_colors matches expected snapshot after applying token to a solved cube.'''
  actions: list[Action] = parse_actions(token)
  cube: Cube = solved()
  act(actions[0], cube)
  assert _colors(cube) == ACTION_COLORS[token]

@pytest.mark.parametrize('token', _TOKENS)
def test_simple_action_integrity(token: str) -> None:
  '''Cube integrity holds after applying token to a solved cube.'''
  actions: list[Action] = parse_actions(token)
  cube: Cube = solved()
  act(actions[0], cube)
  check_cube_integrity(cube)
