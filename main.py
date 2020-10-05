import sys
import os
import eel
import pandas as pd
from pdf_splitter import pdfSplitter
try:
    from tkinter import Tk, filedialog
except:
    from Tkinter import Tk, filedialog
pdf_splitter = None

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
    # print(data)
    return data

eel.init("web")
eel.start("main.html", close_callback=onCloseWindow)