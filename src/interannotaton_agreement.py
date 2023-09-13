import krippendorff
import pandas as pd


def df_to_experiment_annotator_table(df, experiment_col, annotator_col, class_col):
    return df.pivot_table(
        index=annotator_col, columns=experiment_col, values=class_col, aggfunc="first"
    )


def calculate_inter_annotator_agreement(responses_dir):
    results_file_list = ["coherence.csv", "grammar.csv", "repetition.csv"]
    label_to_code = {"A": 0, "B": 1}

    for file_name in results_file_list:
        full_path = responses_dir + file_name
        responses_df = pd.read_csv(full_path)

        column_name = next(filter(lambda x: x.startswith("Answer.best_"), responses_df.columns))

        responses_df["response"] = responses_df[column_name].apply(lambda x: label_to_code[x])

        annotation_matrix = (
            responses_df[['Input.code', "WorkerId", "response"]].pivot_table(index="WorkerId", columns="Input.code",
                                                                             values="response",
                                                                             aggfunc="first")
            .reset_index(drop=True))

        alpha = krippendorff.alpha(annotation_matrix.to_numpy(), level_of_measurement='nominal')
        print(f"Krippendorff's Alpha for {responses_dir.split('/')[-2] + ' ' + file_name}: {alpha:.3f}")


if __name__ == '__main__':

    # args = parser.parse_args()
    response_dirs = ['responses/lab1/', 'responses/lab2/', "responses/merged/"]

    for response_dir in response_dirs:
        calculate_inter_annotator_agreement(response_dir)
