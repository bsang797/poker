import pandas as pd
from datetime import datetime
import os
import csv

class Reconciliation:

    def __init__(self, transactions, shifts, people):
        self.transaction = transactions
        self.shift = shifts
        self.people = people

    def chips_purchased(self):
        transaction_is_chip = self.transaction[self.transaction["chip_purchase"] == 1]
        chip_purchase_byid = transaction_is_chip.groupby(["session_id"])["quantity"].agg("sum")
        return chip_purchase_byid

    def chips_cashed(self):
        transaction_not_chip = self.transaction[self.transaction["chip_purchase"] == 0]
        chip_cashed_bydate = transaction_not_chip.groupby(["session_id"])["quantity"].agg("sum")
        return chip_cashed_bydate

    def debt_outstanding_by_player(self):
        transaction_credit = self.transaction[self.transaction["transaction_type"] == "credit"]
        debt_outstanding = transaction_credit.groupby(["person_id"])["quantity"].agg("sum")
        return debt_outstanding

    def total_rake(self):
        end_float = self.shift.groupby(["session_id"])["end_float"].agg("sum")
        start_float = self.shift.groupby(["session_id"])["start_float"].agg("sum")
        return end_float - start_float

    def total_tips(self):
        tips = self.shift.groupby(["session_id"])["tips"].agg("sum")
        return tips

class FinancialReport:

    def __init__(self, overview, transactions, roles, shifts):
        self.overview = overview
        self.transactions = transactions
        self.roles = roles
        self.shifts = shifts

    def total_revenue(self): # would I want to group by gameday ID here?
        rake_collected = self.overview.groupby(["session_id"])["rake_collected"].agg("sum")
        tips_collected = self.overview.groupby(["session_id"])["tips_collected"].agg("sum")
        return rake_collected + tips_collected

    def revenue_breakdown(self): # % tips per rake
        rake_collected = self.overview.groupby(["session_id"])["rake_collected"].agg("sum")
        tips_collected = self.overview.groupby(["session_id"])["tips_collected"].agg("sum")
        return (tips_collected/rake_collected)*100

    def revenue_per_employee(self):
        rake_collected = self.overview.groupby(["session_id"])["rake_collected"].agg("sum")
        tips_collected = self.overview.groupby(["session_id"])["tips_collected"].agg("sum")
        employees = self.roles.groupby("role")["person_id"].nunique()
        return self.total_revenue()/employees["Dealer"]

    def debt_outstanding(self):
        chip_purchase = self.transactions[self.transactions["chip_purchase"] == 1]
        return (chip_purchase.groupby(["transaction_type"])["quantity"].agg("sum"))["credit"]

    def debt_float_ratio(self):
        end_float = self.shifts.groupby(["datetime"])["end_float"].agg("sum")
        chip_purchase = self.transactions[self.transactions["chip_purchase"] == 1]
        return (chip_purchase/end_float)*100

    def debt_float_ratio(self):
        return self.debt_outstanding()/self.total_revenue()

    def avg_debt_per_player(self):
        players = self.roles.groupby("role")["person_id"].nunique()
        return self.debt_outstanding()/players["Player"]

    def avg_age_of_debt(self):
        avg_age = 0
        age_of_debt = self.transactions[(self.transactions["transaction_type"] == "credit") &
                                        (self.transactions["chip_purchase"] == 1)]
        for i in age_of_debt["datetime"]:
            time_diff = (datetime.today() - datetime.strptime(i, "%Y-%m-%d"))
            avg_age = avg_age + time_diff.days

        return avg_age/len(age_of_debt)

class DealerReport:

    def __init__(self, shifts):
        self.shifts = shifts

    def rake_tips_over_time(self):
        self.shifts["end_float"].astype(float)
        self.shifts["start_float"].astype(float)
        self.shifts["rake"] = self.shifts["end_float"] - self.shifts["start_float"]
        return self.shifts.groupby(["person_id"])["rake"].agg("sum").reset_index(name="rake")

    def shifts_over_time(self):
        self.shifts["shifts"] = self.shifts.groupby(["person_id"]).agg('size')
        return self.shifts.groupby(["person_id"])["shifts"].size().reset_index(name="shifts")

    def avg_rake_per_shift(self):
        self.shifts["avg_rake"] = self.rake_tips_over_time()["rake"]/self.shifts_over_time()["shifts"]
        return self.shifts.groupby(["person_id"])["avg_rake"].agg('sum').reset_index(name="avg_rake")

class PlayerReport:

    def __init__(self, transactions, roles):
        self.transactions = transactions
        self.roles = roles

    def buy_in_over_time(self):
        buy_in = self.transactions[self.transactions["quantity"] > 0]
        return buy_in.groupby(["person_id"])["quantity"].agg("sum").reset_index(name="buy_in")

    # There are a few kinks here I need to figure out
    def average_buy_in(self):
        avg_buy_in = self.transactions[self.transactions["quantity"] > 0]
        return avg_buy_in.groupby("person_id")["quantity"].mean().reset_index(name="avg_buy_in")

    def debt_outstanding_over_time(self):
        chip_purchase = self.transactions[(self.transactions["chip_purchase"] == 1) & (self.transactions["transaction_type"] == "credit")]
        return chip_purchase.groupby(["person_id"])["quantity"].agg("sum").reset_index(name="debt")

    def cash_credit_preference(self):
        preference = self.transactions.groupby(["person_id", "transaction_type"]).size().reset_index(name="count")
        preference["preference"] = preference["transaction_type"].map(str) + '(' + preference["count"].map(str) + ')'
        return preference["preference"].groupby(preference["person_id"]).agg(["size", ", ".join])["join"]

    def gain_loss_over_time(self):
        return self.transactions.groupby(["person_id"])["quantity"].agg("sum").reset_index(name="gain/loss")