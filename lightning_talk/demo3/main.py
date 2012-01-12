#!/usr/bin/env python
"""now with black holes"""
from functools import partial
import itertools
import math
from random import random

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import ListProperty, NumericProperty
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button


kivy.require('1.0.9')


class AimLine(Widget):
    start_pt = ListProperty([0, 0])
    end_pt = ListProperty([0, 0])

    def __init__(self, start_pt, **kwargs):
        super(AimLine, self).__init__(**kwargs)
        self.start_pt = start_pt
        self.end_pt = start_pt


#---- NEW ---------------------------------------------
class BlackHole(Widget):
    d = NumericProperty(50.)
    mass = NumericProperty(50.)

    def __init__(self, **kwargs):
        super(BlackHole, self).__init__(**kwargs)

    def collide_point(self, x, y):
        if (Vector(x, y) - Vector(self.pos)).length() < self.d:
            return True
#---- /NEW ---------------------------------------------


class Shot(Widget):
    d = NumericProperty(10.)
    motion_v = ListProperty([0, 0])

    def __init__(self, motion_v, **kwargs):
        super(Shot, self).__init__(**kwargs)
        self.motion_v = motion_v

    def move(self):
        self.x += self.motion_v[0]
        self.y += self.motion_v[1]

#---- NEW ---------------------------------------------
    def gravitate_towards(self, body):
        m_v = Vector(self.motion_v)
        g_v = Vector(body.pos) - Vector(self.pos)
        self.motion_v = m_v + (g_v * 1. / g_v.length2()) * body.mass
#---- /NEW ---------------------------------------------


class FlingBoard(Widget):
    """
    Main application widget, takes all the touches.
    """
    def __init__(self, *args, **kwargs):
        super(FlingBoard, self).__init__()
        self.aim_line = None
#---- NEW ---------------------------------------------
        self.black_holes = []
        # space is too dark for black holes - set bg color
        Window.clearcolor = (0.2, 0.2, 0.2, 1.)
#---- /NEW ---------------------------------------------
        self.shots = []
        Clock.schedule_interval(self.tick, 1 / 60.)

    def on_touch_down(self, touch):
#---- NEW ---------------------------------------------
        if touch.is_double_tap:
            # if double clicking an existing black hole, remove it
            for black_hole in self.black_holes:
                if black_hole.collide_point(*touch.pos):
                    self.remove_widget(black_hole)
                    self.black_holes.remove(black_hole)
                    return True
            # otherwise add a new black hole
            black_hole = BlackHole(pos=touch.pos)
            self.add_widget(black_hole)
            self.black_holes.append(black_hole)
#---- /NEW ---------------------------------------------
        self.aim_line = AimLine(touch.pos)
        self.add_widget(self.aim_line)
        return True

    def on_touch_move(self, touch):
        try:
            self.aim_line.end_pt = touch.pos
            return True
        except (KeyError), e:
            pass

    def on_touch_up(self, touch):
        start_v = Vector(self.aim_line.start_pt)
        end_v = Vector(self.aim_line.end_pt)

        motion_v = start_v - end_v
        l = motion_v.length()
        if l == 0.:
            return
        motion_v /= math.sqrt(l)

        shot = Shot(motion_v=motion_v, pos=(touch.x, touch.y))
        self.add_widget(shot)
        self.remove_widget(self.aim_line)
        self.shots.append(shot)

    def tick(self, dt):
        for shot1, shot2 in itertools.combinations(self.shots, 2):
            if bodies_collide(shot1, shot2):
                shots_bounce(shot1, shot2)

        for shot in self.shots:
#---- NEW ---------------------------------------------
            for black_hole in self.black_holes:
                shot.gravitate_towards(black_hole)
                if bodies_collide(shot, black_hole):
                    self.remove_widget(shot)
                    self.shots.remove(shot)
#---- /NEW ---------------------------------------------
            shot.move()


class FlingyApp(App):
    def build(self):
        return FlingBoard()


def bodies_collide(body1, body2):
    widget_distance = Vector(body1.pos).distance(Vector(body2.pos))
    radial_distance = (body1.d + body2.d) / 2.
    return widget_distance < radial_distance


def shots_bounce(shot1, shot2):
    p1_v = Vector(shot1.pos)
    p2_v = Vector(shot2.pos)
    shot1.motion_v = (p1_v - p2_v).normalize() / Vector(shot1.motion_v).length()
    shot2.motion_v = (p2_v - p1_v).normalize() / Vector(shot2.motion_v).length()


if __name__ == '__main__':
    FlingyApp().run()
