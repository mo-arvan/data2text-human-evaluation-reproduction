from scipy.stats import pearsonr, spearmanr
import cv
import pandas as pd


def calculate_pearson_spearman_correlation(set_a, set_b):
    # Pearson's r
    pearson_corr, pearson_p = pearsonr(set_a, set_b)

    # Spearman's ρ
    spearman_corr, spearman_p = spearmanr(set_a, set_b)
    #
    # print("Pearson's r: ", pearson_corr, "p-value: ", pearson_p)
    # print("Spearman's ρ: ", spearman_corr, "p-value: ", spearman_p)

    pearson_result_dict = {
        "input a": set_a,
        "input b": set_b,
        "pearson_corr": pearson_corr,
        "pearson_p": pearson_p,
    }
    spearman_result_dict = {
        "input a": set_a,
        "input b": set_b,
        "spearman_corr": spearman_corr,
        "spearman_p": spearman_p,
    }

    return pearson_result_dict, spearman_result_dict


def calculate_coefficient_of_variation(result_sets, range_start, range_end):
    range_shift = 0
    if range_start < 0:
        range_shift = abs(range_start)

    number_of_results = len(result_sets[0])

    full_result_list = []
    for i in range(number_of_results):
        values = [result_set[i] + range_shift for result_set in result_sets]

        precision_results = cv.get_precision_results(values)

        for i in range(len(precision_results["values"])):
            precision_results["values"][i] -= range_shift

        full_result_list.append(precision_results)
    return full_result_list


def report_2_way_reproducibility():
    original_results_df = pd.read_csv("results/original/results.csv")

    survey_dict = {'Lab 1': 'results/lab_1/',
                   'Lab 2': 'results/lab_2/',
                   'Lab 1 and 2': "results/lab_1_and_2/"}
    measure_to_file_dict = {"Coherence": "coherence.csv",
                            "Grammar": "grammar.csv",
                            "Repetition": "repetition.csv"}

    pearson_list = []
    spearman_list = []
    cv_list = []
    system_to_order_dict = {"Gold": 1, "Templ": 2, "ED+CC": 3, "RBF-2020": 4, "Macro": 5}

    original_results_df["O"] = original_results_df["System"].apply(lambda x: system_to_order_dict[x])
    original_results_df.sort_values(by="O", inplace=True)
    original_results_df.drop(columns=["O"], inplace=True)

    for measure_name, results_file_name in measure_to_file_dict.items():
        for survey_origin, survey_dir in survey_dict.items():
            results_df = pd.read_csv(survey_dir + "csv/" + results_file_name)
            # lab 1 to original
            # lab 2 to original
            # lab 1 and lab 2 to orignal

            results_df = sort_by_systems_dict(results_df, system_to_order_dict)
            # need to ensure that the data is in the same order, this can be done using the system column
            original_values = original_results_df[measure_name].values
            reproduction_values = results_df["Best-Worst Scale"].values

            pearson_result_dict, spearman_result_dict = calculate_pearson_spearman_correlation(original_values,
                                                                                               reproduction_values)
            pearson_result_dict["survey_origin"] = survey_origin
            spearman_result_dict["survey_origin"] = survey_origin

            pearson_result_dict["measure"] = measure_name
            spearman_result_dict["measure"] = measure_name

            pearson_list.append(pearson_result_dict)
            spearman_list.append(spearman_result_dict)
            cv_result_list = calculate_coefficient_of_variation([original_values,
                                                                 reproduction_values],
                                                                -100,
                                                                100)
            for cv_result in cv_result_list:
                cv_result["survey_origin"] = survey_origin
                cv_result["measure"] = measure_name
            cv_list.extend(cv_result_list)

    pearson_df = pd.DataFrame(pearson_list)
    spearman_df = pd.DataFrame(spearman_list)
    cv_df = pd.DataFrame(cv_list)

    pearson_df.to_csv("results/comparative/pearson.csv", index=False)
    pearson_df.to_latex("results/comparative/pearson.tex", index=False, float_format='%.2f', escape=True)
    spearman_df.to_csv("results/comparative/spearman.csv", index=False)
    spearman_df.to_latex("results/comparative/spearman.tex", index=False, float_format='%.2f', escape=True)
    cv_df.to_csv("results/comparative/cv_2_way.csv", index=False)
    cv_df.to_latex("results/comparative/cv_2_way.tex", index=False, float_format='%.2f', escape=True)


def sort_by_systems_dict(df, system_to_order_dict):
    df["O"] = df["System"].apply(lambda x: system_to_order_dict[x])
    df.sort_values(by="O", inplace=True)
    df.drop(columns=["O"], inplace=True)
    return df


def report_3_way_reproducibility():
    original_results_df = pd.read_csv("results/original/results.csv")

    survey_dict = {'Lab 1': 'results/lab_1/',
                   'Lab 2': 'results/lab_2/',
                   'Lab 1 and 2': "results/lab_1_and_2/"}
    measure_to_file_dict = {"Coherence": "coherence.csv",
                            "Grammar": "grammar.csv",
                            "Repetition": "repetition.csv"}

    pearson_list = []
    spearman_list = []
    cv_list = []

    system_to_order_dict = {"Gold": 1, "Templ": 2, "ED+CC": 3, "RBF-2020": 4, "Macro": 5}

    original_results_df = sort_by_systems_dict(original_results_df, system_to_order_dict)
    for measure_name, results_file_name in measure_to_file_dict.items():

        lab1_results_df = pd.read_csv(survey_dict["Lab 1"] + "csv/" + results_file_name)
        lab2_results_df = pd.read_csv(survey_dict["Lab 2"] + "csv/" + results_file_name)
        # lab 1 to original
        # lab 2 to original
        # lab 1 and lab 2 to orignal

        lab1_results_df = sort_by_systems_dict(lab1_results_df, system_to_order_dict)
        lab2_results_df = sort_by_systems_dict(lab2_results_df, system_to_order_dict)
        # need to ensure that the data is in the same order, this can be done using the system column
        original_values = original_results_df[measure_name].values
        lab1_values = lab1_results_df["Best-Worst Scale"].values
        lab2_values = lab2_results_df["Best-Worst Scale"].values

        cv_result_list = calculate_coefficient_of_variation([original_values,
                                                             lab1_values,
                                                             lab2_values],
                                                            -100,
                                                            100)
        for cv_result in cv_result_list:
            cv_result["measure"] = measure_name
        cv_list.extend(cv_result_list)

    cv_df = pd.DataFrame(cv_list)

    cv_df.to_csv("results/comparative/cv_3_way.csv", index=False)
    cv_df.to_latex("results/comparative/cv_3_way.tex", index=False, float_format='%.2f', escape=True)


def main():
    # results_df = pd.read_csv("results/ours/metrics.csv")
    report_2_way_reproducibility()
    report_3_way_reproducibility()


if __name__ == "__main__":
    main()
