import pandas as pd
import os
import webbrowser
import csv

def data_exporter(file_directory):
    return pd.read_csv(file_directory)

def append_list_as_row(file_name, list_of_elem):
    if list_of_elem == []:
        quit()
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj)
        csv_writer.writerow(list_of_elem)

def html_temp_file_generator(nested_list):
    string = "<html><body>"
    header_num = 1
    for i in nested_list:
        if i[0] == "header":
            string += "<h" + str(header_num) + "> " + i[1] + " <h" + str(header_num) + ">"
            header_num += 1
        else:
            string += "<p> " + i[0] + ": " + i[1] + " <p>"
    string += "</body></html>"

    f = open("temp.html",'w')
    f.write(string)
    f.close()

    return "temp.html"