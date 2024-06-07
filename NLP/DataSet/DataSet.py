import json
import os
from datetime import datetime

import Search.Engine
from settings import db_connection

import json
import sys
import tkinter.filedialog
from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox as mb
from tkinter import ttk

import Utility.Labelling



db = db_connection.connection
def create(operations, keywords, file_path):
    tools = Search.Engine.search_tools(operations, keywords)
    results = {}
    for t in sorted(tools):
        t_data = db.execute(f"SELECT Name, Description FROM biotools_tools_info WHERE Biotools_id = '{t}'").fetchone()
        name = t_data[0]
        description = t_data[1]
        results[t] = {
            'Name': name,
            'Description': description
        }
        for keyword in keywords:
            if (keyword.islower() and keyword in description.lower()) or keyword in description:
                results[t][keyword] = True
            else:
                results[t][keyword] = False
    if file_path is not None:
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=4)
            print(f"Dataset written to {file_path}")
    else:
        print(json.dumps(results, indent=4))



#create(["sub(Analysis)"], ["parallel", "distributed", "gpu", "cpu", "RAM"], None)

def split(property, proportion, in_file_path, out_directory):
    try:
        proportion = float(proportion)
    except ValueError:
        print("Invalid Proportion given. Provide number between 0 and 1")
        sys.exit()
    data = None
    training_set = {}
    test_set = {}
    tools = {
        True: [],
        False: []
    }
    with open(in_file_path, 'r') as inf:
        data = json.load(inf)
    for key in data.keys():
        if key == 'last_index':
            continue
        tools[data[key][property]].append(key)
    total_true = len(tools[True])
    total_false = len(tools[False])
    pos_training_length = int(round(total_true * proportion))
    pos_test_length = total_true - pos_training_length

    neg_training_length = int(round(total_false * proportion))
    neg_test_length = total_false - neg_training_length

    for i in range(0, pos_training_length):
        tool_id = tools[True][i]
        training_set[tool_id] = data[tool_id]
    for i in range(pos_training_length, pos_training_length + pos_test_length):
        tool_id = tools[True][i]
        test_set[tool_id] = data[tool_id]
    for i in range(0, neg_training_length):
        tool_id = tools[False][i]
        training_set[tool_id] = data[tool_id]
    for i in range(neg_training_length, neg_training_length + neg_test_length):
        tool_id = tools[False][i]
        test_set[tool_id] = data[tool_id]

    if not os.path.exists(out_directory):
        print(f"Can't save to directory '{out_directory}'. It does not exist.")
        sys.exit()
    today = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    training_set_path = os.path.join(out_directory, f"{today}_{property}_training_set.json")
    test_set_path = os.path.join(out_directory, f"{today}_{property}_test_set.json")
    with open(training_set_path, 'w') as f:
        json.dump(training_set, f, indent=4)
        print(f"Training set written to '{training_set_path}'")
    with open(test_set_path, 'w') as f:
        json.dump(test_set, f, indent=4)
        print(f"Test set written to '{test_set_path}")



# split('parallel', 0.75,"D:\\Priv\\repository\\BA-Code\\Data\\Datasets\\Labelled\\dataset_01_labelled.json", 'D:\\Priv\\repository\\BA-Code\\NLP\\DataSet')




class LabellingTool:
    def __init__(self, in_file_path, out_file_path):
        self.in_file_path = in_file_path
        self.out_file_path = out_file_path
        self.dataset = None
        self.tool_list = None
        self.root = None
        self.main_frame = None
        self.variables = None
        self.description_text = None

        self.read_dataset()
        self.initialize_window()
        self.init_vars()
        self.updateVariables()
        self.update_ui()
        self.setup_keybinds()
        self.root.mainloop()
        self.last_labelled = 0

    def save(self, *event):
        self.update_dataset()
        self.dataset['last_index'] = self.last_labelled
        with open(self.out_file_path, 'w') as f:
            json.dump(self.dataset, f, indent=4)
            print("File saved")

    def update_dataset(self):
        active_tool = self.tool_list[self.last_labelled]
        for key in self.variables['Props']:
            self.dataset[active_tool][key] = self.variables['Props'][key].get()


    def get_kw_index(self, word):
        start = '1.0'
        while True:
            start_index = self.description_text.search(word, start, nocase=True, stopindex=END)
            if not start_index:
                break
            end_index = '%s+%dc' % (start_index, len(word))
            self.description_text.tag_add('kw', start_index, end_index)
            start = end_index

    def updateVariables(self):
        active_tool = self.tool_list[self.last_labelled]
        tool = self.dataset[active_tool]
        self.variables['ID'].set(active_tool)
        self.variables['Description'].set(tool['Description'])
        self.variables['cur_tot'].set(f"{self.last_labelled + 1}/{len(self.tool_list)}")
        for key in self.variables['Props']:
            self.variables['Props'][key].set(tool[key] if key in tool.keys() else False)

    def getNextTool(self, *event):
        self.update_dataset()
        if self.last_labelled < len(self.tool_list) - 1:
            self.last_labelled += 1
            self.updateVariables()
            self.update_ui()

    def getPreviousTool(self, *event):
        self.update_dataset()
        if self.last_labelled > 0:
            self.last_labelled -= 1
            self.updateVariables()
            self.update_ui()
    def setup_keybinds(self):
        self.root.bind('<Up>', self.scroll_up)
        self.root.bind('<Down>', self.scroll_down)
        self.root.bind('<Right>', self.getNextTool)
        self.root.bind('<Left>', self.getPreviousTool)
        self.root.bind('<Control-s>', self.save)

    def scroll_down(self, *args):
        self.description_text.yview_scroll(5, "units")

    def scroll_up(self, *args):
        self.description_text.yview_scroll(-5, "units")

    def toggle_var(self, event):
        index = int(event.keysym)
        if index == 0:
            index = 10
        key = list(self.variables['Props'].keys())[index-1]
        if key not in self.variables['Props'].keys():
            print(f"No variable found with key '{key}'")
            return
        self.variables['Props'][key].set(False if self.variables['Props'][key].get() else True)

    def read_dataset(self):
        with open(self.in_file_path, 'r') as f:
            self.dataset = json.load(f)
        self.last_labelled = 0
        if 'last_index' in self.dataset.keys():
            self.last_labelled = self.dataset['last_index']
            del self.dataset['last_index']
        self.tool_list = list(self.dataset.keys())
        if self.last_labelled >= len(self.tool_list):
            self.last_labelled = len(self.tool_list) - 1

    def init_vars(self):
        self.variables = {'ID': StringVar(), 'Description': StringVar(), 'Name': StringVar(), 'Props': {}, 'cur_tot': StringVar()}
        sub_keys = []
        for key in self.dataset.keys():
            if key == 'Meta':
                continue
            sub_keys += self.dataset[key].keys()
        sub_keys = sorted(list(set(sub_keys)))
        for sub_key in sub_keys:
            if sub_key not in ['Description', 'Name']:
                self.variables['Props'][sub_key] = BooleanVar()

    def initialize_window(self):
        self.root = Tk()
        self.root.title('Labelling Tool')
        self.root.geometry('1200x500')

    def update_ui(self):
        self.main_frame = ttk.Frame(self.root, padding="3 3 12 12")
        self.main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        ttk.Label(self.main_frame, text='ID:').grid(column=0, row=0, sticky=W)
        ttk.Label(self.main_frame, textvariable=self.variables['ID']).grid(column=1, row=0, sticky=W)
        ttk.Label(self.main_frame, text='Description:').grid(column=0, row=1, sticky=W)
        self.description_text = scrolledtext.ScrolledText(self.main_frame, height=20, width=100)
        self.description_text.insert('1.0', Utility.Labelling.insert_newLines(self.variables['Description'].get()))
        self.description_text.grid(column=1, row=1, rowspan=20)
        self.description_text.config(state=DISABLED)
        last_prop = 1
        last_row = 1
        last_col = 3
        for key in self.variables['Props'].keys():
            if last_row == 6:
                last_col += 1
                last_row = 1
            ttk.Checkbutton(self.main_frame, variable=self.variables['Props'][key], text=f"{last_prop} - {key}").grid(column=last_col, row=last_row, sticky=(N,W))
            if last_prop <= 10:
                if last_prop == 10:
                    self.root.bind('0', self.toggle_var)
                else:
                    self.root.bind(str(last_prop), self.toggle_var)
            last_row += 1
            last_prop += 1
            self.get_kw_index(key)
        self.description_text.tag_config('kw', foreground='black', background='lightgray')
        ttk.Label(self.main_frame, textvariable=self.variables['cur_tot']).grid(column=0, row=5)
        ttk.Button(self.main_frame, text='Previous', command=self.getPreviousTool).grid(column=3, row=25, sticky=(N, W))
        ttk.Button(self.main_frame, text='Next', command=self.getNextTool).grid(column=4, row=25, sticky=(N,W))
        ttk.Button(self.main_frame, text='Save', command=self.save).grid(column=4, row=26, sticky=(N,W))
        ttk.Label(self.main_frame, text=self.in_file_path).grid(column=1, row=26)




#LabellingTool('test.json', 'test.json')