"""module that holds all the levels"""

from kivy.clock import Clock

from widgets import AimLine, BlackHole, GoalPoint, Rocket, Shot, Stars


class First(object):
    name = "first fling"

    def load(self, fling_board):
        num_points = 10
        mid_height = fling_board.height / 2.
        start_x = fling_board.width * .3
        end_x = fling_board.width * .7
        step_x = (end_x - start_x) / num_points
        for i in range(num_points):
            i_x = start_x + i * step_x
            goal_point = GoalPoint(pos=(i_x, mid_height))
            fling_board.add_widget(goal_point)
            fling_board.goal_points.append(goal_point)


class LongShot(object):
    name = "long shot"

    def load(self, fling_board):
        top_height = fling_board.height * .8
        bottom_height = fling_board.height * .2
        left_x = fling_board.width * .4
        right_x = fling_board.width * .6
        first_goal_point = GoalPoint(pos=(left_x, top_height))
        second_goal_point = GoalPoint(pos=(right_x, bottom_height))
        for goal_point in (first_goal_point, second_goal_point):
            fling_board.add_widget(goal_point)
            fling_board.goal_points.append(goal_point)


class TwoTimed(object):
    name = "two, timed"

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
            fling_board.add_widget(goal_point)
            fling_board.goal_points.append(goal_point)


    def change_direction(self, goal_point):
        def change_func(dt):
            goal_point.velocity_y *= -1

        return change_func


class TwoTimedTwo(object):
    name = "two, timed: part II"

    def load(self, fling_board):
        top_height = fling_board.height * .7
        bottom_height = fling_board.height * .3
        left_x = fling_board.width * .4
        right_x = fling_board.width * .6
        seconds_til_switch = (top_height - bottom_height) / 60.

        for start_x, start_y, start_velocity_y in ((left_x, top_height, -1),
                                                   (right_x, bottom_height, 1)):
            goal_point = GoalPoint(pos=(start_x, start_y),
                                   velocity_y=start_velocity_y)
            Clock.schedule_interval(self.change_direction(goal_point),
                                    seconds_til_switch)
            fling_board.add_widget(goal_point)
            fling_board.goal_points.append(goal_point)


    def change_direction(self, goal_point):
        def change_func(dt):
            goal_point.velocity_y *= -1

        return change_func



levels = [First, LongShot, TwoTimed, TwoTimedTwo]
