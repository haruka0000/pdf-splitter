
import PyPDF2
import os
import time
import shutil
import sys
import argparse
import pandas as pd

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
            result[title] = page_id_to_page_numbers.get(page_idnum, '???')
        return result

def pdf_splitter(opts):
    src_file        = opts.src
    output_dir      = opts.output
    file_prefix     = opts.prefix
    src_delete_flag = bool(opts.delete)

    tmp_dir         = '.tmp/' # Temporary dir
    tmp_file        = os.path.join(tmp_dir, 'tmp.pdf')

    # Create tmp directory
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    shutil.copy(src_file, tmp_file)

    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #Process file
    pdf_data    = open(tmp_file, 'rb')
    pdf_reader  = PyPDF2.PdfFileReader(pdf_data)
    pdf_obj     = BookmarkToPageMap(pdf_data)

    if pdf_reader.isEncrypted:
        print("Encrypted.")
        pdf_reader.decrypt('')  ## important!!
        pdf_obj.decrypt('')     ## important!!
    else:
        print("Decrypted.")
    
    #Get total pages
    num_pages   = pdf_reader.numPages
    print('Number of page: ' + str(num_pages))

    data        = pdf_obj.getDestinationPageNumbers().items()
    df          = pd.DataFrame(data, columns=["title", "from"]).set_index('title')
    
    #### option ####
    df.at['Power Seat Systems', 'from'] = 378
    df.at['Power Seat Systems', 'to']   = 380

    to_page_num = [num-1 for num in df.loc[:,"from"].tolist()[1:]] + [num_pages]
    df['to']    = to_page_num
    df          = df.sort_values('from')
    print(df)
    
    for i, row in df.iterrows():
        pdf_writer = PyPDF2.PdfFileWriter()
        page_idx = 0
        print('Added page to PDF file: ' + row.name + ' - Page #:', end='')
        for j in range(row['from'], row['to']+1):
            pdf_page = pdf_reader.getPage(j-1)
            pdf_writer.addPage(pdf_page)
            print(str(j) + ',', end='')
            page_idx += 1
        print()
        pdf_file_name   = file_prefix + str(row.name).replace(':','_').replace('*','_') + '.pdf'
        output_path     = os.path.join(output_dir, pdf_file_name)
        
        pdf_output_file = open(output_path, 'wb')
        pdf_writer.write(pdf_output_file)
        pdf_output_file.close()
        print('Created PDF file: ' + output_path)
    """
        template = '%-5s  %s'
        print (template % ('Page', 'Title'))
        print (template % (p+1,t))
    
        new_page_num    = p + 1
        new_page_name   = t

        if prev_page_num == 0 and prev_page_name == '':
            print('First Page...')
            prev_page_num   = new_page_num
            prev_page_name  = new_page_name
        else:
            if new_page_name:
                print('Next Page...')
                pdf_writer = PyPDF2.PdfFileWriter()
                page_idx = 0 
                print(prev_page_num, new_page_num)
                for j in range(prev_page_num, new_page_num):
                    pdf_page = pdf_reader.getPage(j-1)
                    pdf_writer.insertPage(pdf_page, page_idx)
                    print('Added page to PDF file: ' + prev_page_name + ' - Page #: ' + str(j))
                    page_idx+=1

                pdf_file_name = file_prefix + str(str(prev_page_name).replace(':','_')).replace('*','_') + '.pdf'
                pdf_output_file = open(os.path.join(output_dir, pdf_file_name), 'wb')
                pdf_writer.write(pdf_output_file)
                pdf_output_file.close()
                print('Created PDF file: ' + os.path.join(output_dir, pdf_file_name))

        i = prev_page_num
        prev_page_num = new_page_num
        prev_page_name = new_page_name

        
        #Split the last page
        print('Last Page...')
        pdf_writer = PyPDF2.PdfFileWriter()
        page_idx = 0 
        for i in range(prev_page_num, num_pages + 1):
            pdf_page = pdf_reader.getPage(i-1)
            pdf_writer.insertPage(pdf_page, page_idx)
            # print('Added page to PDF file: ' + prev_page_name + ' - Page #: ' + str(i))
            page_idx+=1
        
        pdf_file_name = file_prefix + str(str(prev_page_name).replace(':','_')).replace('*','_') + '.pdf'
        pdf_output_file = open(output_dir + pdf_file_name, 'wb')
        pdf_writer.write(pdf_output_file)
        pdf_output_file.close()
        print('Created PDF file: ' + output_dir + pdf_file_name)
    """
    pdf_reader.close()
    # Delete temp file
    os.unlink(tmp_file)

    if src_delete_flag == True or src_delete_flag == "True":
        os.unlink(src_file)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True, help='input pdf')
    parser.add_argument('--output', type=str, default='./output', help='output path')
    parser.add_argument('--prefix', type=str, default='', help='prefix for th files')
    parser.add_argument('--delete', type=int, default=0, help='path for outputs')
    args = parser.parse_args()

    pdf_splitter(args)