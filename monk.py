import actr
from landmark import Landmark
from puzzle import Puzzle, list_to_imaginal


def generate_monk_ldm():
    hat = Landmark("ST-HAT", "SMALL-T", "HAT", "SIMPLE")
    face = Landmark("SQ-FACE", "SQUARE", "FACE", 'SIMPLE')
    arm = Landmark("PG-ARM", 'PARALL', 'ARM', 'SIMPLE')
    foot = Landmark("ST-FOOT", 'SMALL-T', 'FOOT', 'SIMPLE')
    body = Landmark("BODY", "NONE", "BODY", 'SIMPLE')  # NEED A DIFFERENT WAY TO SOLVE COMPLEX VS SIMPLE
    #######
    belly = Landmark('BT-BELLY', 'BIG-T', 'BELLY', 'SIMPLE')
    # neck = Landmark('BT-NECK', 'BIG-T', 'NECK', 'SIMPLE')
    knee = Landmark('MT-KNEE', 'MEDIUM-T', 'KNEE', 'SIMPLE')
    upperbody = Landmark('BT-UPPER', 'BIG-T', 'UPPER', 'SIMPLE')
    lowerbody = Landmark('BT-LOWER', 'BIG-T', 'LOWER', 'SIMPLE')
    # bottom = Landmark('MT-LOWER', 'MEDIUM-T', 'LOWER', 'SIMPLE')
    # leg = Landmark('BT-KNEE', 'BIG-T', 'KNEE', 'SIMPLE')
    # error = Landmark('ERROR-NOTICED', 'LANDMARK-ERROR', 'LANDMARK-ERROR', 'LANDMARK-ERROR')
    error = Landmark('LDM-ERROR', 'LANDMARK-ERROR', 'LANDMARK-ERROR', 'LANDMARK-ERROR', False)  # don't put in dm

    # simple "deterministic"version
    body.add_triggers([belly, upperbody, lowerbody, knee])
    belly.add_removes([upperbody, lowerbody])
    belly.add_triggers([error])
    upperbody.add_removes([belly])
    lowerbody.add_removes([belly])
    # body.add_triggers([belly, neck, knee, upperbody, lowebody, bottom, leg])
    # belly.add_removes([neck,upperbody,lowerbody,leg,bottom])
    # belly.add_triggers([error])
    # neck.add_removes([belly,upperbody,lowerbody,bottom])
    # neck.add_triggers([error])
    # knee.add_removes([leg,bottom])

    active = [hat, face, arm, foot, body]
    # active = [hat, face, arm, foot]
    # unseen = [belly, neck, knee, upperbody, lowerbody, bottom, leg,error]
    # currently not using unseen
    unseen = [belly, upperbody, lowerbody, knee, error]

    return active, unseen


class Monk(Puzzle):
    def __init__(self, path= "ACT-R:tangram-solver;simple-model.lisp"):
        super().__init__(path)
        self.active_landmarks, self.unseen_landmarks = generate_monk_ldm()
        list_to_imaginal(self.active_landmarks)
