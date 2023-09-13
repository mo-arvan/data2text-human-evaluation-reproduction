import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_table(table_df, save_path):
    # List of systems
    df = pd.melt(table_df.reset_index(), id_vars=["System"], var_name="Measure", value_name="Value")

    df['Value'] = df['Value'].apply(round)
    # Create a grouped bar plot
    ax = sns.barplot(data=df, x='Measure', y='Value', hue='System', palette="cubehelix")
    plt.legend(loc='lower left')
    ax.set(xlabel='', ylabel=save_path.split("_")[-1][:-4])

    for i in ax.containers:
        ax.bar_label(i, )
    # Save the plot as an image (optional)
    plt.savefig(save_path)

    # clear the plot
    plt.clf()


def measure_best_worst_scale(response_dir):
    systems_id_to_name = {
        "sys0": "Gold",
        "sys1": "Templ",
        "sys2": "ED+CC",
        "sys3": "RBF-2020",
        "sys4": "Macro",
    }

    results_file_names = ["coherence.csv", "grammar.csv", "repetition.csv"]
    table_list = []
    for results_file_name in results_file_names:
        results_file = pd.read_csv(response_dir + results_file_name)

        # Assuming your columns are named "Input.code" and "Input.system1"
        annotations = results_file[['Input.code', 'Input.system1']]
        # Pivot the DataFrame to create a matrix with IDs as rows and annotators' responses as columns
        annotation_matrix = annotations.pivot(index='Input.code', columns='Annotator', values='Input.system1')
        # Calculate Krippendorff's alpha using the krippendorff library
        alpha_value = alpha(annotation_matrix.values)

        for system in systems_id_to_name.keys():
            system_1 = results_file.loc[results_file["Input.system1"] == system]
            system_2 = results_file.loc[results_file["Input.system2"] == system]

            # if len(system_1) + len(system_2) != 240:
            #     print(f"WARNING: missing data for {system} in {response_dir + results_file_name}")

            column_name = next(filter(lambda x: "Answer.best_" in x, system_1.columns))

            best_count = len(system_1.loc[system_1[column_name] == "A"])
            best_count += len(system_2.loc[system_2[column_name] == "B"])

            worst_count = len(system_1.loc[system_1[column_name] == "B"])
            worst_count += len(system_2.loc[system_2[column_name] == "A"])

            table_list.append({
                "System": systems_id_to_name[system],
                "Measure": results_file_name.split(".")[0].capitalize().split("_")[0],
                "Wins": best_count,
                "Losses": worst_count,
                "Best-Worst Score": best_count - worst_count,
                "Best-Worst Scale": (best_count - worst_count) / (best_count + worst_count) * 100.,
                "Wins Percentage": best_count / (best_count + worst_count) * 100.
            })

    table_df = pd.DataFrame(table_list)
    # print(table_df)
    value_columns = ["Wins", "Losses", "Best-Worst Score", "Best-Worst Scale", "Wins Percentage"]
    column_order = ["Grammar", "Coherence", "Repetition"]
    row_order = ["Gold", "Templ", "ED+CC", "RBF-2020", "Macro"]
    float_formatter = "{:.2f}".format

    for value_column in value_columns:
        current_table = table_df.pivot(index='System', columns='Measure', values=value_column)

        current_table = current_table[column_order]
        current_table = current_table.reindex(row_order)

        out_base_file_name = f"{response_dir}{value_column}".replace("/", "_")
        current_table.to_csv("results/csv/" + out_base_file_name + ".csv", float_format=float_formatter)
        current_table.to_latex("results/latex/" + out_base_file_name + ".tex", float_format=float_formatter)

        # plotting the results
        plot_table(current_table, "results/figures/" + out_base_file_name + ".pdf")


if __name__ == '__main__':

    sns.set_theme()
    sns.set_style("darkgrid")
    # args = parser.parse_args()
    response_dirs = ['responses/lab1/', 'responses/lab2/', "responses/merged/"]

    for response_dir in response_dirs:
        measure_best_worst_scale(response_dir)
