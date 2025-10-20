import unicodedata
import string
from Levenshtein import ratio as sim
from itertools import combinations
import pandas as pd

# Common ignored prefixes for emails
COMMON_PREFIXES = {"me", "github", "mail", "hi", "hello", "info", "contact"}


def process(dev):

    """
    Preprocess a name, email pair.
    Removes punctuation, normalizes accents, converts to lowercase,
    and splits into first and last name.

    """
    name: str = dev[0]

    # Remove punctuation
    trans = name.maketrans("", "", string.punctuation)
    name = name.translate(trans)
    # Remove accents, diacritics
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    # Lowercase
    name = name.casefold()
    # Strip whitespace
    name = " ".join(name.split())

    # Attempt to split name into firstname, lastname by space
    parts = name.split(" ")
    # Expected case
    if len(parts) == 2:
        first, last = parts
    # If there is no space, firstname is full name, lastname empty
    elif len(parts) == 1:
        first, last = name, ""
    # If there is more than 1 space, firstname is until first space, rest is lastname
    else:
        first, last = parts[0], " ".join(parts[1:])

    # Take initials of firstname and lastname if they are long enough
    i_first = first[0] if len(first) > 1 else ""
    i_last = last[0] if len(last) > 1 else ""

    # Determine email prefix
    email: str = dev[1]
    prefix = email.split("@")[0]

    return name, first, last, i_first, i_last, email, prefix



def compute_similarity(devs,t=0.9):

    """
    Compute similarity for all developer pairs based on Bird heuristic (C1–C7).
    Includes prefix-related conditions only if neither developer has a common prefix.
    """
    SIMILARITY = []

    for dev_a, dev_b in combinations(devs, 2):
        # Pre-process both developers
        name_a, first_a, last_a, i_first_a, i_last_a, email_a, prefix_a = process(dev_a)
        name_b, first_b, last_b, i_first_b, i_last_b, email_b, prefix_b = process(dev_b)

        # Conditions of Bird heuristic
        c1 = sim(name_a, name_b)             # full name similarity
        c2 = sim(prefix_a, prefix_b)         # email prefix similarity
        c31 = sim(first_a, first_b)          # first name similarity
        c32 = sim(last_a, last_b)            # last name similarity 
        c4 = c5 = c6 = c7 = False

        # Since lastname and initials can be empty, perform appropriate checks
        if i_first_a != "" and last_a != "":
            c4 = i_first_a in prefix_b and last_a in prefix_b
        if i_last_a != "":
            c5 = i_last_a in prefix_b and first_a in prefix_b
        if i_first_b != "" and last_b != "":
            c6 = i_first_b in prefix_a and last_b in prefix_a
        if i_last_b != "":
            c7 = i_last_b in prefix_a and first_b in prefix_a

        # Determine if prefixes are common
        prefix_a_common = prefix_a in COMMON_PREFIXES
        prefix_b_common = prefix_b in COMMON_PREFIXES

    
        # Always allow name-based matches (C1 or C3)
        strong_name_match = (c1 >= t) or (c31 >= t and c32 >= t)

        # Only allow email-based or initial-based rules if prefixes are not common
        if not (prefix_a_common or prefix_b_common):
            email_based_match = (
                c2 >= t or c4 or c5 or c6 or c7
            )
        else:
            email_based_match = False

        # Check emails are different, strong name match and optionally valid initial/email-based match
        if  email_a != email_b and strong_name_match and (strong_name_match or email_based_match):
            # Save similarity data for each conditions. Original names are saved
            SIMILARITY.append([dev_a[0], email_a, dev_b[0], email_b, c1, c2, c31, c32, c4, c5, c6, c7])


    # Save data on all pairs
    cols = ["name_1", "email_1", "name_2", "email_2",
            "c1", "c2", "c3.1", "c3.2", "c4", "c5", "c6", "c7"]

    return pd.DataFrame(SIMILARITY, columns=cols)
