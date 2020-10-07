import PyPDF2
import os
import time
import shutil
import sys
import argparse
import pandas as pd
import math

# Helper class used to map pages numbers to bookmarks
class BookmarkToPageMap(PyPDF2.PdfFileReader):
    def getDestinationPageNumbers(self):
        def _setup_outline_page_ids(outline, _result=None):
            if _result is None:
                _result = {}
            for obj in outline:
                if isinstance(obj, PyPDF2.pdf.Destination):
                    _result[(id(obj), obj.title)] = obj.page.idnum
                elif isinstance(obj, list):
                    pass
                    # _setup_outline_page_ids(obj, _result)
            return _result

        def _setup_page_id_to_num(pages=None, _result=None, _num_pages=None):
            if _result is None:
                _result = {}
            if pages is None:
                _num_pages = []
                pages = self.trailer["/Root"].getObject()["/Pages"].getObject()
            t = pages["/Type"]
            if t == "/Pages":
                for page in pages["/Kids"]:
                    _result[page.idnum] = len(_num_pages)
                    _setup_page_id_to_num(page.getObject(), _result, _num_pages)
            elif t == "/Page":
                _num_pages.append(1)
            return _result

        outline_page_ids = _setup_outline_page_ids(self.getOutlines())
        page_id_to_page_numbers = _setup_page_id_to_num()

        result = {}
        for (_, title), page_idnum in outline_page_ids.items():
            if isinstance(title, PyPDF2.generic.ByteStringObject): 
                title = title.decode('utf-8', errors="ignore") 
            title = title.replace('\r', '').replace('\n', '')
            result[title] = page_id_to_page_numbers.get(page_idnum, '???') + 1
        return result

class pdfSplitter():
    def __init__(self, src_file):
        self.src_file   = src_file
        self.tmp_dir         = '.tmp/' # Temporary dir
        self.tmp_file        = os.path.join(self.tmp_dir, 'tmp.pdf')

        # Create tmp directory
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        
        shutil.copy(self.src_file, self.tmp_file)

        #Process file
        pdf_data        = open(self.tmp_file, 'rb')
        self.pdf_reader = PyPDF2.PdfFileReader(pdf_data)
        self.pdf_obj    = BookmarkToPageMap(pdf_data)

        if self.pdf_reader.isEncrypted:
            print("Encrypted.")
            self.pdf_reader.decrypt('')  ## important!!
            self.pdf_obj.decrypt('')     ## important!!
        else:
            print("Decrypted.")
        
        #Get total pages
        self.num_pages  = self.pdf_reader.numPages
        print('Number of page: ' + str(self.num_pages))

        data        = self.pdf_obj.getDestinationPageNumbers().items()
        df          = pd.DataFrame(data, columns=["title", "from"]).set_index('title')#[1:]
        
        #### option ####
        # df.at['Power Seat Systems', 'from'] = 378
        # df.at['Power Seat Systems', 'to']   = 380
        ################

        to_page_num = df.loc[:,"from"].tolist()[1:] + [self.num_pages+1]
        from_page_num = df.loc[:,"from"].tolist()
        to_page_num = [to_page_num[i]-1 if to_page_num[i] > from_page_num[i] else to_page_num[i] for i in range(len(df))]
        to_page_num = to_page_num
        df['to']    = to_page_num
        df          = df.sort_values(['from', 'to'])
        
        self.df = df


    def split_pdf(self, output_dir, file_prefix='', src_delete_flag=False, max_num_pages=1000):
        if file_prefix != '':
            file_prefix = file_prefix + '-'

        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_count  = 0
        for i, row in self.df.iterrows():
            pdf_writer = PyPDF2.PdfFileWriter()

            page_count  = 0
            print('Added page to PDF file: ' + row.name + ' - Page #:', end='')
            for j in range(row['from'], row['to']+1):
                print(str(j) + ',', end='')
                pdf_page = self.pdf_reader.getPage(j-1)
                pdf_writer.addPage(pdf_page)
                pdf_writer.removeLinks()
                page_count += 1
                if (page_count != 0 and page_count % max_num_pages == 0) or j == row['to']:
                    print()
                    file_count += 1
                    pdf_file_name   = file_prefix + '%03d_'%(file_count) + str(row.name).replace(':','_').replace('*','_').replace('/', '／') + '.pdf'
                    if math.ceil(round((row['to'] - row['from']) / float(max_num_pages), 5)) > 1:
                        pdf_file_name = pdf_file_name.replace('.pdf', '-%02d.pdf'%(math.ceil(round(page_count/float(max_num_pages), 5)))) 
                    output_path     = os.path.join(output_dir, pdf_file_name)
                    ## Important!! Remove annotations from file. Writing error(stop) will occur without this processs.
                    # pdf_writer.removeLinks()
                    with open(output_path, 'wb') as pdf_output_file:
                        pdf_writer.write(pdf_output_file)
                        print(' => Created PDF file: ' + output_path)
                    pdf_writer = PyPDF2.PdfFileWriter() ## initialize
                    print('Added page to PDF file: ' + row.name + ' - Page #:', end='')
            print()
        # Delete temp file
        os.unlink(self.tmp_file)

        if src_delete_flag == True or src_delete_flag == "True":
            os.unlink(self.src_file)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True, help='input pdf')
    parser.add_argument('--output', type=str, default='./output', help='output path')
    parser.add_argument('--prefix', type=str, default='', help='prefix for th files')
    parser.add_argument('--max', type=int, default=20, help='Max pages num in each files.')
    parser.add_argument('--delete', type=int, default=0, help='path for outputs')
    opts = parser.parse_args()

    src_file        = opts.src
    output_dir      = opts.output
    file_prefix     = opts.prefix
    src_delete_flag = bool(opts.delete)
    max_num_pages   = opts.max

    pdf_splitter    = pdfSplitter(src_file)
    pdf_splitter.split_pdf(output_dir, file_prefix=file_prefix, src_delete_flag=src_delete_flag, max_num_pages=max_num_pages)