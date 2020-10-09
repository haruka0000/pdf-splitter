import sys
import os
import eel
import pandas as pd
from pdf_splitter import pdfSplitter
try:
    from tkinter import Tk, filedialog
except:
    from Tkinter import Tk, filedialog

global pdf_splitter
pdf_splitter = None
global split_progress
global input_path
global output_path

def onCloseWindow(page, sockets):
    print(page + 'が閉じられました。プログラムを終了します。')
    if pdf_splitter != None:
        pdf_splitter.clean_up()
    sys.exit()

@eel.expose
def get_file_path():
    global input_path
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    file_type   = [("PDF", "*.pdf")]
    init_dir    = os.path.abspath(os.path.dirname(__file__))
    file_name   = filedialog.askopenfilename(filetypes=file_type, initialdir=init_dir)
    if file_name == ():
        file_name = ""
    input_path  = file_name
    return file_name

@eel.expose
def get_dir_path():
    global output_path
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    init_dir    = os.path.abspath(os.path.dirname(__file__))
    folder_name = filedialog.askdirectory(initialdir=init_dir)
    if folder_name == ():
        folder_name = ""
    output_path = folder_name
    return folder_name

@eel.expose
def init_data():
    global pdf_splitter
    global split_progress
    split_progress  = 0 
    pdf_splitter    = pdfSplitter(input_path)


@eel.expose
def set_org_data():
    global pdf_splitter
    pdf_splitter.df = pdf_splitter.org_df

@eel.expose
def clear_data():
    global pdf_splitter
    columns = pdf_splitter.df.columns.tolist()
    pdf_splitter.df = pd.DataFrame([], columns=columns)

@eel.expose
def set_prefix(prefix):
    global pdf_splitter
    prefix      = str(prefix)
    prev_prefix = pdf_splitter.prefix
    columns     = pdf_splitter.df.columns.tolist()
    values      = pdf_splitter.df.values.tolist()

    if prev_prefix != "":
        values  = [ [prefix + v[0][len(prev_prefix):]] \
                    + v[1:] for v in values \
                    if v[0][:len(prev_prefix)] == prev_prefix]
    else:
        values  = [[prefix + v[0]] + v[1:] for v in values]
    pdf_splitter.df     = pd.DataFrame(values, columns=columns)
    pdf_splitter.prefix = prefix

@eel.expose
def update_data(data):
    global pdf_splitter
    columns = pdf_splitter.df.columns.tolist()
    data = [ d for d in data if d != [] and d != [""]*len(columns) ]
    pdf_splitter.df = pd.DataFrame(data[1:], columns=columns)
    pdf_splitter.df["from"][ pdf_splitter.df["from"]=="" ] = 1
    pdf_splitter.df["to"][ pdf_splitter.df["to"]=="" ] = len(pdf_splitter.num_pages)
    pdf_splitter.df["from"] = pdf_splitter.df["from"].astype(int)
    pdf_splitter.df["to"]   = pdf_splitter.df["to"].astype(int)
    pdf_splitter.df.sort_values(["from", "to"], inplace=True)
    pdf_splitter.df.reset_index(drop=True)
    print(pdf_splitter.df)


@eel.expose
def get_data():
    data    = [pdf_splitter.df.columns.tolist()] + pdf_splitter.df.values.tolist()
    return data

@eel.expose
def split_pdf():
    global split_progress
    for v in pdf_splitter.split_pdf(output_path, pdf_splitter.prefix):
        eel.update_progressbar(v, str(v) + "%")


if __name__ == "__main__":
    eel.init("web")
    eel.start("main.html", close_callback=onCloseWindow, size=(1200, 800))