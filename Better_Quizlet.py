# Add Randomness
# Add moving right answers to the right ENABLED lists

import os
import random
import time
from colorama import Fore, Style, init


init(autoreset=True)


def print_error(message):
    print(f"{Fore.RED}{Style.BRIGHT}{message}")


def start_screen():
    while True:
        print(f'Welcome to "Better" Quizlet! (tm) \n\n'
              f'In order to start, type "start" \n\n'
              f'In order to go into settings, type "settings" \n\n')

        menu_input = input("Navigate to: ")

        if menu_input.lower() == "start":
            study_set = choose_setlist()
            question_types = ask_question_types()
            randomize_questions = ask_randomize_questions()
            game(study_set, question_types, randomize_questions)
        elif menu_input.lower() == "settings":
            settings()
        else:
            print_error('\nInvalid input, please try again\n')


def choose_setlist():
    study_sets_path = "../Better_Quizlet/Study Sets"

    # Check if the directory exists
    if os.path.exists(study_sets_path) and os.path.isdir(study_sets_path):
        # List all files in the directory
        study_sets = os.listdir(study_sets_path)

        # Print the available study sets
        print(f"\nAvailable Study Sets:\n")
        for index, set_file in enumerate(study_sets, start=1):
            print(f"{index}. {set_file}")

        # Ask the player to choose a setlist
        chosen_set_index = int(input(f"\nEnter the number corresponding to the setlist you want to choose: ")) - 1

        validate_set_index(chosen_set_index, study_sets)

        return study_sets[chosen_set_index]

    else:
        print("Study Sets directory not found.\n")


def validate_set_index(chosen_set_index, study_sets):
    while True:
        if 0 <= chosen_set_index < len(study_sets):
            chosen_setlist = study_sets[chosen_set_index]
            print(f"You have chosen the setlist: {chosen_setlist}\n\n")
            return chosen_setlist
        else:
            print("Invalid selection. Please choose a valid setlist.\n")


def ask_question_types():
    question_types = ["Writing", "Flashcards", "Multiple Choice"]
    chosen_question_types = []

    print("Available Question Types:")
    for index, question_type in enumerate(question_types, start=1):
        print(f"{index}. {question_type}")

    while True:
        try:
            choice = input(
                "Enter the number(s) corresponding to the question types you want to choose (comma-separated): ")
            chosen_indices = [int(index.strip()) - 1 for index in choice.split(",")]

            for index in chosen_indices:
                if 0 <= index < len(question_types) and index not in chosen_question_types:
                    chosen_question_types.append(index)
                else:
                    print_error("\nInvalid selection. Please choose a valid question type.\n")

            more_choices = input("\nDo you want to choose more question types? (yes/no): ").lower()
            print('\n')
            if more_choices != 'yes':
                break

        except ValueError:
            print_error("\nInvalid input. Please enter valid numbers separated by commas.\n")

    chosen_question_types = [question_types[index] for index in chosen_question_types]
    print(f"You have chosen the following question types: {', '.join(chosen_question_types)}\n")

    # Save the chosen question types or use them in your game logic
    return chosen_question_types


def ask_randomize_questions():
    while True:
        try:
            choice = input("Do you want to randomize questions? (yes/no): ").lower()
            print('\n')
            if choice in ['yes', 'no']:
                return choice == 'yes'
            else:
                print_error("Invalid choice. Please enter 'yes' or 'no'.\n")
        except ValueError:
            print_error("Invalid input. Please enter 'yes' or 'no'.\n")


def game(study_set, question_types, randomize_questions):
    # Find number of terms in a study set
    with open(f'Study Sets//{study_set}', 'r') as f:
        study_set_length = len(f.readlines())
        f.seek(0)
        study_set_questions = f.readlines()

    # Creating blank lists
    finished_questions = []
    multiple_choice_list = []
    flashcards_list = []
    writing_list = []

    # Which question type to enable
    perm_enable_question_types = ["Multiple Choice" in question_types, "Flashcards" in question_types,
                                  "Writing" in question_types]
    temp_enable_question_types = [False, False]

    # Create a list for the first chosen question type
    if "Multiple Choice" in question_types:
        multiple_choice_list = list(range(study_set_length))
        if randomize_questions:
            random.shuffle(multiple_choice_list)

    elif "Flashcards" in question_types:
        flashcards_list = list(range(study_set_length))
        if randomize_questions:
            random.shuffle(flashcards_list)

    elif "Writing" in question_types:
        writing_list = list(range(study_set_length))
        if randomize_questions:
            random.shuffle(writing_list)

    # ACTUAL GAME STARTS HERE
    while study_set_length != len(finished_questions):
        too_many_flashcards = False
        too_many_writing = False
        already_used_questions = []

        max_round_length = 7
        if max_round_length > (len(writing_list) + len(flashcards_list) + len(multiple_choice_list)):
            max_round_length = len(writing_list) + len(flashcards_list) + len(multiple_choice_list)

        # Each ROUND
        for round_num in range(max_round_length):
            # Each STEP
            list_disabler = game_subround(study_set_questions, finished_questions, multiple_choice_list,
                                          flashcards_list, writing_list, temp_enable_question_types,
                                          perm_enable_question_types, already_used_questions, too_many_flashcards,
                                          too_many_writing)

            # Disables a list if needed
            if list_disabler == "disable_writing":
                too_many_writing = True
            elif list_disabler == "disable_flashcards":
                too_many_flashcards = True

            # Ensures at least some MCQs are done if there are still some
            if (round_num >= 4) and (len(multiple_choice_list) != 0):
                too_many_flashcards, too_many_writing = True, True
            elif (round_num >= 4) and (len(flashcards_list) != 0):
                too_many_writing = True

        # End of the round
        if temp_enable_question_types[0]:
            temp_enable_question_types[1] = True
        else:
            temp_enable_question_types[0] = True

        print("\nGood Job So Far!\n")
        time.sleep(.5)
        input("Press enter to continue... ")

    # End
    print(f'\nStudy Set Completed!\n')
    input(f'Press enter to continue... \n')
    time.sleep(.5)


def game_subround(study_set_questions, finished_questions, multiple_choice_list, flashcards_list, writing_list,
                  temp_enable_question_types, perm_enable_question_types, already_used_questions, too_many_flashcards,
                  too_many_writing):
    # Find order to move correct questions to
    question_type_order = []
    question_type_template = [multiple_choice_list, flashcards_list, writing_list]
    for i in range(3):
        if perm_enable_question_types[i]:
            question_type_order.append(question_type_template[i])
    question_type_order.append(finished_questions)

    question_correct = False

    if (temp_enable_question_types[1] and perm_enable_question_types[2] and (not too_many_writing) and
            (len(writing_list) != 0)):
        question_index = find_question_number(writing_list, already_used_questions)
        if question_index + 1:  # Checks that an index was found
            question_correct = writing_question(study_set_questions, writing_list, question_index)

        if question_correct:
            writing_question_type_index = question_type_order.index(writing_list)
            moving_questions_between_lists(question_type_order[writing_question_type_index + 1],
                                           writing_list, question_index)
            return stop_doing_question_in_a_row(question_type_order[writing_question_type_index + 1],
                                                writing_list, flashcards_list)
        else:
            already_used_questions.append(writing_list[question_index])

    elif (temp_enable_question_types[0] and perm_enable_question_types[1] and (not too_many_flashcards) and
          (len(flashcards_list) != 0)):
        question_index = find_question_number(flashcards_list, already_used_questions)
        if question_index + 1:  # Checks that an index was found
            question_correct = flashcard_question(study_set_questions, flashcards_list, question_index)

        if question_correct:
            flashcards_question_type_index = question_type_order.index(flashcards_list)
            moving_questions_between_lists(question_type_order[flashcards_question_type_index + 1], flashcards_list,
                                           question_index)
            return stop_doing_question_in_a_row(question_type_order[flashcards_question_type_index + 1],
                                                writing_list, flashcards_list)

        else:
            already_used_questions.append(flashcards_list[question_index])

    elif perm_enable_question_types[0] and (len(multiple_choice_list) != 0):
        question_index = find_question_number(multiple_choice_list, already_used_questions)
        if question_index + 1:  # Checks that an index was found
            question_correct = multiple_choice_question(study_set_questions, multiple_choice_list, question_index)

        if question_correct:
            mcq_question_type_index = question_type_order.index(multiple_choice_list)
            moving_questions_between_lists(question_type_order[mcq_question_type_index + 1], multiple_choice_list,
                                           question_index)
            return stop_doing_question_in_a_row(question_type_order[mcq_question_type_index + 1],
                                                writing_list, flashcards_list)
        else:
            already_used_questions.append(multiple_choice_list[question_index])

    elif temp_enable_question_types[0]:
        temp_enable_question_types[1] = True

    else:
        temp_enable_question_types[0] = True


def find_question_type(multiple_choice_list, flashcards_list, writing_list, subround):
    try:
        question_number = find_question_number(writing_list, subround)  # Search for writing questions
        return question_number, writing_list
    except IndexError:
        try:
            question_number = find_question_number(flashcards_list, subround)  # Then go to flashcards
            return question_number, flashcards_list
        except IndexError:
            question_number = find_question_number(multiple_choice_list, subround)  # Finally MCQ
            return question_number, multiple_choice_list


def find_question_number(question_list, already_used_questions):
    shifter = 0
    while True:
        try:
            if question_list[shifter] not in already_used_questions:
                break
            else:
                shifter += 1
        except IndexError:  # End subround
            return -1  # After adding 1, it's still false

    return shifter


def writing_question(study_set_questions, writing_list, question_index):
    question = study_set_questions[writing_list[question_index]]

    term, definition = question.split(" | ")
    user_input = input(f"Definition: {definition.strip()}\nYour answer: ")

    if user_input.lower() == term.lower():
        print("\nCorrect! You got it right. \n")
        question_correct = True
    else:
        print(f"\nWrong! The correct term is {term}. \n")
        question_correct = False

    input("Press enter to continue... \n")
    time.sleep(.5)

    return question_correct


def flashcard_question(study_set_questions, flashcard_list, question_index):
    # Extract info from list to create question
    question = study_set_questions[flashcard_list[question_index]]
    term, definition = question.split(" | ")

    # Flashcard Process
    input(f"Definition: {definition.strip()}\nPress enter to reveal the term...")
    user_input = input(f"\nTerm: {term}\nDid you get it correct? (yes/no): ")

    if user_input.lower() == 'yes':
        print("\nGreat job! You got it right!\n")
        question_correct = True
    else:
        print(f"\nNice try! You'll get it next time!\n")
        question_correct = False

    input("Press enter to continue...")
    time.sleep(.5)

    return question_correct


def multiple_choice_question(study_set_questions, multiple_choice_list, question_index):
    question = study_set_questions[multiple_choice_list[question_index]]
    term, definition = question.split(" | ")

    # Get wrong answers
    wrong_question_terms = []
    wrong_question_definition = []
    wrong_answers_list = []
    for wrong_question_num in range(3):
        # Call random term index that isn't the current one
        wrong_answer_index = find_wrong_answers_index(study_set_questions, multiple_choice_list[question_index],
                                                      wrong_answers_list)

        # Find the answer from the study set
        wrong_answer = study_set_questions[wrong_answer_index]
        wrong_term, wrong_definition = wrong_answer.split(" | ")

        # Append the info
        wrong_question_terms.append(wrong_term)
        wrong_question_definition.append(wrong_definition)
        wrong_answers_list.append(wrong_answer_index)

    # Create a list with the correct term and three random incorrect terms
    correct_term_in_list = [term]
    options = correct_term_in_list + wrong_question_terms

    # Shuffle the options
    random.shuffle(options)

    print(f"Definition: {definition.strip()}")
    print("Options:")
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")

    user_input = input("\nEnter the number corresponding to the correct term: ")

    while True:
        try:
            chosen_index = int(user_input) - 1

            if 0 <= chosen_index < len(options) and options[chosen_index] == term:
                print("\nCorrect! You got it right.")
                question_correct = True
                break
            else:
                print(f"\nWrong! The correct term is {term}.")
                question_correct = False
                break

        except ValueError:
            print("\nInvalid input. Please enter a valid number.")

    input("\nPress enter to continue...")
    time.sleep(.5)

    return question_correct


def find_wrong_answers_index(study_set_questions, question_index, wrong_answers_list):
    found_question = False
    while not found_question:
        random_num = random.randint(0, len(study_set_questions) - 1)
        if (random_num != question_index) and (random_num not in wrong_answers_list):
            return random_num


def moving_questions_between_lists(new_list, old_list, question_index):
    # Move the question index to a new list
    new_list.append(old_list[question_index])

    # Remove from the old list
    old_list.pop(question_index)


def stop_doing_question_in_a_row(new_list, writing_list, flashcards_list):
    # Check size of new list, let program know if its only one (only old question is in the list)
    if len(new_list) == 1:
        if new_list is writing_list:
            return "disable_writing"
        elif new_list is flashcards_list:
            return "disable_flashcards"
    return 0


def settings():
    pass


def main():
    start_screen()


main()
