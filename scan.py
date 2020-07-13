import re
import pandas as pd
import sys
from dateutil.parser import parse
from tkinter import *
from functools import partial
import glob
import sys
import zipfile
from datetime import datetime
import requests
import os

# select = input('Which example barcode do you want to pick? or scan? ')

# def which_barcode(response):
#     switcher = {
#         # Must configure barcode scanner to read FNC1 codes inside the barcode and program to add tab
#         '1': '012037086010010821TXZ811R4ZKNC	1723022810MT005', # azithromycin 500 mg box
#         '2': '01003633232956152155656222103517	17210630106019894', # vanco 5 gm vial box 363323295615 upc
#         '3': '010030049052083621303978156223	172207311033006308', # pen g 5 mil unit vial box
#         '4': "012037086012130121F83768X2HM3P	17220131109B08TQ", # zosyn 3.375 gm vial box (01)20370860121301 upc
#         # '5': '(01)00312345678906(21)SN345678(10)LN145(17)20181127',
#         '5': '01003442062511022126386940975151	1722102010P100149569',
#         '6': '010036068740583421100000968736	172202281020B88',
#         '7': '010036846233190321EAEV63DY6T9T	172112311019200264',
#         '8': '01003666851001152120000000010964	1721103110KC7045',
#         '9': '01203633232842002140366616241856	1721022810167918',
#         '10': '01003633232956152116749482636589	17210630106019894',
#         '11': '012037086012130121FZ7N875BGT7Z	17220131109B08TQ'
#         }
#     return switcher.get(response)
#
# raw_barcode = which_barcode(select)

# example1 = ' 01  2 03 7086010010 8  21  TXZ811R4ZKNC   17 230228 10 MT005' # azithromycin 500 mg box
# example2 = ' 01  0 03 6332329561 5  21  55656222103517 17 210630 10 6019894' # vanco 5 gm vial box 363323295615 upc
# example3 = ' 01  0 03 0049052083 6  21  303978156223   17 220731 10 33006308' # pen g 5 mil unit vial box
# example4 = ' 01  2 03 7086012130 1  21  F83768X2HM3P   17 220131 10 9B08TQ' # zosyn 3.375 gm vial box (01)20370860121301 upc
# example5 = "(01) 0 03 1234567890 6 (21) SN345678 (10) LN145 (17) 20181127"


#  general overview of codes
# https://www.cardinalhealth.com/content/dam/corp/web/documents/data-sheet/Cardinal-Health-barcode-quick-start-guidelines.pdf

# after serial number, will be fnc1 signal. can reprogram see site below. this allows to separate variable length
# serial number and tell where it ends

# program fnc1 to characters
# https://support.honeywellaidc.com/s/article/How-to-substitute-the-FNC1-GS-characters-in-GS1-128-UCC-EAN128-or-GS1-Datamatrix-bar-code

# 01 - GTIN? global trade item number
# 17 - expiration date
# 10 - LOT
# 21 - serial number

# raw_barcode = input("Scan barcode now: ")
# raw_barcode += input()
# raw_barcode += input()
# raw_barcode += input()
# print("Barcode: " , raw_barcode)

# PATTERN #1 WITH PARENTHESIS
# pattern = re.compile(r'^(\(01\)|\(21\)|\(17\)|\(10\)){1}(.+?)(\(21\)|\(17\)|\(10\))(.+?)(\(01\)|\(21\)|\(17\)|\(10\))(.+?)(\(01\)|\(21\)|\(17\)|\(10\)){1}(.+)')
# https://regex101.com/r/YgGtjZ/6

# PATTERN 2 with and without parenthesis
# pattern = re.compile(r'^(\(01\)|01|\(21\)|21|\(17\)|17|\(10\)|10){1}(\d{14})(\(21\)|21|\(17\)|17|\(10\)|10)(.+?)(\(\(21\)|21|\(17\)|17|\(10\)|10)(.+?)(\(21\)|21|\(17\)|17|\(10\)|10){1}(.+)$')

# PATTERN 3 ignore parenthesis case, incorporate tab after serial number
pattern = re.compile(r"^(01){1}(\d{14})(21){1}(.+?)\t(17){1}(\d{6})(10){1}(.+)$")


# result = pattern.match(raw_barcode)

# print(result.group(1))
# print(result.group(2))
# print(result.group(3))
# print(result.group(4))
# print(result.group(5))
# print(result.group(6))
# print(result.group(7))
# print(result.group(8))
# print('Full result list: ', result.groups())

# result_list = list(result.groups())

def remove_parenth(lst):
    res_list = lst
    bad_chars = '()'
    # res_lst = for c in bad_chars: s = s.replace(c, "")
    # print('Starting loop...')
    # for item in res_list:
    #     print('Fixing: ',item)
    #     for c in bad_chars:
    #         item = item.replace(c,"")
    #         print('Fixed? ',item)

    # a[:] = [x + 2 for x in a]
    # res_list = item.replace(c,"") for c in bad_chars for item in res_list

    # res_list = [item.replace(c,"") for item in res_list for c in bad_chars]
    # print('type of res_list: ', type(res_list))
    for pos, item in enumerate(res_list):
        for c in bad_chars:
            item = item.replace(c, "")
            res_list[pos] = item
    return res_list


# result_list = remove_parenth(result_list)
# print('Parenths removed: ', result_list)

def convert_to_dict(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct


# result_dict = convert_to_dict(result_list)


# print('Full result dictionary: ', result_dict)

# result_dict['GTIN'] = result_dict.pop('01')
# result_dict['Exp date'] = result_dict.pop('17')
# result_dict['LOT'] = result_dict.pop('10')
# result_dict['Serial'] = result_dict.pop('21')
#
# temp = parse(result_dict['Exp date'])
# print('Date parsing... ', temp)
# result_dict['Exp date'] = datetime.strptime(result_dict['Exp date'], '%y%m%d').strftime("%m/%d/%Y")

# print('Renamed full result dictionary: ', result_dict)

# need validation for day of 00

def converter(unrefined_date):
    return parse(unrefined_date, yearfirst=True, fuzzy=True).strftime('%m/%d/%Y')

def get_recent_db():
    # gets most recent ndc db
    return

def match_NDC(ndc):

    def find_recent_db():
        # returns most recent db csv file
        files = glob.glob('ndcdb-*.csv')

        pattern = re.compile(r"^ndcdb-(\d{4}-\d{2}-\d{2}).csv$")
        dates_list = []
        for file in files:
            str_date = pattern.match(file).groups()[0]
            date = datetime.strptime(str_date, '%Y-%m-%d')
            dates_list.append(date)

        formatted_date = datetime.strftime(max(dates_list).date(), '%Y-%m-%d')

        recent_db_file = 'ndcdb-' + formatted_date + '.csv'
        lastupdated_label["text"] = "Using data last updated on: " + formatted_date
        return recent_db_file

    recent_file = find_recent_db()
    df = pd.read_csv(recent_file)
    print('Using db from this file: ', recent_file)
    df['NDCPACKAGECODE_nohyphen'] = df['NDCPACKAGECODE'].apply(lambda x: x.replace('-', ''))
    if ndc in df['NDCPACKAGECODE_nohyphen'].values:
        index = df.loc[df['NDCPACKAGECODE_nohyphen'] == ndc].index[0]
        raw_ndc = df['NDCPACKAGECODE'][index]
        pack_desc = df['PACKAGEDESCRIPTION'][index]
        brand = df['PROPRIETARYNAME'][index]
        generic = df['NONPROPRIETARYNAME'][index]
        dosage_form = df['DOSAGEFORMNAME'][index]
        route = df['ROUTENAME'][index]
        mfg = df['LABELERNAME'][index]
        strength = df['ACTIVE_NUMERATOR_STRENGTH'][index]
        str_units = df['ACTIVE_INGRED_UNIT'][index]
        pharm_class = df['PHARM_CLASSES'][index]

        def eleven_dig(ten_digit):
            lst = ten_digit.split("-")
            lst[0] = lst[0].zfill(5)
            lst[1] = lst[1].zfill(4)
            lst[2] = lst[2].zfill(2)
            return ''.join(lst)

        ten_dig = eleven_dig(raw_ndc)
        return True, raw_ndc, ten_dig, pack_desc, brand, generic, dosage_form, route, mfg, strength, \
               str_units, pharm_class
    else:
        print("Doesn't exist")
        sys.exit()
        # return False


# result_dict['Exp date'] = converter(result_dict['Exp date'])
# result_dict['NDC'] = result_dict['GTIN'][3:13]
#
# match, with_hyphen, ndc_11, package, brand, generic, dosage_form, route, mfg, \
# strength,str_units, pharm_class = match_NDC(result_dict['NDC'])
#
# # print('Barcode Info ', result_dict)
# print('NDC: ', result_dict['NDC'])
# print('LOT: ', result_dict['LOT'])
# print('Exp date: ',result_dict['Exp date'])
# # print('Check if ', result_dict['NDC'], ' matches: ', str(match) )
# print('NDC with hyphen: ', with_hyphen)
# print('11 digit ndc: ' , ndc_11)
# print('Package Description: ', package)
# print('Brand Name: ', brand)
# print('Generic Name: ', generic)
# print('Strength: ', strength, str_units)
# # print('Units: ', str_units)
# print('Dosage Form: ', dosage_form)
# print('Route: ',route )
# print('Manufacturer/Labeler: ',mfg)
# print('Pharmaceutical Class: ', pharm_class)

def generate_db(event=None):

    # popupmsg("Working...")
    url = "https://www.accessdata.fda.gov/cder/ndctext.zip"
    print("Downloading db from ", url)
    r = requests.get(url)
    now = datetime.now().strftime('%Y-%m-%d')
    zip_file_name = "{filename}-{sysdate}.zip".format(sysdate=now, filename="ndctext")

    with open(zip_file_name, 'wb') as f:
        f.write(r.content)

    with zipfile.ZipFile(zip_file_name, 'r') as myzip:
        files = myzip.namelist()
        df = [pd.read_csv(myzip.open(f), sep='\t', encoding='unicode_escape', index_col='PRODUCTID') for f in files]
        lastmodified = myzip.getinfo(files[0]).date_time
        dt_lastmodified = datetime(lastmodified[0],lastmodified[1],lastmodified[2]).date().strftime('%Y-%m-%d')

    if files[0] == 'package.txt':
        package = df[0]
        product = df[1]
    else:
        print('Double check zip files')
        sys.exit()

    # merge product.txt and package.txt together by PRODUCTID
    joined = pd.merge(package, product, how='left', on='PRODUCTID')

    # remove all rows that don't have a package ndc
    joined.dropna(subset=['PRODUCTNDC_y'], inplace=True)

    # remove duplicate columns
    joined.drop(['NDC_EXCLUDE_FLAG_y', 'ENDMARKETINGDATE_y', 'STARTMARKETINGDATE_y', 'PRODUCTNDC_y'], axis=1,
                inplace=True)

    # rename _x columns to the regular names
    joined.columns = joined.columns.str.replace('_x', '')

    joined.to_csv('ndcdb-' + dt_lastmodified + '.csv')
    os.rename(zip_file_name, 'ndctext-' + dt_lastmodified + '.zip')
    print("Generating db completed")


def run(event=None):
    try:
        selection = var.get()
        if selection == 0:
            popupmsg("No barcode type selected. Please select type of barcode")
        elif selection == 1:
            # code for 2d barcode below
            # run the program
            # get input barcode from user
            raw_barcode = barcode_entry.get()
            # match this pattern
            pattern = re.compile(r"^(01){1}(\d{14})(21){1}(.+?)\t(17){1}(\d{6})(10){1}(.+)$")
            result = pattern.match(raw_barcode)
            result_list = list(result.groups())
            # convert to dictionary
            result_dict = convert_to_dict(result_list)
            result_dict['GTIN'] = result_dict.pop('01')
            result_dict['Exp date'] = result_dict.pop('17')
            result_dict['LOT'] = result_dict.pop('10')
            result_dict['Serial'] = result_dict.pop('21')
            result_dict['Exp date'] = converter(result_dict['Exp date'])
            result_dict['NDC'] = result_dict['GTIN'][3:13]
            # cross reference FDA NDC database
            match, with_hyphen, ndc_11, package, brand, generic, dosage_form, route, mfg, \
            strength, str_units, pharm_class = match_NDC(result_dict['NDC'])

            # print('Barcode Info ', result_dict)
            print('11 digit ndc: ', ndc_11)
            print('Scanned NDC: ', result_dict['NDC'])
            print('NDC with hyphen: ', with_hyphen)
            print('LOT: ', result_dict['LOT'])
            print('Exp date: ', result_dict['Exp date'])
            # print('Check if ', result_dict['NDC'], ' matches: ', str(match) )
            print('Package Description: ', package)
            print('Brand Name: ', brand)
            print('Generic Name: ', generic)
            print('Strength: ', strength, str_units)
            # print('Units: ', str_units)
            print('Dosage Form: ', dosage_form)
            print('Route: ', route)
            print('Manufacturer/Labeler: ', mfg)
            print('Pharmaceutical Class: ', pharm_class)

            # global ndc_11_result
            ndc_11_result["text"] = ndc_11
            ndc_scanned_result["text"] = result_dict['NDC']
            ndc_hyphen_result["text"] = with_hyphen
            ndc_lot_result["text"] = result_dict['LOT']
            ndc_exp_result["text"] = result_dict['Exp date']
            ndc_pkg_result["text"] = package
            ndc_brand_result["text"] = brand
            ndc_generic_result["text"] = generic
            ndc_str_result["text"] = strength, str_units
            ndc_dosageform_result["text"] = dosage_form
            ndc_route_result["text"] = route
            ndc_mfg_result["text"] = mfg
            ndc_class_result["text"] = pharm_class

        elif selection == 2:
            # code for linear barcode below
            raw_barcode = barcode_entry.get()
            pattern = re.compile(r"^\d(\d{10})\d$")
            result = pattern.match(raw_barcode).groups()[0]

            match, with_hyphen, ndc_11, package, brand, generic, dosage_form, route, mfg, \
            strength, str_units, pharm_class = match_NDC(result)

            # print('Barcode Info ', result_dict)
            print('11 digit ndc: ', ndc_11)
            print('Scanned NDC: ', result)
            print('NDC with hyphen: ', with_hyphen)
            print('LOT: ', 'no LOT information in this barcode')
            print('Exp date: ', 'no EXP information in this barcode')
            # print('Check if ', result_dict['NDC'], ' matches: ', str(match) )
            print('Package Description: ', package)
            print('Brand Name: ', brand)
            print('Generic Name: ', generic)
            print('Strength: ', strength, str_units)
            # print('Units: ', str_units)
            print('Dosage Form: ', dosage_form)
            print('Route: ', route)
            print('Manufacturer/Labeler: ', mfg)
            print('Pharmaceutical Class: ', pharm_class)

            # global ndc_11_result
            ndc_11_result["text"] = ndc_11
            ndc_scanned_result["text"] = result
            ndc_hyphen_result["text"] = with_hyphen
            ndc_lot_result["text"] = "no LOT information in this barcode"
            ndc_exp_result["text"] = "no EXP information in this barcode"
            ndc_pkg_result["text"] = package
            ndc_brand_result["text"] = brand
            ndc_generic_result["text"] = generic
            ndc_str_result["text"] = strength, str_units
            ndc_dosageform_result["text"] = dosage_form
            ndc_route_result["text"] = route
            ndc_mfg_result["text"] = mfg
            ndc_class_result["text"] = pharm_class
    except:
        if selection == 1:
            sel = "2d barcode"
        elif selection == 2:
            sel = "linear barcode"
        scan = raw_barcode
        popupmsg("Barcode invalid, please double check:\n\n"
                 "1. Barcode type selection. You selected: " + sel + "\n"
                 "2. Barcode scanner is configured correctly\n"
                 "3. Scanned barcode is correct. You scanned: " + scan + "\n"
                 "4. Make sure there's a 'ndcdb' file in the same folder as this file.\n\n"
                 "Program is still too ghetto to tell you which one of these is causing the error :)")
        print("See error message")


def popupmsg(msg):
    LARGE_FONT = ("Verdana", 12)
    NORM_FONT = ("Helvetica", 10)
    SMALL_FONT = ("Helvetica", 8)
    popup = Tk()
    popup.wm_title("!")
    label = Label(popup, text=msg, font=NORM_FONT, justify=LEFT)
    label.pack(side="top", fill="x", pady=10)
    B1 = Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


def copy_button(label):
    clip = Tk()
    clip.withdraw()
    clip.clipboard_clear()
    clip.clipboard_append(label.cget("text"))  # Change INFO_TO_COPY to the name of your data source
    clip.update()
    clip.destroy()
    print('Copying: ', label.cget("text"))


def read_label_text(label):
    print(label.cget("text"))


window = Tk()

var = IntVar()
var.set(0)
window.title("Barcode Extraction Tool v0.1")
intro_label = Label(window, text="Welcome to the barcode extraction tool. \n Please configure the barcode scanner "
                                 "appropriately to ensure this program works.\n"
                                 "Scan barcode into box below and mark the correct type and hit submit")

# barcode_label = Label(window, text = "Scan 2d barcode into this box")
barcode_entry = Entry(window, width=75)
box_barcode = Radiobutton(window, text="2d barcode", value=1, variable=var)
linear_barcode = Radiobutton(window, text="linear barcode", value=2, variable=var)
proceed_button = Button(window, text="Submit", command=run)
window.bind('<Return>', run)

generatedb_button = Button(window, text="Generate DB",command=generate_db)
lastupdated_label = Label(window)
close_button = Button(window, text="Quit", command=window.quit)

ndc_11_label = Label(window, text="11 digit ndc: ")
ndc_11_result = Label(window)
ndc_11_button = Button(window, text="Copy", command=partial(copy_button, ndc_11_result))

ndc_scanned_label = Label(window, text="Scanned NDC: ")
ndc_scanned_result = Label(window)
ndc_scanned_button = Button(window, text="Copy", command=partial(copy_button, ndc_scanned_result))

ndc_hyphen_label = Label(window, text="NDC with hyphen: ")
ndc_hyphen_result = Label(window)
ndc_hyphen_button = Button(window, text="Copy", command=partial(copy_button, ndc_hyphen_result))

ndc_lot_label = Label(window, text="LOT: ")
ndc_lot_result = Label(window)
ndc_lot_button = Button(window, text="Copy", command=partial(copy_button, ndc_lot_result))

ndc_exp_label = Label(window, text="EXP: ")
ndc_exp_result = Label(window)
ndc_exp_button = Button(window, text="Copy", command=partial(copy_button, ndc_exp_result))

ndc_pkg_label = Label(window, text="Package Description: ")
ndc_pkg_result = Label(window)
ndc_pkg_button = Button(window, text="Copy", command=partial(copy_button, ndc_pkg_result))

ndc_brand_label = Label(window, text="Brand Name: ")
ndc_brand_result = Label(window)
ndc_brand_button = Button(window, text="Copy", command=partial(copy_button, ndc_brand_result))

ndc_generic_label = Label(window, text="Generic Name: ")
ndc_generic_result = Label(window)
ndc_generic_button = Button(window, text="Copy", command=partial(copy_button, ndc_generic_result))

ndc_str_label = Label(window, text="Strength: ")
ndc_str_result = Label(window)
ndc_str_button = Button(window, text="Copy", command=partial(copy_button, ndc_str_result))

ndc_dosageform_label = Label(window, text="Dosage Form: ")
ndc_dosageform_result = Label(window)
ndc_dosageform_button = Button(window, text="Copy", command=partial(copy_button, ndc_dosageform_result))

ndc_route_label = Label(window, text="Route: ")
ndc_route_result = Label(window)
ndc_route_button = Button(window, text="Copy", command=partial(copy_button, ndc_route_result))

ndc_mfg_label = Label(window, text="Manufacturer/Labeler: ")
ndc_mfg_result = Label(window)
ndc_mfg_button = Button(window, text="Copy", command=partial(copy_button, ndc_mfg_result))

ndc_class_label = Label(window, text="Pharmaceutical Class: ")
ndc_class_result = Label(window)
ndc_class_button = Button(window, text="Copy", command=partial(copy_button, ndc_class_result))

# POSITIONING BELOW

intro_label.grid(row=0, column=0, columnspan=3, sticky=W + E)

barcode_entry.grid(row=1, rowspan=3, columnspan=2, sticky=E + S)
box_barcode.grid(row=1, column=2, sticky=W)
linear_barcode.grid(row=2, column=2, sticky=W)
proceed_button.grid(row=3, column=2, sticky=W)

# barcode_label.grid(row=1,column=0,sticky=E)

generatedb_button.grid(row=17,column=0,sticky=W)
lastupdated_label.grid(row=17,column=1,sticky=W)
close_button.grid(row=17, column=2, sticky=W)

ndc_hyphen_label.grid(row=4, column=0, sticky=W)
ndc_hyphen_result.grid(row=4, column=1, sticky=W)
ndc_hyphen_button.grid(row=4, column=2, sticky=W)

ndc_11_label.grid(row=5, column=0, sticky=W)
ndc_11_result.grid(row=5, column=1, sticky=W)
ndc_11_button.grid(row=5, column=2, sticky=W)

ndc_lot_label.grid(row=6, column=0, sticky=W)
ndc_lot_result.grid(row=6, column=1, sticky=W)
ndc_lot_button.grid(row=6, column=2, sticky=W)

ndc_exp_label.grid(row=7, column=0, sticky=W)
ndc_exp_result.grid(row=7, column=1, sticky=W)
ndc_exp_button.grid(row=7, column=2, sticky=W)

ndc_pkg_label.grid(row=8, column=0, sticky=W)
ndc_pkg_result.grid(row=8, column=1, sticky=W)
ndc_pkg_button.grid(row=8, column=2, sticky=W)

ndc_brand_label.grid(row=9, column=0, sticky=W)
ndc_brand_result.grid(row=9, column=1, sticky=W)
ndc_brand_button.grid(row=9, column=2, sticky=W)

ndc_generic_label.grid(row=10, column=0, sticky=W)
ndc_generic_result.grid(row=10, column=1, sticky=W)
ndc_generic_button.grid(row=10, column=2, sticky=W)

ndc_str_label.grid(row=11, column=0, sticky=W)
ndc_str_result.grid(row=11, column=1, sticky=W)
ndc_str_button.grid(row=11, column=2, sticky=W)

ndc_dosageform_label.grid(row=12, column=0, sticky=W)
ndc_dosageform_result.grid(row=12, column=1, sticky=W)
ndc_dosageform_button.grid(row=12, column=2, sticky=W)

ndc_route_label.grid(row=13, column=0, sticky=W)
ndc_route_result.grid(row=13, column=1, sticky=W)
ndc_route_button.grid(row=13, column=2, sticky=W)

ndc_mfg_label.grid(row=14, column=0, sticky=W)
ndc_mfg_result.grid(row=14, column=1, sticky=W)
ndc_mfg_button.grid(row=14, column=2, sticky=W)

ndc_class_label.grid(row=15, column=0, sticky=W)
ndc_class_result.grid(row=15, column=1, sticky=W)
ndc_class_button.grid(row=15, column=2, sticky=W)

window.mainloop()

# 012037086010010821TXZ811R4ZKNC	1723022810MT005


# try:
#     print('Type of this one date... ', type(parse(i,yearfirst=True,fuzzy=True).strftime('%m/%d/%Y')))
#     yield parse(i,yearfirst=True,fuzzy=True).strftime('%m/%d/%Y')
# except ValueError:
#     yield i
# try:
#     yield parse(i)
# except ValueError:
#     try:
#         yield parse(i, dayfirst=True)
#     except ValueError:
#         try:
#             yield datetime.strptime(i, '%y%m%d')
#         except:
#             yield i


# ----------------------------------------------------

# def converter(lst):
#     for i in lst:
#         try:
#             yield parser.parse(i)
#         except ValueError:
#             try:
#                 yield parser.parse(i, dayfirst=True)
#             except ValueError:
#                 try:
#                     yield datetime.strptime(i, '%Y-%d-%b')
#                 except:
#                     yield i

# res = list(converter(list1))

# ----------------------------------------------------

# groups = re.findall(r'\(01\)|\(21\)|\(17\)|\(10\)(.*?)', raw_barcode)
# print(groups)

# groups = re.findall(r'(\w+)="(.*?)"', raw_barcode)
# barcode_dict = dict(groups)

# refined_barcode = re.split('\(01\)|\(21\)|\(17\)|\(10\)',raw_barcode)
# refined_barcode = refined_barcode[1:]
# refined_barcode = [x.strip(' ') for x in refined_barcode]
# print(refined_barcode)

# https://stackoverflow.com/questions/30731763/python-parse-string-with-regex-for-constitute-a-dictionary
# parse string regex into dictionary

# w 01 20085412003461 10 DR18G25051 | data matrix

# 250 ml empty bag | 01 00812496011589 10 66045-A4599 17 210706 | data matrix

# duoneb albuterol | w 01 00360687405834 21 100000974164 17 220228 10 20B88 | data matrix

# keppra 500 mg/100 ml bag | c367457255002 | upc A

# w 01 003633232956152182207294774072 17 21063 01 06019894 | data matrix

# y 01 00303380049028 | GS1 Databar

# { 01 00304094887258 | GS1 databar limited

# I0150303380049023 | GS1 -128 hospira

# I0150303380049023    I0150303380049023 | GS1 -128

# I0100304096648024 | GS1 -128

# -----------------


# w 01 20363323284200 21 74981478404269 17 21013 11 0167904

# w 01 20370860121301 21 4YFBCSW519SZ 17 22013 11 09B08TQ

# 01 - GTIN? global trade item number

# 17 - expiration date

# 11 - LOT
# 10

# 21 - serial number

# ---------------------

# y 01 00303380553181


# Code 128, Code ID is “j” and Hex ID is “6A”.

# data matrix ID = w, hex = 77

# w01003445671031022136G3332CEM17221231 10 0A03AK


# ------------------------------------------------------------------------


#
# # examples
# example1 = '012037086010010821TXZ811R4ZKNC1723022810MT005' # azithromycin 500 mg box
# example2 = '0100363323295615215565622210351717210630106019894' # vanco 5 gm vial box 363323295615 upc
# example3 = '010030049052083621303978156223172207311033006308' # pen g 5 mil unit vial box
# example4 = '012037086012130121F83768X2HM3P17220131109B08TQ' # zosyn 3.375 gm vial box (01)20370860121301 upc
# example5 = "(01)00312345678906(21)SN345678(10)LN145(17)20181127"
# raw_barcode = example4
#
# # example1 = ' 01  2 03 7086010010 8  21  TXZ811R4ZKNC   17 230228 10 MT005' # azithromycin 500 mg box
# # example2 = ' 01  0 03 6332329561 5  21  55656222103517 17 210630 10 6019894' # vanco 5 gm vial box 363323295615 upc
# # example3 = ' 01  0 03 0049052083 6  21  303978156223   17 220731 10 33006308' # pen g 5 mil unit vial box
# # example4 = ' 01  2 03 7086012130 1  21  F83768X2HM3P   17 220131 10 9B08TQ' # zosyn 3.375 gm vial box (01)20370860121301 upc
# # example5 = "(01) 0 03 1234567890 6 (21) SN345678 (10) LN145 (17) 20181127"
#
#
# #  general overview of codes
# # https://www.cardinalhealth.com/content/dam/corp/web/documents/data-sheet/Cardinal-Health-barcode-quick-start-guidelines.pdf
#
# # after serial number, will be fnc1 signal. can reprogram see site below. this allows to separate variable length
# # serial number and tell where it ends
#
# # program fnc1 to characters
# # https://support.honeywellaidc.com/s/article/How-to-substitute-the-FNC1-GS-characters-in-GS1-128-UCC-EAN128-or-GS1-Datamatrix-bar-code
#
# # 01 - GTIN? global trade item number
# # 17 - expiration date
# # 10 - LOT
# # 21 - serial number
#
# # raw_barcode = input("Scan barcode now: ")
# # raw_barcode += input()
# # raw_barcode += input()
# # raw_barcode += input()
# # print("Barcode: " , raw_barcode)
#
# # PATTERN #1 WITH PARENTHESIS
# # pattern = re.compile(r'^(\(01\)|\(21\)|\(17\)|\(10\)){1}(.+?)(\(21\)|\(17\)|\(10\))(.+?)(\(01\)|\(21\)|\(17\)|\(10\))(.+?)(\(01\)|\(21\)|\(17\)|\(10\)){1}(.+)')
# # https://regex101.com/r/YgGtjZ/1
#
# # PATTERN 2
# pattern = re.compile(r'^(\(01\)|01|\(21\)|21|\(17\)|17|\(10\)|10){1}(\d{14})(\(21\)|21|\(17\)|17|\(10\)|10)(.+?)(\(\(21\)|21|\(17\)|17|\(10\)|10)(.+?)(\(21\)|21|\(17\)|17|\(10\)|10){1}(.+)$')
# result = pattern.match(raw_barcode)
#
# # print(result.group(1))
# # print(result.group(2))
# # print(result.group(3))
# # print(result.group(4))
# # print(result.group(5))
# # print(result.group(6))
# # print(result.group(7))
# # print(result.group(8))
# print('Full result list: ', result.groups())
#
# result_list = list(result.groups())
#
# def remove_parenth(lst):
#     res_list = lst
#     bad_chars = '()'
#     # res_lst = for c in bad_chars: s = s.replace(c, "")
#     # print('Starting loop...')
#     # for item in res_list:
#     #     print('Fixing: ',item)
#     #     for c in bad_chars:
#     #         item = item.replace(c,"")
#     #         print('Fixed? ',item)
#
#     # a[:] = [x + 2 for x in a]
#     # res_list = item.replace(c,"") for c in bad_chars for item in res_list
#
#     # res_list = [item.replace(c,"") for item in res_list for c in bad_chars]
#     print('type of res_list: ', type(res_list))
#     for pos, item in enumerate(res_list):
#         for c in bad_chars:
#             item = item.replace(c,"")
#             res_list[pos] = item
#     return res_list
#
# result_list = remove_parenth(result_list)
# print('Parenths removed: ', result_list)
#
# def convert_to_dict(lst):
#     res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
#     return res_dct
#
# result_dict = convert_to_dict(result_list)
#
#
#
# print('Full result dictionary: ', result_dict)
#
# result_dict['GTIN'] = result_dict.pop('01')
# result_dict['Exp date'] = result_dict.pop('17')
# result_dict['LOT'] = result_dict.pop('10')
# result_dict['Serial'] = result_dict.pop('21')
#
# # temp = parse(result_dict['Exp date'])
# # print('Date parsing... ', temp)
# # result_dict['Exp date'] = datetime.strptime(result_dict['Exp date'], '%y%m%d').strftime("%m/%d/%Y")
#
# print('Renamed full result dictionary: ', result_dict)
#
# # need validation for day of 00
#
# def converter(unrefined_date):
#     return parse(unrefined_date,yearfirst=True,fuzzy=True).strftime('%m/%d/%Y')
#
# result_dict['Exp date'] = converter(result_dict['Exp date'])
#
# print('Dictionary with formatted date: ', result_dict)
# print('LOT: ', result_dict['LOT'])
# print('Exp date: ',result_dict['Exp date'])
#
#         # try:
#         #     print('Type of this one date... ', type(parse(i,yearfirst=True,fuzzy=True).strftime('%m/%d/%Y')))
#         #     yield parse(i,yearfirst=True,fuzzy=True).strftime('%m/%d/%Y')
#         # except ValueError:
#         #     yield i
#         # try:
#         #     yield parse(i)
#         # except ValueError:
#         #     try:
#         #         yield parse(i, dayfirst=True)
#         #     except ValueError:
#         #         try:
#         #             yield datetime.strptime(i, '%y%m%d')
#         #         except:
#         #             yield i
#
#
# # ----------------------------------------------------
#
# # def converter(lst):
# #     for i in lst:
# #         try:
# #             yield parser.parse(i)
# #         except ValueError:
# #             try:
# #                 yield parser.parse(i, dayfirst=True)
# #             except ValueError:
# #                 try:
# #                     yield datetime.strptime(i, '%Y-%d-%b')
# #                 except:
# #                     yield i
#
# # res = list(converter(list1))
#
# # ----------------------------------------------------
#
#
#
#
#
#
#
# # groups = re.findall(r'\(01\)|\(21\)|\(17\)|\(10\)(.*?)', raw_barcode)
# # print(groups)
#
# # groups = re.findall(r'(\w+)="(.*?)"', raw_barcode)
# # barcode_dict = dict(groups)
#
#
#
#
# # refined_barcode = re.split('\(01\)|\(21\)|\(17\)|\(10\)',raw_barcode)
# # refined_barcode = refined_barcode[1:]
# # refined_barcode = [x.strip(' ') for x in refined_barcode]
# # print(refined_barcode)
#
# # https://stackoverflow.com/questions/30731763/python-parse-string-with-regex-for-constitute-a-dictionary
# # parse string regex into dictionary
#
# # w 01 20085412003461 10 DR18G25051 | data matrix
#
# # 250 ml empty bag | 01 00812496011589 10 66045-A4599 17 210706 | data matrix
#
# # duoneb albuterol | w 01 00360687405834 21 100000974164 17 220228 10 20B88 | data matrix
#
# # keppra 500 mg/100 ml bag | c367457255002 | upc A
#
# # w 01 003633232956152182207294774072 17 21063 01 06019894 | data matrix
#
# # y 01 00303380049028 | GS1 Databar
#
# # { 01 00304094887258 | GS1 databar limited
#
# # I0150303380049023 | GS1 -128 hospira
#
# # I0150303380049023    I0150303380049023 | GS1 -128
#
# # I0100304096648024 | GS1 -128
#
# # -----------------
#
#
# # w 01 20363323284200 21 74981478404269 17 21013 11 0167904
#
# # w 01 20370860121301 21 4YFBCSW519SZ 17 22013 11 09B08TQ
#
# # 01 - GTIN? global trade item number
#
# # 17 - expiration date
#
# # 11 - LOT
# # 10
#
# # 21 - serial number
#
# # ---------------------
#
# # y 01 00303380553181
#
#
# # Code 128, Code ID is “j” and Hex ID is “6A”.
#
# # data matrix ID = w, hex = 77
#
# # w01003445671031022136G3332CEM17221231 10 0A03AK
#
