import actr

activation_values = [1.4,1.6,1.8]


def retrieve_activation(str):
    level = int(str // 0.05)
    if level >= 2:
        level = 2

    return activation_values[level]


class Landmark:
    """
    Represents a landmark


    """

    def __init__(self, landmark_def):
        """
        Initializes the landmark
        :param landmark_def: List of information for the landmark, [piece_type, grid, rotation/rotation, frequency count]

        Sets the values and creates the actr chunk if not already present.
        Updates baseline activation depending on current strength (frequency count)
        """
        self.piece_type = landmark_def[0]
        self.grid = landmark_def[1]
        self.rotation = landmark_def[2]
        self.str = landmark_def[3]  # to move into weak/medium/strong
        self.name = f'{self.piece_type}-{self.grid}-{self.rotation}'

        self.chunk_def = [self.name, "isa", "landmark", "piece-type", self.piece_type, "grid", self.grid, "rotation",
                          self.rotation]
        if not actr.chunk_p(self.name):
            actr.add_dm(self.chunk_def)
        actr.set_base_levels([self.name,retrieve_activation(self.str)])

    def is_involved(self, piece, grid, rotation):
        """
        Check if the given parameters correspond to the ones of the landmark
        :param piece: piece type
        :param grid: grid value
        :param rotation: rotation value
        :return: True if matches, False otherwise
        """

        if self.piece_type == piece and self.grid == grid and self.rotation == rotation:
            return True

        return False

    def get_frequency(self, df):
        """
        Returns the frequency count of the landmark in the given dataframe
        :param df: the dataframe considered
        :return: frequency count
        """
        pt = self.piece_type if "PARALL" not in self.piece_type else "PARALL"
        row = df.loc[(df['item'] == pt) & (df['grid_val'] == self.grid) & \
                      (df['rot'] == self.rotation)]
        return row['strength'].values[0] if not row.empty else 0

