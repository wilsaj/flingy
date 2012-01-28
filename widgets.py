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
    r = NumericProperty(10.)
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
    r = NumericProperty(5.)
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
