"""module that holds all the levels"""

from widgets import AimLine, BlackHole, GoalPoint, Rocket, Shot, Stars


class First(object):
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


levels = [First]
