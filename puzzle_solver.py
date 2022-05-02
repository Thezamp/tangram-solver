import os

import pandas as pd

import actr
from landmark import Landmark
from landmark_detector.landmark_extraction import LandmarkExtractor
from application.application_screen import ApplicationScreen

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

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



class Piece():
    def __init__(self,name,type):
        self.name = name
        self.type = type
        self.used = False
        self.grid = -1
        self.orientation =0


    def place(self,grid, orientation):
        self.grid = grid
        self.orientation = orientation
        self.used = True

    def remove(self):
        self.grid = -1
        self.used = False



class Puzzle():
###NEED TO FIX PIECES AND LANDMARKS
    def __init__(self, tgn, appscreen, path="ACT-R:tangram-solver;models;solver-model.lisp"):
        self.actr_setup(path)
        self.current_placements = []  # what landmarks are actually used
        self.step_sequence = []  # all the landmarks
        self.problem_placements = []  # the landmarks that generated unfeasible regions
        self.available_pieces = ["SMALL-T", 'SMALL-T', 'BIG-T', 'BIG-T', 'MIDDLE-T', 'PARALL', 'SQUARE']
        # self.available_pieces = [Piece("SMALL-T-1",'SMALL-T'),Piece("SMALL-T-2",'SMALL-T'),Piece("MIDDLE-T",'MIDDLE-T'), \
        #                          Piece("BIG-T-1",'BIG-T'),Piece("BIG-T-1",'BIG-T'), Piece("SQUARE",'SQUARE'), Piece("PARALL",'PARALL')]

        self.current_imaginal = []  # python equivalent of the imaginal buffer, maybe use dict?
        self.extractor = LandmarkExtractor(tgn)
        self.step = 0
        self.appscreen = appscreen
        data = pd.read_csv(f'{ROOT_DIR}/../datasets/steps.csv')
        self.players_data = data.loc[data['tangram nr'] == tgn]

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
        path = self.make_move(used.piece, used.grid, used.orientation)
        self.step += 1
        extracted= self.extractor.extract(path, self.available_pieces, self.step)

        if extracted[1]:
            self.problem_placements.append(used)

        self.current_imaginal = puzzle_state_to_imaginal(extracted)

        return True

    def make_move(self, piece, grid, orientation):
        x,y = self.players_data.loc[(self.players_data.item == piece) & \
                                          (self.players_data.grid == grid) & \
                                          (self.players_data.rot == orientation)][['x','y']].iloc[0]




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
