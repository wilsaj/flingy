#!/usr/bin/env python
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
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
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


class BlackHole(Widget):
    d = NumericProperty(50.)
    mass = NumericProperty(50.)

    def __init__(self, **kwargs):
        super(BlackHole, self).__init__(**kwargs)

    def collide_point(self, x, y):
        if (Vector(x, y) - Vector(self.pos)).length() < self.d / 2.:
            return True


class GoalPoint(Widget):
    r = NumericProperty(10.)

    def __init__(self, **kwargs):
        super(GoalPoint, self).__init__(**kwargs)

    def collide_point(self, x, y):
        if (Vector(x, y) - Vector(self.pos)).length() < self.r:
            return True


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
    d = NumericProperty(10.)
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


class FlingBoard(Widget):
    """
    Main application widget, takes all the touches.
    """
    def __init__(self, *args, **kwargs):
        super(FlingBoard, self).__init__()
        self.aim_line = None
        self.black_holes = []
        self.shots = []
        self.rockets = []
        self.goal_points = []
        Window.clearcolor = (0.1, 0.1, 0.1, 1.)
        Clock.schedule_once(self.add_stars, -1)
        Clock.schedule_interval(self.tick, 1 / 60.)

    def add_stars(self, dt):
        self.stars = Stars(2000)
        self.add_widget(self.stars)

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            # for black_hole in self.black_holes:
            #     if black_hole.collide_point(*touch.pos):
            #         self.remove_widget(black_hole)
            #         self.black_holes.remove(black_hole)
            #         return True
            # black_hole = BlackHole(pos=touch.pos)
            # self.add_widget(black_hole)
            # self.black_holes.append(black_hole)
            for goal_point in self.goal_points:
                if goal_point.collide_point(*touch.pos):
                    self.remove_widget(goal_point)
                    self.goal_points.remove(goal_point)
                    return True
            goal_point = GoalPoint(pos=touch.pos)
            self.add_widget(goal_point)
            self.goal_points.append(goal_point)
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
        self.shots.append(shot)

        # rocket = Rocket(motion_v=motion_v, pos=(touch.x, touch.y))
        # self.add_widget(rocket)
        # self.rockets.append(rocket)

        self.remove_widget(self.aim_line)

    def tick(self, dt):
        for shot1, shot2 in itertools.combinations(self.shots, 2):
            if circles_collide(shot1, shot2):
                shots_collide(shot1, shot2)

        for shot in self.shots:
            for black_hole in self.black_holes:
                shot.gravitate_towards(black_hole)
                if circles_collide(shot, black_hole):
                    self.remove_widget(shot)
                    self.shots.remove(shot)
            shot.move()

        for goal_point in self.goal_points:
            for shot in self.shots:
                if goal_point.collide_point(*shot.pos):
                    self.remove_widget(goal_point)
                    self.goal_points.remove(goal_point)

                    if len(self.goal_points) == 0:
                        print "DONE"
                    continue

        for rocket in self.rockets:
            for black_hole in self.black_holes:
                rocket.gravitate_towards(black_hole)
                if black_hole.collide_point(*rocket.pos):
                    self.remove_widget(rocket)
                    self.rockets.remove(rocket)
            rocket.move()


class FlingyApp(App):
    def build(self):
        return FlingBoard()


def circles_collide(widget_1, widget_2):
    widget_distance = Vector(widget_1.pos).distance(Vector(widget_2.pos))
    radial_distance = (widget_1.d + widget_2.d) / 2.
    return widget_distance < radial_distance


def shots_collide(shot1, shot2):
    p1_v = Vector(shot1.pos)
    p2_v = Vector(shot2.pos)
    shot1.motion_v = (p1_v - p2_v).normalize() / Vector(shot1.motion_v).length()
    shot2.motion_v = (p2_v - p1_v).normalize() / Vector(shot2.motion_v).length()


if __name__ == '__main__':
    FlingyApp().run()
