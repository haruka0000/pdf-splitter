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
    # print(pdf_splitter.df)
    columns = pdf_splitter.df.columns.tolist()
    data    = [columns] + pdf_splitter.df.values.tolist()
    return data


@eel.expose
def update_data(data):
    # print(data)
    data = [d for d in data if d != [] and d[0] != ""]
    columns = data[0]
    df = pd.DataFrame(data[1:], columns=columns)
    df[columns[1]] = df[columns[1]].astype(int)
    df[columns[2]] = df[columns[2]].astype(int)
    df.sort_values([columns[1], columns[2]], inplace=True)
    # print(df)
    return [columns] + df.values.tolist()
    
    
eel.init("web")
eel.start("main.html", close_callback=onCloseWindow)