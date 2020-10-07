import sys
import os
import eel
import pandas as pd
from pdf_splitter import pdfSplitter
try:
    from tkinter import Tk, filedialog
except:
    from Tkinter import Tk, filedialog


def onCloseWindow(page, sockets):
	print(page + 'が閉じられました。プログラムを終了します。')
	sys.exit()

@eel.expose
def btn_ResimyoluClick():
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    file_type   = [("PDF", "*.pdf")]
    init_dir    = os.path.abspath(os.path.dirname(__file__))
    file_name   = filedialog.askopenfilename(filetypes=file_type, initialdir=init_dir)
    return file_name


@eel.expose
def get_table_data(path):
    pdf_splitter = pdfSplitter(path)
    columns = pdf_splitter.df.reset_index().columns.tolist()
    data    = [columns] + pdf_splitter.df.reset_index().values.tolist()
    return data


@eel.expose
def update_data(data):
    # print(data)
    data = [d for d in data if d != [] and d[0] != ""]
    print(data)
    columns = data[0]
    df = pd.DataFrame(data[1:], columns=columns)
    df = df.set_index(columns[0])
    df[columns[1]] = df[columns[1]].astype(int)
    df[columns[2]] = df[columns[2]].astype(int)
    df = df.sort_values([columns[1], columns[2]])
    print(df)
    return [columns] + df.reset_index().values.tolist()
    
    
eel.init("web")
eel.start("main.html", close_callback=onCloseWindow)