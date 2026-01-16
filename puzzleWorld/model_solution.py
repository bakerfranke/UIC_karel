###############################################################
# CS 111 - Lab: Movie Data Manager (Week 9)
# Name:
# NetID:
# Date:
#
# This file defines helper functions used by main()
# Students will complete the functions below.
###############################################################


def print_movie_list(heading, movie_list):
    """
    Prints a numbered list of movies with a heading.

    Parameters:
        heading (str): a title or heading for the list
        movie_list (list of str): list of movie titles to display

    Returns:
        None — prints output only.

    🪄 Tip: Use a for-loop with range(len(movie_list)) to print
    each movie on its own line with a number starting from 1.
    """
    print(heading)
    for i in range(len(movie_list)):
        print(f"{i + 1}. {movie_list[i]}")


def print_full_movie_info(title):
    """
    Prints full details (title, rating, description, director, actors)
    for a movie whose title contains the given text.

    Parameters:
        title (str): a title or partial title to search for

    Returns:
        None — prints results directly.

    🪄 Tip: Use global variables and a for-loop.
    Check if title.lower() is contained in all_titles[i].lower()
    to allow partial matches.
    """
    global all_titles, all_ratings, all_description, all_directors, all_actors

    found = False
    for i in range(len(all_titles)):
        if title.lower() in all_titles[i].lower():
            print(f"\nTitle: {all_titles[i]}")
            print(f"Rating: {all_ratings[i]}")
            print(f"Director: {all_directors[i]}")
            print(f"Actors: {all_actors[i]}")
            print(f"Description: {all_description[i]}")
            found = True
    if not found:
        print("No matching movie found.")


def movies_above_rating(threshold):
    """
    Builds and returns a list of movie titles with a rating above threshold.

    Parameters:
        threshold (float): minimum rating (0–10 scale)

    Returns:
        list of str — titles with ratings above threshold.

    🪄 Tip: Start with an empty list, check each rating, and
    append titles that qualify.
    """
    global all_titles, all_ratings

    result = []
    for i in range(len(all_ratings)):
        if all_ratings[i] > threshold:
            result.append(all_titles[i])
    return result


def highest_rated_movie():
    """
    Finds and returns the title of the highest-rated movie.

    Returns:
        str — the title of the movie with the highest rating.

    🪄 Tip: Track the “best so far” rating and its index
    as you loop through the list.
    """
    global all_titles, all_ratings

    best_index = 0
    best_rating = all_ratings[0]
    for i in range(1, len(all_ratings)):
        if all_ratings[i] > best_rating:
            best_rating = all_ratings[i]
            best_index = i
    return all_titles[best_index]


def movies_by_director(name):
    """
    Returns a list of all movies directed by the given name
    (or partial match on name).

    Parameters:
        name (str): director name or partial text to search for

    Returns:
        list of str — titles of all movies directed by that person.

    🪄 Tip: Start with an empty list, loop through all_directors,
    and check if name.lower() is in all_directors[i].lower().
    Append the matching title.
    """
    global all_titles, all_directors

    result = []
    for i in range(len(all_directors)):
        if name.lower() in all_directors[i].lower():
            result.append(all_titles[i])
    return result


# --------------------------------------------------------------
# Function: main
# Purpose:  Runs the Movie Data Manager program.
#           Displays a menu of options and calls the appropriate
#           functions based on the user's choice.
# Params:   None
# Returns:  None
#
# 🪄 Tip: Read the menu options carefully.
#        Each option calls one of your helper functions to perform
#        a task using the global movie data lists.
#        Use "0" to quit the program.
# --------------------------------------------------------------
def main():
    choice = ""  # initialize before loop

    while choice != "0":
        print("\n--- Movie Data Manager ---")
        print("1. Show all movies")
        print("2. Show full movie details")
        print("3. Show movies above a rating")
        print("4. Show highest-rated movie")
        print("5. Show movies by director")
        print("0. Quit")

        choice = input("Choose an option [enter a number]: ")

        if choice == "1":
            print_movie_list("All movies:", all_titles)

        elif choice == "2":
            title = input("Enter a title (or partial): ")
            print_full_movie_info(title)

        elif choice == "3":
            threshold = int(input("Enter minimum rating: "))
            above_rating_list = movies_above_rating(threshold)
            print_movie_list(f"Movies with rating above {threshold}:", above_rating_list)

        elif choice == "4":
            high_rated_movie = highest_rated_movie()
            print_full_movie_info(high_rated_movie)

        elif choice == "5":
            name = input("Enter director name (or partial): ")
            movies_list = movies_by_director(name)
            print_movie_list(f"Movies directed by {name}:", movies_list)

        elif choice == "0":
            print("Goodbye!")

        else:
            print("Invalid choice.")