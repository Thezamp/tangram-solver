import actr

saliency_dict = {'STRONG':3,'WEAK':1,'COMPOUND':2,'DERIVED':2}

class Landmark:
    """

    """
    def __init__(self, landmark_def):
        self.piece_type = landmark_def[0]
        self.grid = landmark_def[1]
        self.orientation = landmark_def[2]
        self.type = landmark_def[3] #to move into weak/medium/strong
        self.name = f'{self.piece_type}-{self.grid}-{self.orientation}'

        self.chunk_def = [self.name, "isa", "landmark", "piece-type", self.piece_type, "grid", self.grid, "orientation", self.orientation]
        if not actr.chunk_p(self.name):
            actr.add_dm(self.chunk_def)
        #actr.set_base_levels([self.name, saliency_dict.get(self.type)])

    def is_involved(self, piece, grid, orientation):

        if self.piece_type == piece and self.grid==grid and self.orientation == orientation:

            return True

        return False

    def get_saliency(self):

        return saliency_dict.get(self.type)
