import random

# ----------------------
# Global Variables
# ----------------------
money = 25
guess = 0
roll_value = 0


# ----------------------
# Function: Get Menu Choice
# ----------------------
def get_menu_choice():
    print(f"\nYou have ${money}")
    print("What would you like to do?")
    print("1. Roll die")
    print("2. Quit")
    choice = input("Enter 1 or 2: ")
    return choice


# ----------------------
# Function: Get Valid Guess (2–12)
# ----------------------
def get_guess():
    while True:
        user_guess = int(input("Guess a number between 2 and 12: "))
        if 2 <= user_guess <= 12:
            return user_guess
        else:
            print("Invalid guess. Please choose a number between 2 and 12.")


# ----------------------
# Function: Roll Dice
# ----------------------
def roll_dice():
    global roll_value

    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    roll_value = die1 + die2

    print(f"You rolled a {die1} and {die2} for a {roll_value}")


# ----------------------
# Function: Check Guess and Update Money
# ----------------------
def check_guess():
    global money

    if guess == roll_value:
        money += 10
        print("You guessed correctly! +$10")
    else:
        money -= 5
        print("Sorry, wrong guess. -$5")


# ----------------------
# Main Function
# ----------------------
def main():
    global guess

    choice = ""

    while choice != "2" and money > 0:

        choice = get_menu_choice()

        if choice == "1":
            guess = get_guess()
            roll_dice()
            check_guess()

        elif choice == "2":
            print("Thanks for playing!")

        else:
            print("Invalid choice")

    if money <= 0:
        print("You're out of money! Game over.")


if __name__ == "__main__":
    main()