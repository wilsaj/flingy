#!/usr/bin/env python
import itertools
import math

import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from widgets import AimLine, BlackHole, GoalPoint, Rocket, Shot, Stars
import levels

kivy.require('1.0.9')


class FlingBoard(Widget):
    """
    Main application widget, takes all the touches and turns them into
    fun.
    """
    def __init__(self, *args, **kwargs):
        super(FlingBoard, self).__init__()
        self.clear_level()
        Window.clearcolor = (0.1, 0.1, 0.1, 1.)
        Clock.schedule_once(self.add_stars, -1)
        Clock.schedule_interval(self.tick, 1 / 60.)
        self._keyboard = Window.request_keyboard(
            None, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        try:
            level_index = int(text)
            print "loading level %s..." % (level_index)
            self.load_level(level_index)
            return True
        except ValueError:
            pass

    def add_stars(self, dt):
        self.stars = Stars(2000)
        self.add_widget(self.stars)

    def clear_level(self):
        self.aim_line = None
        self.black_holes = []
        self.shots = []
        self.rockets = []
        self.goal_points = []

    def load_level(self, level_index):
        level = levels.levels[level_index]()
        level.load(self)

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
