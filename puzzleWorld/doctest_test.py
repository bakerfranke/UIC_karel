"""
score_game.py — Example of doctests with global state and printed output.
"""

# Global variable
score = 0


def increase_score(points):
    """
    Increases the global score by the given number of points.

    >>> score
    0
    >>> increase_score(5)
    >>> score
    5
    """
    global score
    score += points


def display_score():
    """
    Prints the current score.

    >>> display_score()
    Current score: 0
    """
    print(f"Current score: {score}")


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)