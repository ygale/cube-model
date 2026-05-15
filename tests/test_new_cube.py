'''Tests for new cube.'''

from cube_integrity import check_cube_integrity
from cube_model import Cube, shuffled

def test_shuffled() -> None:
    '''Test integrity of shuffled cubes.'''
    cube: Cube = shuffled()
    check_cube_integrity(cube)
    for _ in range(20):
      cube = shuffled(initial=cube)
      check_cube_integrity(cube)

