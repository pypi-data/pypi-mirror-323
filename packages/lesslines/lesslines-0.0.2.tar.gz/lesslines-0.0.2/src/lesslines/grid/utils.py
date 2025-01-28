def create_grid(rows, cols, val=0):
    """
    Create grid with certain value val.
    
    Args:
    -----
    rows : int
        Number of rows.
    cols : int
        Number of columns.
    val : int, optional.
        Value for all cells. Defaults to 0.
    
    Returns:
    --------
    m : list of list of int
        A 2D list containing numerical values.
    """
    m = []
    for r in range(rows):
        a_row = []
        for c in range(cols):
            a_row.append(val)
        m.append(a_row)
    return m


def str_grid(grid, char_map=None, hsep=''):
    """
    Generate string representation of the grid.
    
    Args:
    -----
    grid : list of list of int
        A 2D list containing numerical values.
    
    char_map : dict, optional
        A dictionary mapping numerical values to characters
        Defaults map 0-9 to '0'-'9', 10-35 to 'A'-'Z', others
        to '#'.
    
    hsep : str
        Hofizontal separation string between two characters.
        Defaults to '' (empty string).
    
    Returns:
    --------
    result : str
        A single string representing the grid with rows
        separated by newlines. Each cell is represented by
        a single character according to the `char_map` mapping.
    """
    if char_map is None:
        char_map = {}
    
    def default_mapping(value):
        if 0 <= value <= 9:
            return str(value)
        elif 10 <= value <= 35:
            return chr(ord('A') + value - 10)
        else:
            return '#'

    lines = []
    for row in grid:
        line = []
        for value in row:
            c = char_map.get(value, default_mapping(value))
            line.append(c)
            
        lines.append(hsep.join(line))
    
    result = '\n'.join(lines)
    return result
