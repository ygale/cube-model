'''Tests for the core cube model.'''

from cube_integrity import check_cube_integrity
from rubik_model import solved

def test_integrity_solved() -> None:
    '''Integrity holds for a solved cube.'''
    check_cube_integrity(solved())
