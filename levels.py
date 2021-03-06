"""module that holds all the levels"""

from kivy.clock import Clock
from kivy.vector import Vector

from widgets import AimLine, BlackHole, GoalPoint, Shot, Stars, Wall


class First(object):
    name = "first fling"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        num_points = 10
        mid_height = fling_board.height / 2.
        start_x = fling_board.width * .3
        end_x = fling_board.width * .7
        step_x = (end_x - start_x) / num_points
        for i in range(num_points):
            i_x = start_x + i * step_x
            goal_point = GoalPoint(pos=(i_x, mid_height))
            fling_board.add_goal_point(goal_point)


class LongShot(object):
    name = "long shot"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        top_height = fling_board.height * .8
        bottom_height = fling_board.height * .2
        left_x = fling_board.width * .4
        right_x = fling_board.width * .6
        first_goal_point = GoalPoint(pos=(left_x, top_height))
        second_goal_point = GoalPoint(pos=(right_x, bottom_height))
        for goal_point in (first_goal_point, second_goal_point):
            fling_board.add_goal_point(goal_point)


class TwoTimed(object):
    name = "two, timed"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        top_height = fling_board.height * .7
        bottom_height = fling_board.height * .3
        left_x = fling_board.width * .4
        right_x = fling_board.width * .6
        seconds_til_switch = (top_height - bottom_height) / 60.

        for start_x in (left_x, right_x):
            goal_point = GoalPoint(pos=(start_x, top_height),
                                   velocity_y=-1)
            Clock.schedule_interval(self.change_direction(goal_point),
                                    seconds_til_switch)
            fling_board.add_goal_point(goal_point)

    @classmethod
    def change_direction(self, goal_point):
        def change_func(dt):
            goal_point.velocity_y *= -1

        return change_func


class TwoTimedTwo(object):
    name = "two, timed: part II"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        top_height = fling_board.height * .7
        bottom_height = fling_board.height * .3
        left_x = fling_board.width * .4
        right_x = fling_board.width * .6
        seconds_til_switch = (top_height - bottom_height) / 60.

        start_pos_vels = [
            (left_x, top_height, -1),
            (right_x, bottom_height, 1)]

        for start_x, start_y, start_velocity_y in start_pos_vels:
            goal_point = GoalPoint(pos=(start_x, start_y),
                                   velocity_y=start_velocity_y)
            Clock.schedule_interval(self.change_direction(goal_point),
                                    seconds_til_switch)
            fling_board.add_goal_point(goal_point)

    @classmethod
    def change_direction(self, goal_point):
        def change_func(dt):
            goal_point.velocity_y *= -1

        return change_func


class OrbitIt(object):
    name = "orbit it"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        num_points = 24
        r = 250
        center_x = fling_board.width / 2.
        center_y = fling_board.height / 2.

        black_hole = BlackHole(pos=(center_x, center_y))
        fling_board.add_black_hole(black_hole)

        v = Vector(r, 0)
        rotation_angle = 360. / num_points
        for i in range(num_points):
            goal_point = GoalPoint(pos=(center_x + v.x, center_y + v.y))
            fling_board.add_goal_point(goal_point)
            v = v.rotate(rotation_angle)


class GoFigure(object):
    name = "go figure"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        num_points = 24
        r = 250
        center_x = fling_board.width / 2.
        center_y = fling_board.height / 2.
        left_x = fling_board.width * .3
        right_x = fling_board.width * .7
        m = center_x - left_x

        left_hole = BlackHole(pos=(left_x, center_y))
        fling_board.add_black_hole(left_hole)

        right_hole = BlackHole(pos=(right_x, center_y))
        fling_board.add_black_hole(right_hole)

        point_positions = [
            (left_x - m, center_y),
            (center_x, center_y),
            (right_x + m, center_y),
        ]

        for pos in point_positions:
            goal_point = GoalPoint(pos=pos)
            fling_board.add_goal_point(goal_point)


class Wally(object):
    name = "wally"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        wall_x = fling_board.width * .7 + 10
        wall_top_y = fling_board.height * .6
        wall_bottom_y = fling_board.height * .4

        wall = Wall(start_point=[wall_x, wall_top_y],
                    end_point=[wall_x, wall_bottom_y])
        fling_board.add_wall(wall)

        goals_start_x = fling_board.width * .45
        goals_offset_x = fling_board.width * .05
        goals_center_y = fling_board.height * .5
        goals_offset_y = fling_board.height * .05

        num_rows = 5
        for i in xrange(num_rows):
            fling_board.add_goal_point(
                GoalPoint(x=goals_start_x + i * goals_offset_x,
                          y=goals_center_y + (num_rows - i) * goals_offset_y))
            fling_board.add_goal_point(
                GoalPoint(x=goals_start_x + i * goals_offset_x,
                          y=goals_center_y - (num_rows - i) * goals_offset_y))


class HopSkip(object):
    name = "hopskip"
    max_shots = 1

    @classmethod
    def load(self, fling_board):
        wall_width = 100

        for hop_scale in [.2, .5, .8]:
            hop_x = fling_board.width * hop_scale
            fling_board.add_black_hole(BlackHole(
                pos=(hop_x, 200)))

            fling_board.add_wall(Wall(
                start_point=(hop_x - 50, 275),
                end_point=(hop_x + 50, 275)))

            fling_board.add_goal_point(GoalPoint(
                pos=(hop_x, 325)))


class Kinetic(object):
    name = "kinetic"
    max_shots = 2

    @classmethod
    def load(self, fling_board):
        center_y = fling_board.height * .5
        for scale in [.2, .3, .4, .5, .6]:
            x = fling_board.width * scale
            fling_board.add_goal_point(GoalPoint(
                pos=(x, center_y)))

        for offset in [50, 100]:
            fling_board.add_goal_point(GoalPoint(
                pos=(x + offset, center_y + offset)))
            fling_board.add_goal_point(GoalPoint(
                pos=(x, center_y - offset)))

levels = [
    First,
    LongShot,
    TwoTimed,
    TwoTimedTwo,
    OrbitIt,
    GoFigure,
    Wally,
    HopSkip,
    Kinetic,
]
