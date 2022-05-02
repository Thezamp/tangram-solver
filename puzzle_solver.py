import os

import actr
from landmark import Landmark
from landmark_detector.landmark_extraction import LandmarkExtractor
from application.application_screen import ApplicationScreen


def puzzle_state_to_imaginal(extracted):
    """
    sets the actr imaginal buffer

    the imaginal buffer is so defined:
    (chunk-type PUZZLE-STATE
        PIECES-AVAILABLE
        LANDMARK-1
        LANDMARK-2
        LANDMARK-3
        LANDMARK-4
        LANDMARK-5
        LANDMARK-6
        SPECIAL-LANDMARK
    )

    """
    ldm_list=  extracted[0]
    problem = extracted[1]
    state_def = ['isa', 'PUZZLE-STATE', 'PIECES-AVAILABLE', 'T']
    current_imaginal = []
    for i in range(len(ldm_list[0:6])):
        l = Landmark(ldm_list[i])
        state_def.append(f'LANDMARK-{i + 1}')
        state_def.append(l.name)
        current_imaginal.append(l)
    if problem:
        state_def.append('SPECIAL-LANDMARK')
        state_def.append('UNF-REG')

    imaginal_chunk = actr.define_chunks(state_def)
    actr.set_buffer_chunk('imaginal', imaginal_chunk)
    return current_imaginal


def make_move(piece, grid, orientation):
    return ''


class Puzzle():

    def __init__(self, tgn, appscreen, path="ACT-R:tangram-solver;models;solver-model.lisp"):
        self.actr_setup(path)
        self.current_placements = []  # what landmarks are actually used
        self.step_sequence = []  # all the landmarks
        self.problem_placements = []  # the landmarks that generated unfeasible regions
        self.available_pieces = ["SMALL-T", 'SMALL-T', 'BIG-T', 'BIG-T', 'MIDDLE-T', 'PARALL', 'SQUARE']
        self.current_imaginal = []  # python equivalent of the imaginal buffer, maybe use dict?
        # self.unfeasible_ldm = Landmark(['UNC:\Users\ASUS\Desktop\Hamburg\ACT-R\tangram-solver\models\solver-model.lispF-REGION', 'UNF-REGION', 'BACKTRACK', 'STRONG']) #TO be defined
        self.extractor = LandmarkExtractor(tgn)
        self.step = 0
        self.appscreen = appscreen

    def actr_setup(self, path):
        actr.reset()
        actr.load_act_r_model(path)

        actr.add_command("update", self.update)
        actr.add_command("piece-backtrack", self.piece_backtrack)
        actr.add_command("region-backtrack", self.region_backtrack)
        actr.add_command("get-pieces", self.get_pieces)

        actr.add_dm(['start', 'isa', 'goal', 'state', 'choose-landmark'])

    def update(self, piece, grid, orientation):
        print(f'action taken: {piece}-{orientation} at grid pos {grid}')

        # update the state
        used = [x for x in self.current_imaginal if x.is_involved(piece, grid, orientation)][0]
        self.step_sequence.append(used)
        self.current_placements.append(used)
        self.available_pieces.remove(used.piece)

        # generate the new picture
        path = make_move(used.piece, used.grid, used.orientation)
        self.step += 1
        new_landmarks, problem = self.extractor.extract(path, self.available_pieces, self.step)

        if problem:
            self.problem_placements.append(used)

        self.current_imaginal = puzzle_state_to_imaginal(new_landmarks, problem)

        return True

    def piece_backtrack(self):
        return True

    def region_backtrack(self):
        return True

    def get_pieces(self):
        state_def = ['isa', 'piece-state']

        for p in set(self.available_pieces):
            state_def.append(p)
            state_def.append('t')
        imaginal_chunk = actr.define_chunks(state_def)
        actr.set_buffer_chunk('imaginal', imaginal_chunk)
        return True

    def run(self, time=20):
        path = './landmark_detector/example_pictures/1.png'
        self.current_imaginal = puzzle_state_to_imaginal(self.extractor.extract(path, self.available_pieces, self.step))
        actr.goal_focus('start')
        actr.run(time)


def main():
    appscreen = ApplicationScreen()
    p = Puzzle(4,appscreen)
    p.appscreen.dump_gui()
    p.run(20)


if __name__ == '__main__':
    main()
