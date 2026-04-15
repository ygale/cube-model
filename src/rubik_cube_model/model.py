from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum


class Color(Enum):
    WHITE = "white"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    ORANGE = "orange"
    RED = "red"


class Side(Enum):
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


@dataclass(eq=False, slots=True)
class Sticker(ABC):
    color: Color
    other: Sticker = field(init=False, repr=False)


@dataclass(eq=False, slots=True)
class CornerSticker(Sticker):
    other: CornerSticker = field(init=False, repr=False)


@dataclass(eq=False, slots=True)
class EdgeSticker(Sticker):
    other: EdgeSticker = field(init=False, repr=False)


@dataclass(slots=True)
class Cube:
    home: CornerSticker
    front_color: Color
    top_color: Color
    next_edge: dict[CornerSticker, EdgeSticker]
    next_corner: dict[EdgeSticker, CornerSticker]

    def __post_init__(self) -> None:
        self._validate_orientation()
        self._validate_adjacency()

    def _validate_orientation(self) -> None:
        if self.front_color is self.top_color:
            raise ValueError("front_color and top_color must be different")

    def _validate_adjacency(self) -> None:
        if len(self.next_edge) != 24:
            raise ValueError("next_edge must contain exactly 24 corner-to-edge links")
        if len(self.next_corner) != 24:
            raise ValueError("next_corner must contain exactly 24 edge-to-corner links")

        corners_from_next_edge = set(self.next_edge.keys())
        corners_from_next_corner = set(self.next_corner.values())
        edges_from_next_edge = set(self.next_edge.values())
        edges_from_next_corner = set(self.next_corner.keys())

        if len(corners_from_next_edge) != 24:
            raise ValueError("each corner sticker must appear exactly once in next_edge")
        if len(corners_from_next_corner) != 24:
            raise ValueError("each corner sticker must appear exactly once in next_corner")
        if len(edges_from_next_edge) != 24:
            raise ValueError("each edge sticker must appear exactly once in next_edge")
        if len(edges_from_next_corner) != 24:
            raise ValueError("each edge sticker must appear exactly once in next_corner")

        if corners_from_next_edge != corners_from_next_corner:
            raise ValueError("next_edge and next_corner must mention the same corner stickers")
        if edges_from_next_edge != edges_from_next_corner:
            raise ValueError("next_edge and next_corner must mention the same edge stickers")

    @classmethod
    def solved(cls, front_color: Color = Color.GREEN, top_color: Color = Color.WHITE) -> Cube:
        if front_color is top_color:
            raise ValueError("front_color and top_color must be different")

        # Corner cubies. Each triple is a circular linked list.
        f_ul, u_lf, l_fu = make_corner_stickers(Color.GREEN, Color.WHITE, Color.ORANGE)
        f_ur, r_fu, u_rf = make_corner_stickers(Color.GREEN, Color.RED, Color.WHITE)
        f_dr, d_rf, r_fd = make_corner_stickers(Color.GREEN, Color.YELLOW, Color.RED)
        f_dl, l_fd, d_lf = make_corner_stickers(Color.GREEN, Color.ORANGE, Color.YELLOW)

        b_ur, u_rb, r_bu = make_corner_stickers(Color.BLUE, Color.WHITE, Color.RED)
        b_ul, l_bu, u_lb = make_corner_stickers(Color.BLUE, Color.ORANGE, Color.WHITE)
        b_dl, d_lb, l_db = make_corner_stickers(Color.BLUE, Color.YELLOW, Color.ORANGE)
        b_dr, r_db, d_bd = make_corner_stickers(Color.BLUE, Color.RED, Color.YELLOW)

        # Edge cubies. Each pair is a circular linked list.
        f_u, u_f = make_edge_stickers(Color.GREEN, Color.WHITE)
        f_r, r_f = make_edge_stickers(Color.GREEN, Color.RED)
        f_d, d_f = make_edge_stickers(Color.GREEN, Color.YELLOW)
        f_l, l_f = make_edge_stickers(Color.GREEN, Color.ORANGE)

        u_r, r_u = make_edge_stickers(Color.WHITE, Color.RED)
        u_l, l_u = make_edge_stickers(Color.WHITE, Color.ORANGE)
        d_r, r_d = make_edge_stickers(Color.YELLOW, Color.RED)
        d_l, l_d = make_edge_stickers(Color.YELLOW, Color.ORANGE)

        b_u, u_b = make_edge_stickers(Color.BLUE, Color.WHITE)
        b_l, l_b = make_edge_stickers(Color.BLUE, Color.ORANGE)
        b_d, d_b = make_edge_stickers(Color.BLUE, Color.YELLOW)
        b_r, r_b = make_edge_stickers(Color.BLUE, Color.RED)

        next_edge: dict[CornerSticker, EdgeSticker] = {}
        next_corner: dict[EdgeSticker, CornerSticker] = {}

        def add_face_cycle(
            c0: CornerSticker,
            e0: EdgeSticker,
            c1: CornerSticker,
            e1: EdgeSticker,
            c2: CornerSticker,
            e2: EdgeSticker,
            c3: CornerSticker,
            e3: EdgeSticker,
        ) -> None:
            next_edge[c0] = e0
            next_corner[e0] = c1
            next_edge[c1] = e1
            next_corner[e1] = c2
            next_edge[c2] = e2
            next_corner[e2] = c3
            next_edge[c3] = e3
            next_corner[e3] = c0

        # Clockwise when looking directly at each face.
        add_face_cycle(f_ul, f_u, f_ur, f_r, f_dr, f_d, f_dl, f_l)
        add_face_cycle(b_ur, b_u, b_ul, b_l, b_dl, b_d, b_dr, b_r)
        add_face_cycle(u_lb, u_b, u_rb, u_r, u_rf, u_f, u_lf, u_l)
        add_face_cycle(d_lf, d_f, d_rf, d_r, d_bd, d_b, d_lb, d_l)
        add_face_cycle(r_fu, r_u, r_bu, r_b, r_db, r_d, r_fd, r_f)
        add_face_cycle(l_bu, l_u, l_fu, l_f, l_fd, l_d, l_db, l_b)

        return cls(
            home=f_ul,
            front_color=front_color,
            top_color=top_color,
            next_edge=next_edge,
            next_corner=next_corner,
        )


def make_corner_stickers(a: Color, b: Color, c: Color) -> tuple[CornerSticker, CornerSticker, CornerSticker]:
    first = CornerSticker(a)
    second = CornerSticker(b)
    third = CornerSticker(c)

    first.other = second
    second.other = third
    third.other = first

    return (first, second, third)


def make_edge_stickers(a: Color, b: Color) -> tuple[EdgeSticker, EdgeSticker]:
    first = EdgeSticker(a)
    second = EdgeSticker(b)

    first.other = second
    second.other = first

    return (first, second)
