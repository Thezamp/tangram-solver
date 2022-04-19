import actr
from landmark import Landmark
import random

def puzzle_state_to_imaginal(ldm_list):
    state_def = ['isa', 'PUZZLE-STATE', 'pieces-available', 't']
    for ldm in ldm_list:
        state_def.append(ldm.name)
        state_def.append(ldm.name)
    imaginal_chunk = actr.define_chunks(state_def)
    actr.set_buffer_chunk('imaginal', imaginal_chunk)


class Puzzle():

    def __init__(self, path="ACT-R:tangram-solver;models;simple-model.lisp"):
        self.actr_setup(path)
        self.noticed_landmarks = set()
        self.placed_landmarks = []
        self.available_pieces = ["SMALL-T", 'SMALL-T', 'BIG-T', 'BIG-T', 'MEDIUM-T', 'PARALL', 'SQUARE']
        self.unfeasible_causes = []
        self.step_seq = []
        self.unfeasible_ldm = Landmark('UNF-REGION', 'UNF-REGION', 'BACKTRACK', 'UNF-REGION', False)

    def actr_setup(self, path):
        actr.reset()
        actr.load_act_r_model(path)

        actr.add_command("update", self.update)
        actr.add_command("piece-backtrack", self.piece_backtrack)
        actr.add_command("region-backtrack", self.region_backtrack)
        actr.add_command("get-pieces", self.get_pieces)

        actr.add_dm(['start', 'isa', 'process-goal', 'state', 'choose-landmark'])

    def update(self, piece, location):
        print(f'action taken: {piece} at {location}')

        #works only if landmarks are unique
        used_ldm = [l for l in self.noticed_landmarks if l.is_involved(piece,location)][0]

        #update the landmark_state
        self.noticed_landmarks.remove(used_ldm)  # maybe not needed
        self.noticed_landmarks.update(set(used_ldm.get_triggers()))

        self.noticed_landmarks.difference_update(used_ldm.get_removes())

        #track what causes the unfeasible regions
        if self.unfeasible_ldm in used_ldm.get_triggers():
            self.unfeasible_causes.append(used_ldm)

        #track the step sequence
        self.step_seq.append(used_ldm)
        #keep track of the landmarks
        self.placed_landmarks.append(used_ldm)
        #decrase the list of available pieces
        if used_ldm.piece_type != 'COMPOUND':
            self.available_pieces.remove(used_ldm.piece_type)

        #update imaginal buffer
        if len(self.available_pieces) == 0:
            print("stop")
            imaginal_chunk = actr.define_chunks(['isa', 'puzzle-state', 'pieces-available', 'nil'])
            actr.set_buffer_chunk('imaginal', imaginal_chunk)
        else:

            puzzle_state_to_imaginal(list(self.noticed_landmarks))

        return True

    def piece_backtrack(self):
        weakest=sorted(self.placed_landmarks, key= lambda k: k.get_saliency())[0]
        self.noticed_landmarks.add(weakest)
        self.noticed_landmarks.update(weakest.get_removes())
        self.placed_landmarks.remove(weakest)
        puzzle_state_to_imaginal(self.noticed_landmarks)
        self.available_pieces.append(weakest.piece_type)
        return True

    def region_backtrack(self):

        #ldm = self.unfeasible_causes.pop(-1)
        ldm = self.unfeasible_causes.pop(random.randrange(len(self.unfeasible_causes)))
        self.placed_landmarks.remove(ldm)
        self.noticed_landmarks.add(ldm)
        self.noticed_landmarks.update(ldm.get_removes())
        if len(self.unfeasible_causes) == 0:
            self.noticed_landmarks.remove(self.unfeasible_ldm)

        puzzle_state_to_imaginal(self.noticed_landmarks)
        # ADD THE PIECE BACK
        self.available_pieces.append(ldm.piece_type)
        print('Unfeasible region: backtrack')
        return True

    def get_pieces(self):
        state_def= ['isa', 'piece-state']

        for p in set(self.available_pieces):
            state_def.append(p)
            state_def.append('t')
        imaginal_chunk = actr.define_chunks(state_def)
        actr.set_buffer_chunk('imaginal', imaginal_chunk)
        return True

    def run(self, time=10):

        actr.goal_focus('start')
        actr.run(time)
