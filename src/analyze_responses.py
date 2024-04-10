import collections
import functools
import os
import shutil
import warnings
import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utils
import interannotaton_agreement

warnings.filterwarnings("ignore", "is_categorical_dtype")


# anova, tukey test
# responses from users who had more than X responses within this task
# proportions for how often each participant agrees with the majority
# time spend reading the instructions

def plot_table(table_df):
    response_list = table_df["Response"].unique()
    filter_list = table_df["Filter"].unique().tolist()
    measure_list = table_df["Measure"].unique()
    filter_list.reverse()
    metric_column_list = ["Wins", "Losses", "Best-Worst Score", "Best-Worst Scale", "Wins Percentage", "Rank"]

    n_rows = len(response_list) * len(filter_list)
    color_palette = sns.color_palette("colorblind", 5)
    # swap first and second colors, we want to the gold label to have the same color
    color_palette[0], color_palette[1] = color_palette[1], color_palette[0]

    for metric_column in metric_column_list:
        table_df[metric_column] = table_df[metric_column].apply(round)

        # fig, axes_list = plt.subplots(n_rows, 1, figsize=(9, n_rows * 5))

        min_value = table_df[metric_column].min()
        max_value = table_df[metric_column].max()
        max_value, min_value = max_value + (max_value - min_value) * 0.1, min_value - (max_value - min_value) * 0.1
        min_value = min(min_value, 0)

        plot_index = 0
        for filter_name in filter_list:
            for response in response_list:
                sub_df = table_df.loc[(table_df["Response"] == response) & (table_df["Filter"] == filter_name)]
                # Create a grouped bar plot

                ax = sns.barplot(data=sub_df,
                                 x='Measure',
                                 y=metric_column,
                                 hue='System',
                                 palette=color_palette,
                                 # ax=axes_list[plot_index]
                                 )
                sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
                # plt.legend(bbox_to_anchor=(1.0, 1), loc='upper left', borderaxespad=0)
                ax.set(xlabel='', ylabel=metric_column)
                ax.set_ylim([min_value, max_value])
                plot_title = response
                if filter_name != "None":
                    plot_title += " - " + filter_name
                ax.set_title(plot_title)
                # compact the layout
                plt.tight_layout()

                for i in ax.containers:
                    ax.bar_label(i, )

                save_path = "results/figures/" + get_file_name(
                    response + " " + metric_column + " " + filter_name) + ".pdf"
                plt.savefig(save_path)
                plt.clf()

                plot_index += 1
        # save_path = "results/figures/" + get_file_name(metric_column) + ".pdf"
        # Save the plot as an image (optional)
        # plt.savefig(save_path)
        # clear the plot
        # plt.clf()


def evaluate_responses(df, response, measure, filter_name="None"):
    systems_id_to_name = {
        "sys0": "Gold",
        "sys1": "Templ",
        "sys2": "ED+CC",
        "sys3": "RBF-2020",
        "sys4": "Macro",
    }

    system_measure_list = []

    for system in systems_id_to_name.keys():
        system_1 = df.loc[df["Input.system1"] == system]
        system_2 = df.loc[df["Input.system2"] == system]

        # if len(system_1) + len(system_2) != 240:
        #     print(f"WARNING: missing data for {system} in {response_dir + results_file_name}")

        column_name = next(filter(lambda x: "Answer.best_" in x, system_1.columns))

        best_count = len(system_1.loc[system_1[column_name] == "A"])
        best_count += len(system_2.loc[system_2[column_name] == "B"])

        worst_count = len(system_1.loc[system_1[column_name] == "B"])
        worst_count += len(system_2.loc[system_2[column_name] == "A"])

        best_worst_scale = None
        win_percentage = None

        if best_count + worst_count != 0:
            best_worst_scale = (best_count - worst_count) / (best_count + worst_count) * 100.
            win_percentage = best_count / (best_count + worst_count) * 100.

        system_measure_list.append({
            "System": systems_id_to_name[system],
            "Response": response,
            "Measure": measure,
            "Filter": filter_name,
            "Wins": best_count,
            "Losses": worst_count,
            "Best-Worst Score": best_count - worst_count,
            "Best-Worst Scale": best_worst_scale,
            "Wins Percentage": win_percentage,
        })

    # we add the rank of each system based on the best-worst score
    system_measure_list = sorted(system_measure_list, key=lambda x: x["Best-Worst Score"], reverse=True)
    for index, system_measure in enumerate(system_measure_list):
        system_measure["Rank"] = index + 1

    # we need the output to be in this order
    system_to_order_dict = {"Gold": 1, "Templ": 2, "ED+CC": 3, "RBF-2020": 4, "Macro": 5}
    system_measure_list = sorted(system_measure_list, key=lambda x: system_to_order_dict[x["System"]])

    return system_measure_list


def get_stats(df, response_name, measure_name, filter_name="None"):
    life_time_approval_rate = utils.get_lifetime_approval_rate(df)
    life_time_approval_rate_mean = life_time_approval_rate.mean()
    life_time_approval_rate_std = life_time_approval_rate.std()
    life_time_approval_median = life_time_approval_rate.median()

    decision_time = utils.get_decision_time(df)
    decision_time_mean = decision_time.mean()
    decision_time_std = decision_time.std()
    decision_time_median = decision_time.median()

    hit_duration = df["WorkTimeInSeconds"]
    hit_duration_mean = hit_duration.mean()
    hit_duration_std = hit_duration.std()
    hit_duration_median = hit_duration.median()

    response_per_worker = df["WorkerId"].value_counts().reset_index()
    response_per_worker_mean = response_per_worker["count"].mean()
    response_per_worker_std = response_per_worker["count"].std()
    response_per_worker_median = response_per_worker["count"].median()

    number_of_participants = df["WorkerId"].nunique()

    inter_rater_agreement = interannotaton_agreement.calculate_inter_annotator_agreement_from_df(df)

    result_dict = {"Response": response_name,
                   "Measure": measure_name,
                   "Filter": filter_name,
                   "Life Time Approval Rate Mean": life_time_approval_rate_mean,
                   "Life Time Approval Rate Std": life_time_approval_rate_std,
                   "Life Time Approval Rate Median": life_time_approval_median,
                   # "Life Time Approval Rate Array": life_time_approval_rate.to_numpy(),
                   "Decision Time Mean (seconds)": decision_time_mean,
                   "Decision Time Std (seconds)": decision_time_std,
                   "Decision Time Median (seconds)": decision_time_median,
                   # "Decision Time Array (seconds)": decision_time.to_numpy(),
                   "Hit Duration Mean": hit_duration_mean,
                   "Hit Duration Std": hit_duration_std,
                   "Hit Duration Median": hit_duration_median,
                   "Response Per Worker Mean": response_per_worker_mean,
                   "Response Per Worker Std": response_per_worker_std,
                   "Response Per Worker Median": response_per_worker_median,
                   "Number of Participants": number_of_participants,
                   "Inter Rater Agreement": inter_rater_agreement,
                   }

    return result_dict


def get_float_formatter():
    return "{:.2f}".format


def get_file_name(given_name):
    return given_name.replace("/", "_").replace(" ", "_").lower()


def report_results(df):
    float_formatter = "{:.2f}".format

    value_columns = ["Wins", "Losses", "Best-Worst Score", "Best-Worst Scale", "Wins Percentage", "Rank"]
    column_order_list = ["Grammar", "Coherence", "Repetition"]
    system_order_list = ["Gold", "Templ", "ED+CC", "RBF-2020", "Macro"]
    filter_order_list = sorted(df["Filter"].unique())
    response_order_list = ["Lab 1", "Lab 2", "Lab 1 and 2"]
    df.to_csv("results/csv/measures_all.csv", float_format=float_formatter, index=False)
    df.to_latex("results/latex/measures_all.tex", float_format=float_formatter, index=False)

    # Order : filter, response, measure, system
    total_systems = len(system_order_list)
    system_order = df["System"].apply(lambda x: system_order_list.index(x))

    total_systems_measures = total_systems * len(column_order_list)
    measure_order = df["Measure"].apply(lambda x: column_order_list.index(x))

    total_systems_measures_responses = total_systems_measures * len(response_order_list)
    response_order = df["Response"].apply(lambda x: response_order_list.index(x))

    # total_systems_measures_responses_filters = total_systems_measures_responses * len(filter_order_list)
    filter_order = df["Filter"].apply(lambda x: filter_order_list.index(x))

    df["order"] = (filter_order * total_systems_measures_responses + \
                   response_order * total_systems_measures + \
                   measure_order * total_systems + \
                   system_order
                   )

    df = df.sort_values(by="order")
    df.drop(columns=["order"], inplace=True)

    plot_table(df)

    for value_column in value_columns:
        current_table = df.pivot(index=['Response', 'System', 'Filter'], columns='Measure', values=value_column)

        current_table = current_table[column_order_list].reset_index()

        out_base_file_name = "measures_" + get_file_name(value_column) + "_all"

        current_table.to_csv("results/csv/" + out_base_file_name + ".csv", float_format=float_formatter, index=False)
        current_table.to_latex("results/latex/" + out_base_file_name + ".tex", float_format=float_formatter,
                               index=False,
                               caption=value_column)

        # plotting the results


def report_stats(df):
    stats_columns = ["Life Time Approval Rate Median",
                     "Decision Time Median (seconds)",
                     "Hit Duration Median",
                     "Response Per Worker Median",
                     "Number of Participants",
                     "Inter Rater Agreement"]

    float_formatter = "{:.2f}".format

    df.drop(columns=["Filter"], inplace=True)

    df.to_csv("results/csv/stats_all.csv", float_format=float_formatter, index=False)
    df.to_latex("results/latex/stats_all.tex", float_format=float_formatter, index=False)

    for column in stats_columns:
        matching_columns = [col for col in df.columns if col.startswith(column)]

        sub_df = df[["Response", "Measure"] + matching_columns]
        sub_df = sub_df.rename(columns={col: col.replace(column, "") for col in matching_columns})

        csv_file_path = "results/csv/stats_" + get_file_name(column) + ".csv"
        tex_file_path = "results/latex/stats_" + get_file_name(column) + ".tex"

        sub_df.to_csv(csv_file_path,
                      float_format=float_formatter,
                      index=False)
        sub_df.to_latex(tex_file_path,
                        float_format=float_formatter,
                        caption=column,
                        index=False)


def report_metrics_stats(response_name, measure_name, system_measure_list, stats_dict):
    system_measure_df = pd.DataFrame(system_measure_list)

    system_order_dict = {"Gold": 1, "Templ": 2, "ED+CC": 3, "RBF-2020": 4, "Macro": 5}
    system_measure_df["O"] = system_measure_df["System"].apply(lambda x: system_order_dict[x])
    system_measure_df.sort_values(by="O", inplace=True)
    system_measure_df.drop(columns=["O"], inplace=True)
    original_results_df = pd.read_csv("results/original/results.csv")
    original_results_df["O"] = original_results_df["System"].apply(lambda x: system_order_dict[x])
    original_results_df.sort_values(by="O", inplace=True)
    original_results_df.drop(columns=["O"], inplace=True)

    summary_df = pd.DataFrame()
    summary_df["System"] = system_measure_df["System"]
    summary_df["Orig"] = original_results_df[measure_name]
    summary_df["Rep"] = system_measure_df["Best-Worst Scale"]

    base_out_dir = "results/" + get_file_name(response_name)

    csv_dir = base_out_dir + "/csv/"
    latex_dir = base_out_dir + "/latex/"

    for out_dir in [csv_dir, latex_dir]:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    summary_df.to_csv(csv_dir + get_file_name(measure_name) + "_summary.csv",
                        float_format=get_float_formatter(),
                        index=False,
                        quoting=csv.QUOTE_NONNUMERIC)
    summary_df.to_latex(latex_dir + get_file_name(measure_name) + "_summary.tex",
                        float_format=get_float_formatter(),
                        index=False,
                        escape=True)

    system_measure_df.to_csv(csv_dir + get_file_name(measure_name) + ".csv",
                             float_format=get_float_formatter(),
                             index=False,
                             quoting=csv.QUOTE_NONNUMERIC)
    system_measure_df.to_latex(latex_dir + get_file_name(measure_name) + ".tex",
                               float_format=get_float_formatter(),
                               index=False,
                               escape=True)

    stats_list = []
    for k, v in stats_dict.items():
        if k in ["Response", "Measure", "Filter"]:
            continue
        stats_list.append({"Response": response_name,
                           "Measure": measure_name,
                           "Name": k,
                           "Value": v}
                          )

    stats_df = pd.DataFrame(stats_list)

    stats_df.to_csv(csv_dir + "stats_" + get_file_name(measure_name) + ".csv",
                    float_format=get_float_formatter(),
                    index=False,
                    quoting=csv.QUOTE_NONNUMERIC)
    stats_df.to_latex(latex_dir + "stats_" + get_file_name(measure_name) + ".tex",
                      float_format=get_float_formatter(),
                      index=False,
                      escape=True)


def main():
    sns.set_theme()
    sns.set_style("darkgrid")

    survey_dict = {'Lab 1': 'responses/lab1/',
                   'Lab 2': 'responses/lab2/',
                   'Lab 1 and 2': "responses/merged/"}
    measure_to_file_dict = {"Coherence": "coherence.csv",
                            "Grammar": "grammar.csv",
                            "Repetition": "repetition.csv"}

    measure_result_list = []
    stats_result_list = []

    for measure_name, results_file_name in measure_to_file_dict.items():
        response_df_list = []
        for survey_origin, survey_dir in survey_dict.items():
            responses_df = pd.read_csv(survey_dir + results_file_name)
            # if filter_function is not None:
            #     responses_df = filter_function(responses_df)
            response_df_list.append(responses_df)

            system_measure_list = evaluate_responses(responses_df, survey_origin, measure_name)
            stats_dict = get_stats(responses_df, survey_origin, measure_name)

            report_metrics_stats(survey_origin, measure_name, system_measure_list, stats_dict)

            measure_result_list.append(system_measure_list)
            stats_result_list.append(stats_dict)


if __name__ == '__main__':
    main()
