import csv
import pandas as pd
from Levenshtein import ratio as sim
import os
from similarity_functions import process, compute_similarity

# This block of code take the repository, fetches all the commits,
# retrieves name and email of both the author and commiter and saves the unique
# pairs to csv

from pydriller import Repository

DEVS = set()
for commit in Repository("https://github.com/twbs/bootstrap").traverse_commits():
    DEVS.add((commit.author.name, commit.author.email))
    DEVS.add((commit.committer.name, commit.committer.email))

DEVS = sorted(DEVS)
with open(os.path.join("project1devs", "devs.csv"), 'w', newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"')
    writer.writerow(["name", "email"])
    writer.writerows(DEVS)


DEVS = []
with open(os.path.join("project1devs", "devs.csv"), 'r', newline='', encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        DEVS.append(row)
DEVS = DEVS[1:]

# Compute similarity between all possible pairs
df = compute_similarity(DEVS)

# Set similarity threshold
t = 0.9


# Apply threshold checks against the 
print("Threshold:", t)
df["c1_check"] = df["c1"] >= t
df["c2_check"] = df["c2"] >= t
df["c3_check"] = (df["c3.1"] >= t) & (df["c3.2"] >= t)

# Keep only rows where at least one condition is true
df = df[df[["c1_check", "c2_check", "c3_check", "c4", "c5", "c6", "c7"]].any(axis=1)]

# Check columns before saving
df = df[["name_1", "email_1", "name_2", "email_2",
         "c1", "c2", "c3.1", "c3.2", "c4", "c5", "c6", "c7"]]

df.to_csv(os.path.join("project1devs", f"devs_similarity_t={t}.csv"), index=False, header=True)

