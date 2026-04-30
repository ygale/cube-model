'''Tests for the core cube model.'''

from rubik_cube_model import (
    CornerSticker,
    Cube,
    EdgeSticker,
    Side,
    solved,
)
from rubik_cube_model.navigation import corner_on_side, side_corners


def test_solved_counts() -> None:
    '''A solved cube has 24 directed corner and 24 directed edge entries.'''
    cube: Cube = solved()
    assert len(cube.next_edge) == 24
    assert len(cube.next_corner) == 24


def test_solved_home_is_corner_sticker() -> None:
    '''The home sticker is a CornerSticker.'''
    cube: Cube = solved()
    assert isinstance(cube.home, CornerSticker)


def test_solved_corner_three_cycle() -> None:
    '''Each corner sticker's other-other-other returns to itself.'''
    cube: Cube = solved()
    corner: CornerSticker
    for corner in cube.next_edge.keys():
        assert corner.other.other.other is corner


def test_solved_edge_two_cycle() -> None:
    '''Each edge sticker's other-other returns to itself.'''
    cube: Cube = solved()
    edge: EdgeSticker
    for edge in cube.next_corner.keys():
        assert edge.other.other is edge


def test_solved_face_cycle() -> None:
    '''next_corner[next_edge[c]] steps around the face in a 4-cycle.'''
    cube: Cube = solved()
    side: Side
    for side in Side:
        corners: list[CornerSticker] = side_corners(
            cube, corner_on_side(cube, side)
        )
        assert len(corners) == 4
        for i in range(4):
            edge: EdgeSticker = cube.next_edge[corners[i]]
            nxt: CornerSticker = cube.next_corner[edge]
            assert nxt is corners[(i + 1) % 4]


def test_solved_all_six_sides_reachable() -> None:
    '''corner_on_side returns a distinct corner for each side.'''
    cube: Cube = solved()
    home_corners: set[int] = set()
    side: Side
    for side in Side:
        home_corners.add(id(corner_on_side(cube, side)))
    assert len(home_corners) == 6
