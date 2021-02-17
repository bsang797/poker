from tkinter import *
import tkinter.font as font
from tkinter import ttk
from Functions import *
from Reports import Reconciliation as rec
from datetime import datetime

class MainMenu:
    def __init__(self, overview_file, people_file, roles_file, shift_file, transactions_file):
        self.root = Tk()
        self.root.resizable(False, False)
        self.session_id = data_exporter(transactions_file)['session_id'].max() + 1

        self.font_style = "Helvetica"
        self.button_fontsize = 20
        self.label_fontsize = 20
        self.option_menu_width = 18
        self.bg_color = "#F0F0F0"

        self.overview_file = overview_file
        self.people_file = people_file
        self.roles_file = roles_file
        self.shift_file = shift_file
        self.transactions_file = transactions_file

    def mainloop(self):
        self.main_menu_frames()
        self.root.mainloop()

    def main_menu_frames(self):
        self.load_ppl_data()
        self.load_chip_data()
        self.load_debt_data()
        self.buttons()
        self.tabs()
        self.chip_labels()
        self.debt_labels()
        self.root.title("Poker Accounting System")

    def load_ppl_data(self):
        ppl = data_exporter(self.people_file)[['person_id', 'first_name', 'last_name']]
        role = data_exporter(self.roles_file)
        ppl_roles = pd.merge(ppl, role, how="inner", on="person_id")

        self.owners = []
        self.dealers = []
        self.players = []
        self.ppl_id = pd.DataFrame(columns=["person_id", "name"])

        for i in ppl_roles.iterrows():
            if i[1]['role'] == 'Player':
                self.players.append(i[1]['first_name'] + " " + i[1]['last_name'])
            if i[1]['role'] == 'Owner':
                self.owners.append(i[1]['first_name'] + " " + i[1]['last_name'])
            if i[1]['role'] == 'Dealer':
                self.dealers.append(i[1]['first_name'] + " " + i[1]['last_name'])

        for i in ppl.iterrows():
            self.ppl_id = self.ppl_id.append({"person_id": i[1]['person_id'],
                                              "name": i[1]['first_name'] + " " + i[1]['last_name']},
                                             ignore_index=TRUE)

    def load_chip_data(self):
        self.reconciliation_data = rec(
            data_exporter(self.transactions_file),
            data_exporter(self.shift_file),
            data_exporter(self.people_file))

        chips_purchased_series = self.reconciliation_data.chips_purchased()
        chips_cashed_series = self.reconciliation_data.chips_cashed()
        total_rake_series = self.reconciliation_data.total_rake()
        total_tips_series = self.reconciliation_data.total_tips()
        debt_outstanding_series = self.reconciliation_data.debt_outstanding_by_player()

        try:
            self.chips_purchased = chips_purchased_series[self.session_id]
        except KeyError:
            self.chips_purchased = 0

        try:
            self.chips_cashed = -chips_cashed_series[self.session_id]
        except KeyError:
            self.chips_cashed = 0

        try:
            self.total_rake = total_rake_series[self.session_id]
        except KeyError:
            self.total_rake = 0

        try:
            self.total_tips = total_tips_series[self.session_id]
        except KeyError:
            self.total_tips = 0

        try:
            self.chips_float = self.chips_purchased - self.chips_cashed - (self.total_rake + self.total_tips)
        except KeyError:
            self.chips_float = 0

        self.total_debt = debt_outstanding_series.agg('sum')

    def load_debt_data(self):
        debt_outstanding_series = self.reconciliation_data.debt_outstanding_by_player()
        debts = pd.merge(data_exporter(self.people_file),
                         debt_outstanding_series,
                         how="inner",
                         on="person_id").drop(["person_id",
                                               "phone_num",
                                               "email",
                                               "address"], axis=1)
        self.debt_byperson = []
        j = 0
        for i in debts.iterrows():
            if i[1]["quantity"] != 0:
                self.debt_byperson.append([])
                name = i[1]["first_name"] + " " + i[1]["last_name"]
                self.debt_byperson[j] = [name, str(i[1]["quantity"])]
                j += 1
        self.debt_byperson.sort(key=lambda x: x[0])

    def buttons(self):
        self.buttons_frame = Frame(self.root)
        self.buttons_frame.grid(row=0, column=2, rowspan=6)

        buying_in_button = Button(self.buttons_frame, width=15, text="Buying In",
                                  command=self.buyin_button)
        cashing_out_button = Button(self.buttons_frame, width=15, text="Cashing Out",
                                    command=self.cashout_button)
        debt_button = Button(self.buttons_frame, width=15, text="Debt Repayment",
                             command=self.debt_button)
        shift_button = Button(self.buttons_frame, width=15, text="End of Shift",
                              command=self.shift_button)
        report_button = Button(self.buttons_frame, width=15, text="Create Report",
                               command=self.report_button)
        quit_button = Button(self.buttons_frame, width=10, text="Quit",
                             command=self.root.destroy)

        self.format_buttons([buying_in_button, cashing_out_button, debt_button,
                             shift_button, report_button, quit_button])

    def format_buttons(self, buttons):
        i = 0
        for button in buttons:
            button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
            button.grid(row=i, column=2)
            i += 1

    def tabs(self):
        self.tab_parent = ttk.Notebook(self.root)
        self.chip_tab = ttk.Frame(self.tab_parent)
        self.debt_tab = ttk.Frame(self.tab_parent)

        self.tab_parent.add(self.chip_tab, text="Overview")
        self.tab_parent.add(self.debt_tab, text="Outstanding Debts")

        self.tab_parent.grid(row=0, column=0, sticky="nw", rowspan=6, columnspan=2)

    def debt_labels(self):
        v = Scrollbar(self.debt_tab)
        v.pack(side=RIGHT, fill=Y)

        t = Text(self.debt_tab, width=0, height=8, wrap=NONE, yscrollcommand=v.set)
        t['font'] = font.Font(family=self.font_style, size=self.button_fontsize)

        for i in self.debt_byperson:
            t.insert(END, i[0] + ": " + i[1] + "\n")
        t.pack(side=TOP, fill=X)
        v.config(command=t.yview)

    def chip_labels(self):
        description = Label(self.chip_tab, text="Description", bg=self.bg_color)
        amount = Label(self.chip_tab, text="Amount", bg=self.bg_color)

        desc_purchased = Label(self.chip_tab, text="Chips Purchased", bg=self.bg_color)
        purchased_amt = Label(self.chip_tab, text=self.chips_purchased, bg=self.bg_color)

        desc_cashed = Label(self.chip_tab, text="Chips Cashed Out", bg=self.bg_color)
        cashed_amt = Label(self.chip_tab, text=self.chips_cashed, bg=self.bg_color)

        desc_float = Label(self.chip_tab, text="Chips in Play", bg=self.bg_color)
        float_amt = Label(self.chip_tab, text=self.chips_float, bg=self.bg_color)

        desc_rake = Label(self.chip_tab, text="Rake Collected", bg=self.bg_color)
        rake_amt = Label(self.chip_tab, text=self.total_rake, bg=self.bg_color)

        desc_tips = Label(self.chip_tab, text="Tips Collected", bg=self.bg_color)
        tips_amt = Label(self.chip_tab, text=self.total_tips, bg=self.bg_color)

        desc_debt = Label(self.chip_tab, text="Total Debt", bg=self.bg_color)
        debt_amt = Label(self.chip_tab, text=self.total_debt, bg=self.bg_color)

        self.format_chip_labels([[description, amount],
                                 [desc_purchased, purchased_amt],
                                 [desc_cashed, cashed_amt],
                                 [desc_float, float_amt],
                                 [desc_rake, rake_amt],
                                 [desc_tips, tips_amt],
                                 [desc_debt, debt_amt]])

    def format_chip_labels(self, labels):
        i = 0
        for pair in labels:
            for label in pair:
                label['font'] = font.Font(family=self.font_style, size=self.label_fontsize)
            pair[0].grid(row=i, column=0, sticky="nw")
            pair[1].grid(row=i, column=1, sticky="nw")
            i += 1

    def buyin_button(self):
        self.transaction_id = data_exporter(self.transactions_file)['transaction_id'].max() + 1
        self.date_time = datetime.now()
        self.chip_purchase = 1
        self.root.title("Buy-In Transaction")

        self.buttons_frame.destroy()
        self.tab_parent.destroy()

        # === Create Frame
        self.buyin_frame = Frame(self.root)
        self.buyin_frame.grid()

        # === Email
        player_label = Label(self.buyin_frame, text="Player")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.buyin_frame)
        player_dropdown = OptionMenu(self.buyin_frame, self.player_var, *self.players)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Transaction Type Entry
        type_label = Label(self.buyin_frame, text="Transaction Type")
        type_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        type_label.grid(row=1, column=0, sticky="w")

        self.trans_type_var = StringVar(self.buyin_frame)
        type_dropdown = OptionMenu(self.buyin_frame, self.trans_type_var, "cash", "credit")
        type_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        type_dropdown.config(width=self.option_menu_width)
        type_dropdown.grid(row=1, column=1)

        # === Quantity
        quant_label = Label(self.buyin_frame, text="Quantity of Chips")
        quant_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quant_label.grid(row=2, column=0, sticky="w")

        self.quant_ent = Entry(self.buyin_frame)
        self.quant_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.quant_ent.grid(row=2, column=1)

        # === Email
        email_label = Label(self.buyin_frame, text="E-Transfer Recipient")
        email_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_label.grid(row=3, column=0, sticky="w")

        self.email_var = StringVar(self.buyin_frame)
        email_dropdown = OptionMenu(self.buyin_frame, self.email_var, "", *self.owners)
        email_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_dropdown.config(width=self.option_menu_width)
        email_dropdown.grid(row=3, column=1)

        confirm_button = Button(self.buyin_frame, text="Confirm", command=self.buyin_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        exit_button = Button(self.buyin_frame, text="Quit", command = self.buyin_quit)
        exit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        exit_button.grid(row=4, column=1, sticky="e")

    def buyin_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]
        if self.email_var.get() != "":
            email_player_id = self.ppl_id[self.ppl_id['name'] == self.email_var.get()]['person_id'].values[0]
        else:
            email_player_id = ""
        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date_time,
                                                    self.trans_type_var.get(),
                                                    self.quant_ent.get(),
                                                    email_player_id,
                                                    self.chip_purchase])

        if self.email_var.get() != "":

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date_time,
                                                        "cash",
                                                        -int(self.quant_ent.get()),
                                                        "",
                                                        0])
            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date_time,
                                                        "credit",
                                                        int(self.quant_ent.get()),
                                                        "",
                                                        0])

        self.buyin_frame.destroy()
        self.main_menu_frames()

    def buyin_quit(self):
        self.buyin_frame.destroy()
        self.main_menu_frames()

    def cashout_button(self):
        self.transaction_id = data_exporter(self.transactions_file)['transaction_id'].max() + 1
        self.date_time = datetime.now()
        self.chip_purchase = 0
        self.root.title("Cash-Out Transaction")

        self.buttons_frame.destroy()
        self.tab_parent.destroy()

        # === Create Frame
        self.cashout_frame = Frame(self.root)
        self.cashout_frame.grid()

        # === Email
        player_label = Label(self.cashout_frame, text="Player")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.cashout_frame)
        player_dropdown = OptionMenu(self.cashout_frame, self.player_var, *self.players)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Quantity
        quant_label = Label(self.cashout_frame, text="Quantity of Chips")
        quant_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quant_label.grid(row=2, column=0, sticky="w")

        self.quant_ent = Entry(self.cashout_frame)
        self.quant_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.quant_ent.grid(row=2, column=1)

        # === Email
        email_label = Label(self.cashout_frame, text="E-Transfer Sender")
        email_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_label.grid(row=3, column=0, sticky="w")

        self.email_var = StringVar(self.cashout_frame)
        email_dropdown = OptionMenu(self.cashout_frame, self.email_var, "", *self.owners)
        email_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_dropdown.config(width=self.option_menu_width)
        email_dropdown.grid(row=3, column=1)

        confirm_button = Button(self.cashout_frame, text="Confirm", command=self.cashout_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        quit_button = Button(self.cashout_frame, text="Quit", command = self.cashout_quit)
        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.grid(row=4, column=1, sticky="e")

    def cashout_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]
        if self.email_var.get() != "":
            email_player_id = self.ppl_id[self.ppl_id['name'] == self.email_var.get()]['person_id'].values[0]
        else:
            email_player_id = ""

        print("hi")

        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date_time,
                                                    "cash",
                                                    -int(self.quant_ent.get()),
                                                    email_player_id,
                                                    self.chip_purchase])

        if self.email_var.get() != "":

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date_time,
                                                        "cash",
                                                        int(self.quant_ent.get()),
                                                        "",
                                                        self.chip_purchase])

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date_time,
                                                        "credit",
                                                        -int(self.quant_ent.get()),
                                                        "",
                                                        0])

        self.cashout_frame.destroy()
        self.main_menu_frames()

    def cashout_quit(self):
        self.cashout_frame.destroy()
        self.main_menu_frames()

    def debt_button(self):
        self.transaction_id = data_exporter(self.transactions_file)['transaction_id'].max() + 1
        self.date_time = datetime.now()
        self.chip_purchase = 0
        self.root.title("Debt Repayment")

        self.buttons_frame.destroy()
        self.tab_parent.destroy()

        # === Create Frame
        self.debt_frame = Frame(self.root)
        self.debt_frame.grid()

        # === Player
        player_label = Label(self.debt_frame, text="Player")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.debt_frame)
        player_dropdown = OptionMenu(self.debt_frame, self.player_var, *self.players)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Quantity
        quant_label = Label(self.debt_frame, text="Quantity of Chips")
        quant_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quant_label.grid(row=2, column=0, sticky="w")

        self.quant_ent = Entry(self.debt_frame)
        self.quant_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.quant_ent.grid(row=2, column=1)

        # === Email
        email_label = Label(self.debt_frame, text="E-Transfer Recipient")
        email_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_label.grid(row=3, column=0, sticky="w")

        self.email_var = StringVar(self.debt_frame)
        email_dropdown = OptionMenu(self.debt_frame, self.email_var, "", *self.owners)
        email_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        email_dropdown.config(width=self.option_menu_width)
        email_dropdown.grid(row=3, column=1)

        confirm_button = Button(self.debt_frame, text="Confirm", command=self.debt_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        quit_button = Button(self.debt_frame, text="Quit", command = self.debt_quit)
        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.grid(row=4, column=1, sticky="e")

    def debt_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]
        if self.email_var.get() != "":
            email_player_id = self.ppl_id[self.ppl_id['name'] == self.email_var.get()]['person_id'].values[0]
        else:
            email_player_id = ""

        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date_time,
                                                    "cash",
                                                    int(self.quant_ent.get()),
                                                    email_player_id,
                                                    self.chip_purchase])

        append_list_as_row(self.transactions_file, [player_id,
                                                    self.transaction_id,
                                                    self.session_id,
                                                    self.date_time,
                                                    "credit",
                                                    -int(self.quant_ent.get()),
                                                    "",
                                                    self.chip_purchase])

        if self.email_var.get() != "":
            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date_time,
                                                        "cash",
                                                        -int(self.quant_ent.get()),
                                                        "",
                                                        0])

            append_list_as_row(self.transactions_file, [email_player_id,
                                                        self.transaction_id,
                                                        self.session_id,
                                                        self.date_time,
                                                        "credit",
                                                        int(self.quant_ent.get()),
                                                        "",
                                                        0])


        self.debt_frame.destroy()
        self.main_menu_frames()

    def debt_quit(self):
        self.debt_frame.destroy()
        self.main_menu_frames()

    def shift_button(self):
        self.shift_id = data_exporter(self.shift_file)['shift_id'].max() + 1
        self.date_time = datetime.now()
        self.root.title("Shift Reconciliation")

        self.buttons_frame.destroy()
        self.tab_parent.destroy()

        # === Create Frame
        self.shift_frame = Frame(self.root)
        self.shift_frame.grid()

        # === Dealer
        player_label = Label(self.shift_frame, text="Dealer")
        player_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_label.grid(row=0, column=0, sticky="w")

        self.player_var = StringVar(self.shift_frame)
        player_dropdown = OptionMenu(self.shift_frame, self.player_var, *self.dealers)
        player_dropdown['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_dropdown.config(width=self.option_menu_width)
        player_dropdown.grid(row=0, column=1)

        # === Starting Float
        start_label = Label(self.shift_frame, text="Starting Float")
        start_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        start_label.grid(row=1, column=0, sticky="w")

        self.start_ent = Entry(self.shift_frame)
        self.start_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.start_ent.insert(END, "1000")
        self.start_ent.grid(row=1, column=1)

        # === Ending Float
        end_label = Label(self.shift_frame, text="Ending Float")
        end_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        end_label.grid(row=2, column=0, sticky="w")

        self.end_ent = Entry(self.shift_frame)
        self.end_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.end_ent.grid(row=2, column=1)

        # === Tips Collected
        tips_label = Label(self.shift_frame, text="Tips Collected")
        tips_label['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        tips_label.grid(row=3, column=0, sticky="w")

        self.tips_ent = Entry(self.shift_frame)
        self.tips_ent['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        self.tips_ent.grid(row=3, column=1)

        confirm_button = Button(self.shift_frame, text="Confirm", command=self.shift_confirm)
        confirm_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        confirm_button.grid(row=4, column=1, sticky="w")

        quit_button = Button(self.shift_frame, text="Quit", command = self.shift_quit)
        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.grid(row=4, column=1, sticky="e")

    def shift_confirm(self):
        player_id = self.ppl_id[self.ppl_id['name'] == self.player_var.get()]['person_id'].values[0]

        append_list_as_row(self.shift_file, [player_id,
                                             self.shift_id,
                                             self.session_id,
                                             self.date_time,
                                             self.start_ent.get(),
                                             self.end_ent.get(),
                                             self.tips_ent.get()])

        self.shift_frame.destroy()
        self.main_menu_frames()

    def shift_quit(self):
        self.shift_frame.destroy()
        self.main_menu_frames()

    def report_button(self):
        self.buttons_frame.destroy()
        self.tab_parent.destroy()
        self.root.title("Reports")

        self.report_frame = Frame(self.root)
        self.report_frame.grid()

        fin_button = Button(self.report_frame, text="Financial Report",
                            command=lambda: webbrowser.open(os.getcwd() + "/FINReport/FINReport.html"))
        fin_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        fin_button.config(width=self.option_menu_width)
        fin_button.grid(row=0)

        dealer_button = Button(self.report_frame, text="Dealer Report",
                            command=lambda: webbrowser.open(os.getcwd() + "/DealerReport/DealerReport.html"))
        dealer_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        dealer_button.config(width=self.option_menu_width)
        dealer_button.grid(row=1)

        player_button = Button(self.report_frame, text="Player Report",
                            command=lambda: webbrowser.open(os.getcwd() + "/PlayerReport/PlayerReport.html"))
        player_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        player_button.config(width=self.option_menu_width)
        player_button.grid(row=2)

        quit_button = Button(self.report_frame, text="Back", command=self.report_quit)
        quit_button['font'] = font.Font(family=self.font_style, size=self.button_fontsize)
        quit_button.config(width=int(self.option_menu_width/2))
        quit_button.grid(row=3)

    def report_quit(self):
        self.report_frame.destroy()
        self.main_menu_frames()