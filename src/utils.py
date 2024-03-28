import pandas as pd
import json
import collections
import functools
import json
import os
import re
import shutil
from datetime import datetime


def get_lifetime_approval_rate(df):
    approval_rate_series = df["LifetimeApprovalRate"].apply(lambda x: float(x.split("(")[1].split("/")[0]))
    return approval_rate_series


def get_timezone(df):
    timezone_series = df["Answer.clicks"].apply(lambda x: json.loads(x)["start_time"].split("(")[-1][:-1])
    return timezone_series


def get_decision_time(df):
    def calculate_time_spent(click_list):
        # we need to find the window between when the user reads the last introduction
        # and when the user submits the response
        # very hacky way of doing this, not easy to predict the pattern of clicks
        # but it seems to work for now

        # Here is the structure of html:

        # Instructions
        #     next-intro
        # question1
        #     next-intro
        #
        # question2
        #     best
        #     worst
        #     next-summary1
        # CROWD-BUTTON

        next_intro_clicks = list(filter(lambda x: x[1]["id_tag"].startswith("next-intro"),
                                        enumerate(click_list)))
        if len(next_intro_clicks) != 2:
            # print("Warning: next button clicked more than twice")
            pass
        last_intro_click = next_intro_clicks[-1][0]

        click_window = click_list[last_intro_click:]
        next_button_clicked_list = list(filter(lambda x: x[1]["id_tag"].startswith("next-summary"),
                                               enumerate(click_window)))
        if len(next_button_clicked_list) == 0:
            next_button_clicked_list = list(filter(lambda x: x[1]["nodeName"].startswith("CROWD-BUTTON"),
                                                   enumerate(click_window)))

        click_window = click_window[:next_button_clicked_list[-1][0] + 1]

        # final sanity check
        # if the window does not contain best or worst, then we have a problem finding the window
        contains_best = any(map(lambda x: x["id_tag"].startswith("best"), click_window))
        contains_worst = any(map(lambda x: x["id_tag"].startswith("worst"), click_window))
        contains_question = any(map(lambda x: x["id_tag"].startswith("question2"), click_window))

        if not contains_worst and not contains_best and not contains_question:
            print("Warning: window not found")
            print(click_window)
        previous_click_time = click_window[0]["time"]
        next_click_time = click_window[-1]["time"]

        timestamp_pattern_1 = r'(\w{3} \w{3} \d{2} \d{4} \d{2}:\d{2}:\d{2})'
        datetime_str_pattern_1 = '%a %b %d %Y %H:%M:%S'
        date_time_match = re.search(timestamp_pattern_1, previous_click_time)
        if date_time_match is not None:
            date_time_str = date_time_match.group(1)
            previous_click_time = datetime.strptime(date_time_str, datetime_str_pattern_1)

            next_click_time = datetime.strptime(re.search(timestamp_pattern_1, next_click_time).group(1),
                                                datetime_str_pattern_1)
        else:
            # we have to try other patterns
            print("Warning: timestamp pattern not found")

        time_spent = (next_click_time - previous_click_time).total_seconds()

        # if time_spent <= 1:
        #     print("Warning: time spent is unreasonable")
        # if time_spent < 5:
        #     print("Warning: time spent is too short")
        # if time_spent > 1000:
        #     print("Warning: time spent is too long")

        return time_spent

    clicks_dict_list = df["Answer.clicks"].apply(lambda x: json.loads(x)["clicks"])

    decision_time = clicks_dict_list.apply(calculate_time_spent)

    return decision_time
