"""
Download the responses collected by lab 1, clean them up, and convert them to CSV files for further analysis.
"""

import io

import pandas as pd
import requests

# List of URLs
urls = [
    "https://github.com/evanmiltenburg/ReproHum-D2T/raw/main/Results/Responses/Combined/Grammaticality.xlsx",
    "https://github.com/evanmiltenburg/ReproHum-D2T/raw/main/Results/Responses/Combined/Repetition.xlsx",
    "https://github.com/evanmiltenburg/ReproHum-D2T/raw/main/Results/Responses/Combined/Coherence.xlsx"
]

# Output CSV filenames
output_files = ["grammar.csv", "repetition.csv", "coherence.csv"]


# Function to download and convert to CSV
def download_and_convert_to_csv(url, output_file):
    try:
        if url.endswith('.xlsx'):
            # Download the Excel file
            response = requests.get(url)
            excel_data = response.content
            excel_io = io.BytesIO(excel_data)

            # Convert to CSV
            df = pd.read_excel(excel_io)

            # remove the first column as it is only the index
            df = df.iloc[:, 1:]
            best_column_name = next(filter(lambda x: x.startswith("Answer.best_"), df.columns))
            worst_column_name = next(filter(lambda x: x.startswith("Answer.worst_"), df.columns))

            # check if there are any invalid annotations, we expect only A or B and remove them
            df = df.loc[df[best_column_name].isin(["A", "B"])]
            df = df.loc[df[worst_column_name].isin(["A", "B"])]

            df.to_csv(output_file, index=False)
            print(f"Successfully converted {url} to {output_file[:-5]}.csv")
        else:
            print(f"Skipping {url} as it is not an Excel file.")
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


response_dir = "responses/lab1"
# Download and convert each URL
for url, output_file in zip(urls, output_files):
    output_file_path = f"{response_dir}/{output_file}"
    download_and_convert_to_csv(url, output_file_path)
