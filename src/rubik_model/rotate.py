'''Rigid rotation of the Rubik's cube.'''

from .new_cube import solved
from .model import (
    Color,
    Cube,
    Side,
    opp_side,
    shallow_copy,
)
from .move import Move, Multiplicity, invert
from .navigation import (
    Nav,
    nav_cc,
    parse_navs,
    side_color,
)

HOME_TRANSITIONS: dict[Move, list[Nav]] = {
    Move(Side.FRONT, Multiplicity.CW):  parse_navs('ONNO'),
    Move(Side.FRONT, Multiplicity.CCW): parse_navs('NN'),
    Move(Side.FRONT, Multiplicity.TWO): parse_navs('NNNN'),
    Move(Side.RIGHT, Multiplicity.CW):  parse_navs('ONNOO'),
    Move(Side.RIGHT, Multiplicity.CCW): parse_navs('OONN'),
    Move(Side.RIGHT, Multiplicity.TWO): parse_navs('ONNNNOO'),
    Move(Side.TOP, Multiplicity.CW):    parse_navs('NNOO'),
    Move(Side.TOP, Multiplicity.CCW):   parse_navs('OONNO'),
    Move(Side.TOP, Multiplicity.TWO):   parse_navs('OONNNNO'),
}

for _side in (Side.LEFT, Side.BOTTOM, Side.BACK):
    for _mult in Multiplicity:
        HOME_TRANSITIONS[Move(_side, _mult)] = HOME_TRANSITIONS[
            Move(opp_side[_side], invert[_mult])
        ]

COLOR_TRANSITIONS: dict[tuple[Move, Color, Color], tuple[Color, Color]] = {}

def _build_color_transitions() -> None:
    '''Populate COLOR_TRANSITIONS dynamically using side_color.'''
    dummy: Cube = solved()
    opp_color: dict[Color, Color] = {
        side_color(dummy, side): side_color(dummy, opp)
        for side, opp in opp_side.items()
    }
    m_f_cw  = Move(Side.FRONT, Multiplicity.CW)
    m_f_ccw = Move(Side.FRONT, Multiplicity.CCW)
    m_f_two = Move(Side.FRONT, Multiplicity.TWO)
    m_r_cw  = Move(Side.RIGHT, Multiplicity.CW)
    m_r_ccw = Move(Side.RIGHT, Multiplicity.CCW)
    m_r_two = Move(Side.RIGHT, Multiplicity.TWO)
    m_t_cw  = Move(Side.TOP, Multiplicity.CW)
    m_t_ccw = Move(Side.TOP, Multiplicity.CCW)
    m_t_two = Move(Side.TOP, Multiplicity.TWO)
    for f in Color:
        for t in Color:
            if f == t or t == opp_color[f]:
                continue
            dummy.front_color = f
            dummy.top_color = t
            left_c:   Color = side_color(dummy, Side.LEFT)
            right_c:  Color = side_color(dummy, Side.RIGHT)
            bottom_c: Color = side_color(dummy, Side.BOTTOM)
            back_c:   Color = side_color(dummy, Side.BACK)
            COLOR_TRANSITIONS[(m_f_cw,  f, t)] = (f, left_c)
            COLOR_TRANSITIONS[(m_f_ccw, f, t)] = (f, right_c)
            COLOR_TRANSITIONS[(m_f_two, f, t)] = (f, bottom_c)
            COLOR_TRANSITIONS[(m_r_cw,  f, t)] = (bottom_c, f)
            COLOR_TRANSITIONS[(m_r_ccw, f, t)] = (t, back_c)
            COLOR_TRANSITIONS[(m_r_two, f, t)] = (back_c, bottom_c)
            COLOR_TRANSITIONS[(m_t_cw,  f, t)] = (right_c, t)
            COLOR_TRANSITIONS[(m_t_ccw, f, t)] = (left_c, t)
            COLOR_TRANSITIONS[(m_t_two, f, t)] = (back_c, t)
    for side in (Side.LEFT, Side.BOTTOM, Side.BACK):
        for mult in Multiplicity:
            opp: Side = opp_side[side]
            inv: Multiplicity = invert[mult]
            for f in Color:
                for t in Color:
                    if f == t or t == opp_color[f]:
                        continue
                    m: Move = Move(side, mult)
                    opp_m: Move = Move(opp, inv)
                    COLOR_TRANSITIONS[(m, f, t)] = (
                        COLOR_TRANSITIONS[(opp_m, f, t)]
                    )

_build_color_transitions()

def rotate(move: Move, cube: Cube) -> None:
    '''Rotate the cube rigidly in-place.'''
    steps: list[Nav] = HOME_TRANSITIONS[move]
    cube.home = nav_cc(steps, cube, cube.home)
    new_f, new_t = COLOR_TRANSITIONS[
        (move, cube.front_color, cube.top_color)
    ]
    cube.front_color = new_f
    cube.top_color = new_t

def rotated(move: Move, cube: Cube) -> Cube:
    '''Return a new cube after rotating it rigidly.'''
    new_cube: Cube = shallow_copy(cube)
    rotate(move, new_cube)
    return new_cube
