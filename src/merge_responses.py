import os

import pandas as pd

# Define the directory names
directories = ["lab1", "lab2"]

# Define the list of CSV files to merge
csv_files_to_merge = ["coherence.csv", "grammar.csv", "repetition.csv"]

# Initialize a dictionary to store the merged DataFrames
merged_data = {}

response_dir = "responses/"
output_dir = "merged/"
# Loop through the CSV files to merge
for csv_file in csv_files_to_merge:
    # Construct the file path
    lab_1_path = os.path.join(response_dir + directories[0], csv_file)
    lab_2_path = os.path.join(response_dir + directories[1], csv_file)

    # Read the CSV files
    lab_1_df = pd.read_csv(lab_1_path)
    lab_2_df = pd.read_csv(lab_2_path)

    # Merge the DataFrames
    merged_df = pd.concat([lab_1_df, lab_2_df])

    merged_df.to_csv(os.path.join(response_dir + output_dir, csv_file), index=False)
