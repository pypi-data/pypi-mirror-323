def add_wall(grid, start, end, wall=-1, orient='horiz'):
    """
    Adds a wall to a 2D grid by modifying its elements.
    
    Args :
    ------
    grid : list[list[int]]
        The grid to modify.
    start : tuple[int, int]
        Starting coordinate as (row, col).
    end : tuple[int, int]
        Ending coordinate as (row, col).
    wall : int, optional
        The value to assign to the wall in the grid.
        Defaults to -1.
    orient : str, optional
        Wall orientation. Accepts 'horiz' or 'vert'.
        Defaults to 'horiz'.
    
    Returns:
    --------
    None : None
        This function modifies the grid in-place and
        does not return any value.
    """
    if orient == "horiz":
        for col in range(start[1], end[1] + 1):
            grid[start[0]][col] = wall
    elif orient == "vert":
        for row in range(start[0], end[0] + 1):
            grid[row][start[1]] = wall


def add_surrounding_walls(grid, wall=-1):
    """
    Add walls around the edges of the grid.
    
    Args :
    ------
    grid : list[list[int]]
        The grid to modify.
    wall : int, optional
        The value to assign to the wall in the grid.
        Defaults to -1.
    
    Returns:
    --------
    None : None
        This function modifies the grid in-place and
        does not return any value.
    """
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        grid[r][0] = wall
        grid[r][cols - 1] = wall
    for c in range(cols):
        grid[0][c] = wall
        grid[rows - 1][c] = wall
