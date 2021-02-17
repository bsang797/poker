import pandas
import sys
import webbrowser
import os

from Functions import *
from Reports import Reconciliation as rec
from Reports import FinancialReport as fin
from Reports import DealerReport as deal
from Reports import PlayerReport as player

overview_file = os.getcwd()+"/data/overview.csv"
people_file = os.getcwd()+"/data/people.csv"
roles_file = os.getcwd()+"/data/roles.csv"
shift_file = os.getcwd()+"/data/shift.csv"
transactions_file = os.getcwd()+"/data/transactions.csv"

# === EOD Reconciliation HTML
def eodrec(session_id):

    rec_data = rec(data_exporter(transactions_file),
                   data_exporter(shift_file),
                   data_exporter(people_file))

    chips_purchased = rec_data.chips_purchased()
    chips_cashed = rec_data.chips_cashed()
    debt_outstanding = rec_data.debt_outstanding_by_player()
    total_rake = rec_data.total_rake()
    total_tips = rec_data.total_tips()
    chips_float = rec_data.chips_floating()

    chips_purchased = chips_purchased[chips_purchased["session_id"] == session_id]
    chips_cashed = chips_cashed[chips_cashed["session_id"] == session_id]

    debts = pd.merge(data_exporter(people_file),
                   debt_outstanding,
                   how="inner",
                   on="person_id").drop(["person_id",
                                         "phone_num",
                                         "email",
                                         "address"], axis=1)

    debt_byperson = [["Debts per Person", "Describes per person"]]
    j = 1
    for i in debts.iterrows():
        debt_byperson.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        debt_byperson[j] = [name, str(i[1]["quantity"])]
        j += 1

    html_table = [["header","End of Day Reconciliation"],
                  ["chips purchased", str(chips_purchased["chips_purchased"][0])],
                  ["chips cashed", str(chips_cashed["chips_cashed"][0])],
                  ["chips out on the tables", str(chips_float[1])],
                  ["debt outstanding", str(debt_outstanding.agg("sum"))],
                  ["total rake", str(total_rake[1])],
                  ["total tips", str(total_tips[1])]]

    for i in debt_byperson:
        html_table.append(i)

    webbrowser.open(html_temp_file_generator(html_table))


def financial_report():
    data = fin(data_exporter(overview_file), data_exporter(transactions_file),
               data_exporter(roles_file), data_exporter(shift_file))

    total_revenue = data.total_revenue()
    revenue_breakdown = data.revenue_breakdown()
    revenue_per_employee = data.revenue_per_employee()
    debt_outstanding = data.debt_outstanding()
    debt_float_ratio = data.debt_float_ratio()
    avg_debt_per_player = data.avg_debt_per_player()
    avg_age_of_debt = data.avg_age_of_debt()


    html_table = [["header","Financial Report"],
                  ["total revenue", str(total_revenue[1])],
                  ["revenue breakdown", str(revenue_breakdown[1])],
                  ["revenue per employee", str(revenue_per_employee[1])],
                  ["debt outstanding", str(debt_outstanding)],
                  ["debt to float ratio", str(debt_float_ratio[1])],
                  ["avg_debt_per_player", str(avg_debt_per_player)],
                  ["avg_age_of_debt", str(avg_age_of_debt)]]

    webbrowser.open(html_temp_file_generator(html_table))

def dealer_report():
    rake_tips_over_time = deal(data_exporter(shift_file)).rake_tips_over_time()
    total_shifts = deal(data_exporter(shift_file)).shifts_over_time()
    avg_rake = deal(data_exporter(shift_file)).avg_rake_per_shift()

    rake = pd.merge(data_exporter(people_file),
                     rake_tips_over_time,
                     how="inner",
                     on="person_id").drop(["person_id",
                                           "phone_num",
                                           "email",
                                           "address"], axis=1)

    rake_html = [["header", "Dealer Report"]]
    j = 1
    for i in rake.iterrows():
        rake_html.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        rake_html[j] = [name, str(i[1]["rake"])]
        j += 1

    shifts = pd.merge(data_exporter(people_file),
                      total_shifts,
                      how="inner",
                      on="person_id").drop(["person_id",
                                            "phone_num",
                                            "email",
                                            "address"], axis=1)

    shifts_html = [["header", "Number of shifts by Dealer"]]
    j = 1
    for i in shifts.iterrows():
        shifts_html.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        shifts_html[j] = [name, str(i[1]["shifts"])]
        j += 1

    rakes = pd.merge(data_exporter(people_file),
                      avg_rake,
                      how="inner",
                      on="person_id").drop(["person_id",
                                            "phone_num",
                                            "email",
                                            "address"], axis=1)

    html_file = [["header", "Average rake per shift by Dealer"]]
    j = 1
    for i in rakes.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["avg_rake"])]
        j += 1

    for i in rake_html:
        html_file.append(i)

    for i in shifts_html:
        html_file.append(i)
    webbrowser.open(html_temp_file_generator(html_file))
dealer_report()

def player_buy_in(person_id):
    total_buy_in = player(data_exporter(transactions_file), data_exporter(shift_file)).buy_in_over_time()
    total_buy_in = total_buy_in[total_buy_in["person_id"] == person_id]
    buy_in = pd.merge(data_exporter(people_file),
                     total_buy_in,
                     how="inner",
                     on="person_id").drop(["person_id",
                                           "phone_num",
                                           "email",
                                           "address"], axis=1)

    html_file = [["header", "Total buy in from players"]]
    j = 1
    for i in buy_in.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["buy_in"])]
        j += 1
    return html_file

def avg_player_buy_in(person_id):
    tot_avg_buy_in = player(data_exporter(transactions_file), data_exporter(shift_file)).average_buy_in()
    tot_avg_buy_in = tot_avg_buy_in[tot_avg_buy_in["person_id"] == person_id]
    buy_in = pd.merge(data_exporter(people_file),
                     tot_avg_buy_in,
                     how="inner",
                     on="person_id").drop(["person_id",
                                           "phone_num",
                                           "email",
                                           "address"], axis=1)

    html_file = [["header", "Average player buy in"]]
    j = 1
    for i in buy_in.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["avg_buy_in"])]
        j += 1
    return html_file

def player_debt_outstanding(person_id):
    debt_outstanding_over_time = player(data_exporter(transactions_file),
                                                     data_exporter(shift_file)).debt_outstanding_over_time()
    debt_outstanding_over_time = debt_outstanding_over_time[debt_outstanding_over_time["person_id"] == person_id]
    if len(debt_outstanding_over_time) == 0:
        html_file = [["header", "No outstanding debt"]]
    else:
        debt = pd.merge(data_exporter(people_file),
                        debt_outstanding_over_time,
                        how="inner",
                        on="person_id").drop(["person_id",
                                            "phone_num",
                                            "email",
                                            "address"], axis=1)

        html_file = [["header", "Debt outstanding over time by player"]]
        j = 1
        for i in debt.iterrows():
            html_file.append([])
            name = i[1]["first_name"] + " " + i[1]["last_name"]
            html_file[j] = [name, str(i[1]["debt"])]
            j += 1
    return html_file

def player_payment_preference(person_id):
    cash_credit_preference = player(data_exporter(transactions_file), data_exporter(shift_file)).cash_credit_preference()
    d = {"person_id":[person_id], "cc_preference":cash_credit_preference[person_id]}
    preference_data = pd.DataFrame(data=d)
    preference = pd.merge(data_exporter(people_file),
                    preference_data,
                    how="inner",
                    on="person_id").drop(["person_id",
                                          "phone_num",
                                          "email",
                                          "address"], axis=1)
    html_file = [["header", "Player payment preference"]]
    j = 1
    for i in preference.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["cc_preference"])]
        j += 1
    return html_file


def player_gain_loss(person_id):
    gain_loss_over_time = player(data_exporter(transactions_file),
                                                 data_exporter(shift_file)).gain_loss_over_time()
    gain_loss_over_time = gain_loss_over_time[gain_loss_over_time["person_id"] == person_id]
    gain_loss = pd.merge(data_exporter(people_file),
                    gain_loss_over_time,
                    how="inner",
                    on="person_id").drop(["person_id",
                                          "phone_num",
                                          "email",
                                          "address"], axis=1)

    html_file = [["header", "Player gain/loss over time"]]
    j = 1
    for i in gain_loss.iterrows():
        html_file.append([])
        name = i[1]["first_name"] + " " + i[1]["last_name"]
        html_file[j] = [name, str(i[1]["gain/loss"])]
        j += 1
    return html_file

def player_report(person_id):
    data = [player_buy_in(person_id),avg_player_buy_in(person_id),
                      player_debt_outstanding(person_id), player_debt_outstanding(person_id),
                      player_gain_loss(person_id)]
    html_file = [["header", "Player Report"]]

    for i in data:
        for j in i:
            html_file.append(j)

    webbrowser.open(html_temp_file_generator(html_file))