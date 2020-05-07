import requests
from requests.exceptions import HTTPError
import tkinter as tk
import pandas as pd
import re
import numpy as np
from date_manipulator import *
import graph_widget
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

time_series_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/'\
                    'csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
UID_ISO_FIPS_LookUp_Table = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'

time_series_death_url='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/'\
                        'csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
class UserEntry:
    def __init__(self):
        self.entry = {'CountryName':None}

class MainApp():
    def __init__(self, root):
        root.protocol("WM_DELETE_WINDOW", quit_me)
        root.title("Covid 19 Data")
        root.configure(bg='#2C3E50')
        root.resizable(False, False)

        self.graph_frame = tk.Frame(root, width=640, height=480)
        self.graph_frame.grid(column=0, row=0, rowspan=5)
        self.graph_frame.pack_propagate(False)

        response = test_response(time_series_url)

        if isinstance(response, str):
            error_label = tk.Label(self.graph_frame, text=response, wraplength=500)
            error_label.place(relx=0.5, rely=0.5, anchor='center')
            self.empty_widget = tk.Label(root, text = '  ', height=3, width=30)
            self.empty_widget.grid(column=1, row=0, columnspan = 2, sticky='N')
        else:   
            self.report1 = get_report(time_series_url)     
            self.look_up_table = get_report(UID_ISO_FIPS_LookUp_Table)

            data_graph = extract_data_to_graph('Singapore', self.report1, 'Country/Region')
            self.graph_figure = FigureCanvasTkAgg(data_graph, master=self.graph_frame)
            self.graph_figure.draw()

            self.toolbar = NavigationToolbar2Tk(self.graph_figure, self.graph_frame)
            self.toolbar.update()

            self.graph_widget = self.graph_figure.get_tk_widget()
            self.graph_widget.pack()
          
            latest_date = get_latest_date_from_report(self.report1)
            default_text = 'Total number of confirmed cases in {} is {}'.format('Singapore', get_total_cases(latest_date, 'Singapore', 'Country/Region'))
            self.display_text1 = tk.StringVar()
            self.display_text1.set(default_text)
            self.text_widget = tk.Label(root, textvariable=self.display_text1,font=(None, 15), wraplength=250, width=30)
            self.text_widget.grid(column=1, row=0, columnspan = 2, sticky="nsew")
            root.update()
        
        self.country_frame = tk.Frame(root,highlightbackground="black", highlightcolor="black", highlightthickness=1, bd=0)
        self.country_frame.grid(column=1, row=1, columnspan = 2, sticky="new")
        self.country_frame.grid_columnconfigure([0,1,2],weight=1)

        self.country_name_entry_title = tk.Label(self.country_frame, text='Find Country',font=(None, 15), anchor='center')
        self.country_name_entry_title.grid(columnspan=3, column=0,row=0,pady=(10,15))

        self.country_name_entry_label = tk.Label(self.country_frame, text='Country Name:')
        self.country_name_entry = tk.Entry(self.country_frame, relief="solid",width=30)   
        self.country_name_entry_label.grid(column=0, row=1, sticky='E')  
        self.country_name_entry.grid(column=1,row=1, columnspan=2)

        self.country_name_entry_label = tk.Label(self.country_frame, text='Country Type:')
        self.country_name_entry_label.grid(column=0, row=2, sticky='E')
        self.type_of_place = tk.StringVar()
        self.type_of_place.set('Country/Region')
        self.radiobutton1 = tk.Radiobutton(self.country_frame, text='Country', variable=self.type_of_place, value='Country/Region')
        self.radiobutton2 = tk.Radiobutton(self.country_frame, text='Province', variable=self.type_of_place, value='Province/State')
        self.radiobutton1.grid(column=1,row=2)
        self.radiobutton2.grid(column=2,row=2,sticky='W')

        self.userentry = UserEntry()
        self.submit_name = tk.Button(self.country_frame, text='find country', command=self.update_country_name)
        self.submit_name.grid(column=2,row=3, sticky='se',padx=(0,10),pady=(20,10))
    
    def update_country_name(self):

        latest_date = get_latest_date_from_report(self.report1)
        self.userentry.entry['CountryType']= self.type_of_place.get()
        self.userentry.entry['CountryName'] = self.country_name_entry.get()
        country_name = self.parse_country_name_input(self.country_name_entry.get(),self.type_of_place.get())

        if country_name != None:           
            self.graph_widget.destroy()
            self.toolbar.destroy()

            data_graph = extract_data_to_graph(country_name, self.report1, self.type_of_place.get())
            self.graph_figure = FigureCanvasTkAgg(data_graph, master=self.graph_frame)
            self.graph_figure.draw()

            self.toolbar = NavigationToolbar2Tk(self.graph_figure, self.graph_frame)
            self.toolbar.update()

            self.graph_widget = self.graph_figure.get_tk_widget()
            self.graph_widget.pack()

            new_text = 'Total number of confirmed cases in {} is {}'.format(country_name, 
                        get_total_cases(latest_date, country_name, self.type_of_place.get()))
        else:
            new_text = 'We could not find the country or province you are looking for.'
        
        self.display_text1.set(new_text)
    
    def parse_country_name_input(self, country_name, country_type):
        temp_func = decorator1(is_substring, country_name)
        reduced_series=self.report1[country_type][self.report1[country_type].apply(temp_func)]
        if len(set(reduced_series.values)) == 1:
            return reduced_series.values[0]


def test_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.ConnectionError as err:
        return f'Connection Error: {err}'
    except HTTPError as http_err:
        return f'HTTP error occurred: {http_err}'
    except Exception as err:
        raise

def get_report(url):
    # return pd.DataFrame object
    return pd.read_csv(url)

def is_substring(substring, string):
    if type(substring)==str and re.match(substring, string,re.I):
        return True
    else:
        return False

def decorator1(func, arg1):
    def new_func(arg):
        return func(arg, arg1)
    return new_func

def get_dataframe_of_value_in_unknown_column(identifier, report):
    temp_func = decorator1(is_substring, identifier)
    temp_matrix = report.applymap(str)
    boolean_matrix = temp_matrix.applymap(temp_func)
    return report.loc[boolean_matrix.any(axis=1)]

def get_dataframe_of_value_in_known_column(identifier, report, label):
    return report.loc[report[label]==identifier]
    '''
    # Identifier in the column label 
    for label in report.columns.values:
        if is_substring(sublabel, label): # Acceptable labels include Province_state, Province/State   
            for actual_value in report[label]:
                if is_substring(identifier, actual_value):
                    dataframeobject = report.loc[report[label]==actual_value]
                    return dataframeobject
    '''
def get_country_data(country, report, label):
    #Assuming there is only one column name with the word "country"
    return get_dataframe_of_value_in_known_column(country, report, label)

def get_daily_no_of_cases(date, country, province = None):
    # data available from 1/23/20 onwards
    # date in MM/DD/YY format
    previous_date = get_previous_date(date, '%m/%d/%y')
    previous_date = parse_date(previous_date, '%m/%d/%y', '%#m/%#d/%y')
    return get_total_cases(date, country, province)- get_total_cases(previous_date, country, province)

def get_total_cases(date, country, country_type):
    # data available from 1/22/20 onwards
    # date: MM/DD/YY, (03/05/20 not accepted, only 3/5/20)
    # Get province data, else get total confirmed cases in country
    report = get_report(time_series_url)
    dataframeobject = get_country_data(country, report, country_type)
    confirmed_cases = dataframeobject[date].sum()
    return confirmed_cases #integer

def get_series_from_report(country_report):
    # country_report: pandas dataframe object
    # slice and sum dataframe object from john hopkins data on covid 19, since actual data start from column 4
    return country_report.iloc[:,4:].sum()

def get_latest_date_from_report(report):
    if isinstance(report, pd.core.series.Series):
        return report.last_valid_index()
    elif isinstance(report, pd.core.frame.DataFrame):
        return report.columns.values[-1]

def extract_data_to_graph(country, report, country_type):
    # returns a matplotlib Figure
    country_report = get_country_data(country, report, country_type)
    final_report = get_series_from_report(country_report)
    date_range_string = final_report.index
    date_range_np = get_range_of_dates(date_range_string)
    return graph_widget.main(date_range_np, final_report.to_numpy(), country)

def quit_me():
    root.quit()
    root.destroy()


root = tk.Tk()
app = MainApp(root)
root.mainloop()
'''
temp = [
    ['su',1,2,4,56,2],
    ['tu',3,-1,23,1,14],
    ['ve',10,23,12,199,10]
]
df1 = pd.DataFrame(temp)
temp2=df1.loc[df1.iloc[:,0].apply(lambda x: x.endswith('u'))]
print(df1.loc[df1.iloc[:,0].apply(lambda x: x.endswith('u'))])
temp3=df1[0][df1[0].apply(lambda x: x.endswith('g'))]
print(temp3.values)
'''