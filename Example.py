import pandas
import webbrowser
import os
from Functions import *
from Reports import *
from MainMenu import *
from datetime import datetime

overview_file = os.getcwd()+"/Data/overview.csv"
people_file = os.getcwd()+"/Data/people.csv"
roles_file = os.getcwd()+"/Data/roles.csv"
shift_file = os.getcwd()+"/Data/shift.csv"
transactions_file = os.getcwd()+"/Data/transactions.csv"

MainMenu(overview_file, people_file, roles_file, shift_file, transactions_file).mainloop()

