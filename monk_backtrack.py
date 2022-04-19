from landmark import Landmark
from backtracking_puzzle import Puzzle,puzzle_state_to_imaginal


def generate_monk_ldm(unf_region_ldm):
#                   Name    Piece-type  location    tier
    hat = Landmark("ST-HAT", "SMALL-T", "HAT", "STRONG")
    face = Landmark("SQ-FACE", "SQUARE", "FACE", 'STRONG')
    arm = Landmark("PG-ARM", 'PARALL', 'ARM', 'STRONG')
    foot = Landmark("ST-FOOT", 'SMALL-T', 'FOOT', 'STRONG')
    body = Landmark("BODY", "COMPOUND", "BODY", 'WEAK')  # NEED A DIFFERENT WAY TO SOLVE COMPLEX VS SIMPLE
    #######
    belly = Landmark('BT-BELLY', 'BIG-T', 'BELLY', 'WEAK')
    # neck = Landmark('BT-NECK', 'BIG-T', 'NECK', 'WEAK')
    knee = Landmark('MT-KNEE', 'MEDIUM-T', 'KNEE', 'WEAK')
    upperbody = Landmark('BT-UPPER', 'BIG-T', 'UPPER', 'WEAK')
    lowerbody = Landmark('BT-LOWER', 'BIG-T', 'LOWER', 'WEAK')
    # bottom = Landmark('MT-LOWER', 'MEDIUM-T', 'LOWER', 'WEAK')
    # leg = Landmark('BT-KNEE', 'BIG-T', 'KNEE', 'WEAK')

    # simple "deterministic"version
    body.add_triggers([belly, upperbody, lowerbody, knee])
    belly.add_removes([upperbody, lowerbody])
    belly.add_triggers([unf_region_ldm])
    upperbody.add_removes([belly])
    lowerbody.add_removes([belly])
    # body.add_triggers([belly, neck, knee, upperbody, lowebody, bottom, leg])
    # belly.add_removes([neck,upperbody,lowerbody,leg,bottom])
    # belly.add_triggers([error])
    # neck.add_removes([belly,upperbody,lowerbody,bottom])
    # neck.add_triggers([error])
    # knee.add_removes([leg,bottom])

    active = {hat, face, arm, foot, body}
    # active = [hat, face, arm, foot]
    # unseen = [belly, neck, knee, upperbody, lowerbody, bottom, leg,error]
    # currently not using unseen
    unseen = set([belly, upperbody, lowerbody, knee, unf_region_ldm]) #to be removed

    return active, unseen


class Monk(Puzzle):
    def __init__(self, path= "ACT-R:tangram-solver;models;two-backtrack-model.lisp"):
        super().__init__(path)
        self.noticed_landmarks, self.unseen_landmarks = generate_monk_ldm(self.unfeasible_ldm)
        puzzle_state_to_imaginal(self.noticed_landmarks)


def main():
    m = Monk()
    print('start')
    m.run(10)

if __name__ == "__main__":
    main()