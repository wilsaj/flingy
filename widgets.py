"""all the things that we need"""

from functools import partial
import itertools
from random import random

from kivy.clock import Clock
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.widget import Widget


class AimLine(Widget):
    start_pt = ListProperty([0, 0])
    end_pt = ListProperty([0, 0])

    def __init__(self, start_pt, **kwargs):
        super(AimLine, self).__init__(**kwargs)
        self.start_pt = start_pt
        self.end_pt = start_pt


class BlackHole(Widget):
    r = NumericProperty(25.)
    mass = NumericProperty(50.)

    def __init__(self, **kwargs):
        super(BlackHole, self).__init__(**kwargs)

    def collide_point(self, x, y):
        if (Vector(x, y) - Vector(self.pos)).length() < self.r:
            return True


class GoalPoint(Widget):
    r = NumericProperty(5.)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, **kwargs):
        super(GoalPoint, self).__init__(**kwargs)

    def collide_point(self, x, y):
        if (Vector(x, y) - Vector(self.pos)).length() < self.r:
            return True

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y


class Rocket(Widget):
    l = NumericProperty(20.)
    w = NumericProperty(8.)
    tip_l = NumericProperty(1.5)
    tip_w = NumericProperty(1.5)
    motion_v = ListProperty([0, 0])
    boost = BooleanProperty(False)
    quad_points = ListProperty([0, 0, 0, 0, 0, 0, 0, 0])
    # tip_points = ListProperty([0, 0, 0, 0, 0, 0])

    def __init__(self, **kwargs):
        super(Rocket, self).__init__(**kwargs)

    def update_points(self):
        m_v = Vector(self.motion_v)
        l_v = m_v.normalize() * self.l / 2.
        # orthogonal vector
        o_v = m_v.normalize().rotate(90) * self.w / 2.
        self.quad_points = [self.x - (l_v + o_v)[0], self.y - (l_v + o_v)[1],
                            self.x + (l_v - o_v)[0], self.y + (l_v - o_v)[1],
                            self.x + (l_v + o_v)[0], self.y + (l_v + o_v)[1],
                            self.x - (l_v - o_v)[0], self.y - (l_v - o_v)[1],
                            ]

        # self.tip_points = [
        #     self.x + (l_v * self.tip_l)[0], self.y + (l_v * self.tip_l)[1],
        #     self.x + (l_v + (o_v + Vector(self.tip_w, 0)))[0], self.y + (l_v + (o_v + Vector(self.tip_w, 0)))[1],
        #     self.x + (l_v - (o_v - Vector(self.tip_w, 0)))[0], self.y + (l_v + (o_v - Vector(self.tip_w, 0)))[1],
        #     ]

    def move(self):
        if self.boost:
            m_v = Vector(self.motion_v)
            self.motion_v = m_v + m_v.normalize()
        self.x += self.motion_v[0]
        self.y += self.motion_v[1]
        self.update_points()

    def gravitate_towards(self, body):
        m_v = Vector(self.motion_v)
        g_v = Vector(body.pos) - Vector(self.pos)
        self.motion_v = m_v + (g_v * 1. / g_v.length2()) * body.mass


class Shot(Widget):
    r = NumericProperty(10.)
    mass = NumericProperty(1.)
    motion_v = ListProperty([0, 0])

    def __init__(self, motion_v, **kwargs):
        super(Shot, self).__init__(**kwargs)
        self.motion_v = motion_v

    def move(self):
        self.x += self.motion_v[0]
        self.y += self.motion_v[1]

    def gravitate_towards(self, body):
        m_v = Vector(self.motion_v)
        g_v = Vector(body.pos) - Vector(self.pos)
        self.motion_v = m_v + (g_v * 1. / g_v.length2()) * body.mass

    def collide_wall(self, wall):
        if hasattr(self, 'last_bounced') and self.last_bounced == wall:
            return

        deflect_edge = None
        m_v = Vector(self.motion_v)
        pos_v = Vector(self.pos)

        edge_points = zip(wall.quad_points[0::2], wall.quad_points[1::2])
        edges = [
            (edge_points[0], edge_points[1]),
            (edge_points[1], edge_points[2]),
            (edge_points[2], edge_points[3]),
            (edge_points[3], edge_points[0]),
            ]

        closest_point = None

        for point in edge_points:
            if (pos_v - Vector(point)).length() < self.r:
                if not closest_point or \
                   (pos_v - Vector(point)).length() < (Vector(closest_point) - Vector(point)).length():
                    closest_point = point

        if closest_point:
            # take the deflection edge to be the normal of here to the corner
            deflect_edge = (pos_v - Vector(point)).rotate(90)

        else:
            for edge in edges:
                e0 = Vector(edge[0])
                e1 = Vector(edge[1])

                ortho_v = (e0 - e1).rotate(90).normalize()
                dist_v = Vector.line_intersection(self.pos, pos_v + ortho_v,
                                                  edge[0], edge[1])

                # dist_v will be None if we happen to be parallel
                if not dist_v:
                    continue

                dist_from_edge = (pos_v - dist_v).length()

                # if the shot touches the wall here
                if min(e0[0], e1[0]) <= dist_v[0] <= max(e0[0], e1[0]) and \
                   min(e0[1], e1[1]) <= dist_v[1] <= max(e0[1], e1[1]) and \
                   dist_from_edge < self.r + (wall.thickness / 2.):
                    if not deflect_edge:
                        deflect_edge = e0 - e1
                        dist_from_deflect_edge = dist_from_edge

                    elif dist_from_edge < dist_from_deflect_edge:
                        deflect_edge = e0 - e1
                        dist_from_deflect_edge = dist_from_edge

        if deflect_edge:
            self.motion_v = m_v.rotate(-2 * m_v.angle(deflect_edge))
            self.last_bounced = wall


class Stars(Widget):
    points = ListProperty([(0, 0), (0, 0), (0, 0)])

    def __init__(self, number_of_stars, **kwargs):
        super(Stars, self).__init__(**kwargs)
        Clock.schedule_once(partial(self.add_stars, number_of_stars), -1)

    def add_stars(self, number_of_stars, dt):
        width = self.parent.width
        height = self.parent.height
        self.points[0] = list(itertools.chain(*[
                    (random() * width, random() * height)
                    for i in xrange(number_of_stars)]))
        self.points[1] = list(itertools.chain(*[
                    (random() * width, random() * height)
                    for i in xrange(number_of_stars / 3)]))
        self.points[2] = list(itertools.chain(*[
                    (random() * width, random() * height)
                    for i in xrange(number_of_stars / 50)]))


class Wall(Widget):
    start_point = ListProperty([0, 0])
    end_point = ListProperty([0, 0])
    thickness = NumericProperty(4.)
    quad_points = ListProperty([0, 0, 0, 0, 0, 0, 0, 0])

    def __init__(self, start_point, end_point, **kwargs):
        super(Wall, self).__init__(**kwargs)
        self.start_point = start_point
        self.end_point = end_point
        self.update_points()

    def update_points(self):
        v = Vector(self.start_point[0] - self.end_point[0],
                   self.start_point[1] - self.end_point[1])
        # orthogonal vector
        o_v = v.normalize().rotate(90) * self.thickness / 2.
        self.quad_points = [
            self.start_point[0] + o_v[0], self.start_point[1] + o_v[1],
            self.start_point[0] - o_v[0], self.start_point[1] - o_v[1],
            self.end_point[0] - o_v[0], self.end_point[1] - o_v[1],
            self.end_point[0] + o_v[0], self.end_point[1] + o_v[1],
        ]

        self.x = min(self.quad_points[::2]) - self.thickness
        self.y = min(self.quad_points[1::2]) - self.thickness
        self.width = max(self.quad_points[::2]) - min(self.quad_points[::2]) + 2 * self.thickness
        self.height = max(self.quad_points[1::2]) - min(self.quad_points[1::2]) + 2 * self.thickness
