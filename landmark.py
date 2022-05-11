import actr

saliency_dict = {'STRONG': 3, 'WEAK': 1, 'COMPOUND': 2, 'DERIVED': 2}


class Landmark:
    """
    Represents a landmark


    """

    def __init__(self, landmark_def):
        """
        Initializes the landmark
        :param landmark_def: List of information for the landmark, [piece_type, grid, orientation/rotation, frequency count]

        Sets the values and creates the actr chunk if not already present.
        Updates baseline activation depending on current strength (frequency count)
        """
        self.piece_type = landmark_def[0]
        self.grid = landmark_def[1]
        self.orientation = landmark_def[2]
        self.type = landmark_def[3]  # to move into weak/medium/strong
        self.name = f'{self.piece_type}-{self.grid}-{self.orientation}'

        self.chunk_def = [self.name, "isa", "landmark", "piece-type", self.piece_type, "grid", self.grid, "orientation",
                          self.orientation]
        if not actr.chunk_p(self.name):
            actr.add_dm(self.chunk_def)
        # actr.set_base_levels([self.name, saliency_dict.get(self.type)])

    def is_involved(self, piece, grid, orientation):
        """
        Check if the given parameters correspond to the ones of the landmark
        :param piece: piece type
        :param grid: grid value
        :param orientation: rotation value
        :return: True if matches, False otherwise
        """

        if self.piece_type == piece and self.grid == grid and self.orientation == orientation:
            return True

        return False

    def get_frequency(self, df):
        """
        Returns the frequency count of the landmark in the given dataframe
        :param df: the dataframe considered
        :return: frequency count
        """
        row = df.loc[(df['item'] == self.piece_type) & (df['grid_val'] == self.grid) & \
                      (df['rot'] == self.orientation)]
        return row['counts'].values[0] if not row.empty else 0

