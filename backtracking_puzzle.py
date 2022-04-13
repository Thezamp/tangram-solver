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
        self.active_landmarks = set()
        self.available_pieces = ["SMALL-T", 'SMALL-T', 'BIG-T', 'BIG-T', 'MEDIUM-T', 'PARALL', 'SQUARE']
        self.unfeasible_causes = []
        self.step_seq = []
        self.error_ldm = Landmark('LDM-ERROR', 'LANDMARK-ERROR', 'LANDMARK-ERROR', 'LANDMARK-ERROR', False)

    def actr_setup(self, path):
        actr.reset()
        actr.load_act_r_model(path)

        actr.add_command("update", self.update)
        actr.add_command("piece-backtrack", self.piece_backtrack)
        actr.add_command("region-backtrack", self.region_backtrack)

        actr.add_dm(['start', 'isa', 'goal', 'state', 'choose-landmark'])

    def update(self, piece, location):
        print(f'action taken: {piece} at {location}')

        #works only if landmarks are unique
        used_ldm = next(l for l in self.active_landmarks if l.is_involved(piece,location))
        #update the landmark_state
        self.active_landmarks.remove(used_ldm)  # maybe not needed
        self.active_landmarks.update(used_ldm.get_triggers())
        self.active_landmarks = [ldm for ldm in self.active_landmarks if ldm not in used_ldm.get_removes()]

        #track what causes the unfeasible regions
        if self.error_ldm in used_ldm.get_triggers:
            self.unfeasible_causes.append(used_ldm)

        #track the step sequence
        self.step_seq.append(used_ldm)

        #decrase the list of available pieces
        self.available_pieces.remove(used_ldm.piece_type)

        #update imaginal buffer
        if len(self.available_pieces) == 0:
            print("stop")
            imaginal_chunk = actr.define_chunks(['isa', 'puzzle-state', 'pieces-available', 'nil'])
            actr.set_buffer_chunk('imaginal', imaginal_chunk)
        else:
            puzzle_state_to_imaginal(self.active_landmarks)

        return True

    def piece_backtrack(self):
        pass

    def region_backtrack(self):

        #ldm = self.unfeasible_causes.pop(-1)
        ldm = self.unfeasible_causes.pop(random.randrange(len(self.unfeasible_causes)))
        self.active_landmarks.add(ldm)
        self.active_landmarks.update(ldm.get_removes())
        if len(self.unfeasible_causes) == 0:
            self.active_landmarks.remove(self.error_ldm)

        puzzle_state_to_imaginal(self.active_landmarks)

    def run(self, time=10):
        actr.goal_focus('start')
        actr.run(time)
