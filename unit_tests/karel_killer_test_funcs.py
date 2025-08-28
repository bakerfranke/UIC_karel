# Global Variables - game actions should alter these variables 
# Chance of false info, starts at 40%
def printResults(before, after):
    print(
            "Variable values for [clues_found, days_remaining] before calling followALead()\n"
            f"   {before}\n"
            "Your values for [clues_found, days_remaining]\n"
            f"   {after}\n"
            "The global values should have been changed by your function.\n"
        )

"""pre-condition: before,after lists have the same length, and have
comparable elements.
post-condition: returns true if and only if the two lists have exactly
one element that differs."""
def exactlyOneDiff(before_list, after_list):
    diff_count = 0
    for i in range(len(before_list)):
        if before_list[i]!= after_list[i]:
            diff_count+=1
    return diff_count == 1


import importlib

def globalVarsExist(module_name="main", required_global_vars=[]):
    try:
        module = importlib.import_module(module_name)  # Dynamically import the module
    except ModuleNotFoundError:
        print(f"Error: Module '{module_name}' not found.")
        return False
  
    required_global_vars = ["clues_needed", "clues_found", "days_remaining", "misinformation_chance"]
    for var in required_global_vars:
        if not hasattr(module,var):
            print("The tests require these global variables to be in place (spelled the same):")
            print(required_global_vars)
            print("You are missing:",var)
            return False

    return True