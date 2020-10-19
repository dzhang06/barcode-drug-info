# import re
import pandas as pd
# import sys
from dateutil.parser import parse
from tkinter import *
from tkinter import messagebox
from functools import partial
import glob
import sys
import zipfile
from datetime import datetime
import requests
import os
from calendar import monthrange

version = "0.3.2"


def convert_to_dict(lst):
    """ converts the one liner barcode string into individual components using dict """
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct


def converter(unrefined_date):
    """ converts barcode date of YYMMDD to mm/dd/yyyy
        if day is 00, automatically change to 31;
        example 220100 = 220131
    """
    dt_yr = unrefined_date[:2]
    dt_mo = unrefined_date[2:4]
    dt_dy = unrefined_date[4:]
    if dt_dy == '00':
        dt_dy = str(monthrange(int(dt_yr), int(dt_mo))[1])
    return parse(dt_yr+dt_mo+dt_dy, yearfirst=True).strftime('%m/%d/%Y')


def remove_hyphen(string):
    """ removes hyphen from ndc """
    return string.replace('-', '')


def str_to_list(string):
    new_list = list(string.strip('][').split(', '))
    print("Returning a list? ", new_list, " of type: ", type(new_list))
    return new_list


def match_ndc(ndc):
    """ Matches the NDC to db"""

    def find_recent_db():
        """ returns most recent db csv file. Gives error pop up if no db file found """
        files = glob.glob('ndcdb-*.csv')
        if len(files) == 0:
            error_msg = "No NDC database file found (prefixed with ndcdb-[date].csv). This means that either " \
                        "the file doesn't exist or was renamed to something else. Please generate that file"
            popupmsg(error_msg)
            print(error_msg)
        else:
            pattern = re.compile(r"^ndcdb-(\d{4}-\d{2}-\d{2}).csv$")
            dates_list = []
            for file in files:
                str_date = pattern.match(file).groups()[0]
                date = datetime.strptime(str_date, '%Y-%m-%d')
                dates_list.append(date)

            formatted_date = datetime.strftime(max(dates_list), '%Y-%m-%d')

            recent_db_file = 'ndcdb-' + formatted_date + '.csv'
            lastupdated_label["text"] = "Using data last updated on: " + formatted_date
            return recent_db_file

    recent_file = find_recent_db()
    df = pd.read_csv(recent_file)
    print('Using db from this file: ', recent_file)

    # print("First entry of ndc package code no hyphen: ", df['NDCPACKAGECODE_nohyphen'][0], ", and type: ", type(df['NDCPACKAGECODE_nohyphen'][0]))
    # print("First entry of ALL_NDC: ", df['ALL_NDC'][0], ", and type: ", type(df['ALL_NDC'][0]))

    # below will be if ndc in df['NDCPACKAGECODE_nohyphen'].values: -- if ndc is found in a list of NDCs with no hyphen

    # 012037086010010821TXZ811R4ZKNC	1723022810MT005
    # if df['ALL_NDC'].apply(lambda x: ndc in x).sum() == 1:
    # str_to_list = lambda x: x.strip('][').split(', ')
    if df['ALL_NDC_NO_HYPHEN'].apply(lambda x: ndc in x).any():
        index = df.loc[df['ALL_NDC_NO_HYPHEN'].apply(lambda x: ndc in x)].index[0]

        # assign "raw_ndc" with hyphens by looking through column with list of all ndcs under a package
        ndc_list = str_to_list(df['ALL_NDC'][index])
        raw_ndc = ""
        for check_ndc in ndc_list:
            if ndc == remove_hyphen(check_ndc):
                raw_ndc = check_ndc

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
            """ changes 10 digit ndc to 11 digit ndc adding the zero to the appropriate place """
            lst = ten_digit.split("-")
            lst[0] = lst[0].zfill(5)
            lst[1] = lst[1].zfill(4)
            lst[2] = lst[2].zfill(2)
            return ''.join(lst)

        ten_dig = eleven_dig(raw_ndc)
        return True, raw_ndc, ten_dig, pack_desc, brand, generic, dosage_form, route, mfg, strength, \
               str_units, pharm_class
    else:
        error_msg = "NDC doesn't exist in database? If drug is new or unofficial (or maybe OTC? not sure if those are" \
                    " in there.., may require updating database?"
        print(error_msg)
        popupmsg(error_msg)


def generate_db(event=None):
    """ Generates the fda ndc database """
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
        dt_lastmodified = datetime(lastmodified[0], lastmodified[1], lastmodified[2]).date().strftime('%Y-%m-%d')

    if files[0] == 'package.txt':
        package = df[0]
        product = df[1]
    else:
        error_msg = 'Double check zip file. Files inside is not match up to pattern "package.txt" and "product.txt"'
        print(error_msg)
        popupmsg(error_msg)
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

    # Create new column of list of NDCs including package and item NDCs

    def make_ndc_list(row):
        pattern = re.compile(r"(\d{5}-\d{4}-\d{1})|(\d{5}-\d{3}-\d{2})|(\d{4}-\d{4}-\d{2})")
        match_iter = pattern.finditer(row['PACKAGEDESCRIPTION'])
        ndc_list = [ndc.group() for ndc in match_iter]
        return ndc_list

    # print("Type of the lambda apply: ", type(joined.apply(lambda row: make_ndc_list(row), axis=1)))
    joined['ALL_NDC_TEMP'] = joined.apply(lambda row: make_ndc_list(row), axis=1)
    joined['ALL_NDC_NO_HYPHEN'] = joined['ALL_NDC_TEMP'].apply(lambda row: ', '.join([remove_hyphen(x) for x in row]))
    joined.drop(columns='ALL_NDC_TEMP', inplace=True)
    joined['ALL_NDC'] = joined.apply(lambda row: ', '.join(make_ndc_list(row)), axis=1)

    joined.to_csv('ndcdb-' + dt_lastmodified + '.csv')
    os.rename(zip_file_name, 'ndctext-' + dt_lastmodified + '.zip')

    generate_completed = "Database generation completed"
    popupmsg(generate_completed)


# saved in case need to use radio buttons in future
# def run(event=None):
#         selection = var.get()
#         if selection == 0:
#         elif selection == 1:
#         elif selection == 2:


def parse_barcode(code):
    """
    Parses barcode. Currently takes four different types of patterns described below. If there is a new format, please
    let me know.

    1. 10 digit NDC. Some drug barcodes such as on unit dose items will be straight NDC. These should all be only 10
    digits only as 11 digit NDCs are not officially sanctioned by the FDA. Also, it's almost impossible to tell
    where the addon zero was placed in 11 digit NDCs which is why this script will almost certainly never be able to
    parse those out.

    2. 12 digit UPC barcodes. These usually have an extra digit before and after the 10 digit NDC.

    3. 16 digit GTIN which comprises of 5 prefix digits and one extra digit after.

    4. Datamatrix 2d barcode which contains GTIN, SN, EXP, LOT either in that order or sometimes GTIN, LOT, EXP, SN.
    This barcode must be scanned by a configurable barcode scanner that can receive a FNC1 signal embedded into the
    barcode and converts it to a \t or tab input.
    """
    # pattern = re.compile(
    #     r"^01\d{3}(\d{10})\d$|^\d(\d{10})\d$|(^\d{10}$)|^(01){1}(\d{14})(21|10){1}(.+?)\t(17){1}(\d{6})(10|21){1}(.+)$")
    # pattern = re.compile(
    #     r"^01\d{3}(\d{10})\d$|^\d(\d{10})\d$|(^\d{10}$)|^(01){1}(\d{14})\ta?(21|10){1}(.+?)\t(17){1}(\d{6})(10|21){1}(.+)$"
    # )
    pattern = re.compile(
        r"^01\d{3}(\d{10})\d$|^\d(\d{10})\d$|(^\d{10}$)|^(01){1}(\d{14})\ta?(21|10){1}(.+?)\t(17){1}(\d{6})(10|21){1}(.+)$|"
        r"^(01){1}(\d{14})(21|10){1}(.+?)\t(17){1}(\d{6})(10|21){1}(.+)$|^(01){1}(\d{14})(17){1}(\d{6})(10){1}(.+)\t(21){1}(.+)$"
        r"^(01)\d{3}(\d{10})\d(17)(\d{6})(10)(.+)$"
    )

    match = pattern.search(code)

    if match:
        if match.group(1) is not None:
            return match.group(1)
        elif match.group(2) is not None:
            return match.group(2)
        elif match.group(3) is not None:
            return match.group(3)
        else:
            # return 2d barcode dictionary
            result_list = list(match.groups())[3:]
            # convert to dictionary
            result_dict = convert_to_dict(result_list)
            result_dict['GTIN'] = result_dict.pop('01')
            result_dict['Exp date'] = result_dict.pop('17')
            result_dict['LOT'] = result_dict.pop('10')
            result_dict['Serial'] = result_dict.pop('21')
            result_dict['Exp date'] = converter(result_dict['Exp date'])
            result_dict['NDC'] = result_dict['GTIN'][3:13]
            return result_dict
    else:
        error_msg = "Not a valid barcode. Remember, NDCs with hyphens are not included in this search since" \
                    "barcodes shouldn't(?) have hyphens in them."
        print(error_msg)
        popupmsg(error_msg)
        return None


def run(event=None):
    """ runs the main program loop. Reads the text entry, parses it, and displays information. """

    raw_entry = barcode_text.get("1.0", "end-1c")

    ndc = parse_barcode(raw_entry)
    if ndc is None:
        popupmsg("Invalid barcode formatting. Please retry or submit a ticket. The format may not be added yet.")
        return 'break'
    elif type(ndc) == str:
        # linear barcode, do all linear barcode stuff
        match, with_hyphen, ndc_11, package, brand, generic, dosage_form, route, mfg, \
        strength, str_units, pharm_class = match_ndc(ndc)

        print('11 digit ndc: ', ndc_11)
        print('Scanned NDC: ', ndc)
        print('NDC with hyphen: ', with_hyphen)
        print('LOT: ', 'no LOT information in this barcode')
        print('Exp date: ', 'no EXP information in this barcode')
        print('Package Description: ', package)
        print('Brand Name: ', brand)
        print('Generic Name: ', generic)
        print('Strength: ', strength, str_units)
        print('Dosage Form: ', dosage_form)
        print('Route: ', route)
        print('Manufacturer/Labeler: ', mfg)
        print('Pharmaceutical Class: ', pharm_class)

        # global ndc_11_result
        ndc_11_result["text"] = ndc_11
        ndc_scanned_result["text"] = ndc
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
        return 'break'

    else:
        # 2d barcode stuff
        # code for 2d barcode below
        # run the program
        # get input barcode from user

        match, with_hyphen, ndc_11, package, brand, generic, dosage_form, route, mfg, \
        strength, str_units, pharm_class = match_ndc(ndc['NDC'])

        # print('Barcode Info ', result_dict)
        print('11 digit ndc: ', ndc_11)
        print('Scanned NDC: ', ndc['NDC'])
        print('NDC with hyphen: ', with_hyphen)
        print('LOT: ', ndc['LOT'])
        print('Exp date: ', ndc['Exp date'])
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
        ndc_scanned_result["text"] = ndc['NDC']
        ndc_hyphen_result["text"] = with_hyphen
        ndc_lot_result["text"] = ndc['LOT']
        ndc_exp_result["text"] = ndc['Exp date']
        ndc_pkg_result["text"] = package
        ndc_brand_result["text"] = brand
        ndc_generic_result["text"] = generic
        ndc_str_result["text"] = strength, str_units
        ndc_dosageform_result["text"] = dosage_form
        ndc_route_result["text"] = route
        ndc_mfg_result["text"] = mfg
        ndc_class_result["text"] = pharm_class
        return 'break'


def popupmsg(msg):
    """ pop up message """
    messagebox.showinfo("!", msg)


def copy_button(label):
    """ copies to clipboard the text displayed to the left of the button """
    clip = Toplevel()
    clip.withdraw()
    clip.clipboard_clear()
    clip.clipboard_append(label.cget("text"))  # Change INFO_TO_COPY to the name of your data source
    clip.update()
    clip.destroy()
    print('Copying: ', label.cget("text"))


def clear(event=None):
    barcode_text.delete(1.0, END)


window = Tk()

# var = IntVar() # used for radio button
# var.set(0) # for radio button

window.title("Barcode Extraction Tool v" + version)
intro_label = Label(window, text="Welcome to the barcode extraction tool. \n Please configure the barcode scanner "
                                 "appropriately to ensure this program works.\n"
                                 "Scan barcode into box below and hit enter or the submit button.")

# barcode_label = Label(window, text = "Scan 2d barcode into this box")
barcode_text = Text(window, width=75, height=2, font=("Helvetica", 10), wrap='none')
# box_barcode = Radiobutton(window, text="2d barcode", value=1, variable=var)
# linear_barcode = Radiobutton(window, text="linear barcode", value=2, variable=var)
proceed_button = Button(window, text="Submit", command=run)
clear_button = Button(window, text="Clear", command=clear)
barcode_text.bind('<Return>', run)
barcode_text.bind('<BackSpace>', clear)
generatedb_button = Button(window, text="Generate DB", command=generate_db)
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

barcode_text.grid(row=1, rowspan=3, columnspan=2, sticky=W + S)
# box_barcode.grid(row=1, column=2, sticky=W)
# linear_barcode.grid(row=2, column=2, sticky=W)
proceed_button.grid(row=3, column=2, sticky=W)
clear_button.grid(row=3, column=3, sticky=W)

# barcode_label.grid(row=1,column=0,sticky=E)

generatedb_button.grid(row=17, column=0, sticky=W)
lastupdated_label.grid(row=17, column=1, sticky=W)
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

barcode_text.focus_set()

window.mainloop()

# random notes here and below.. still cleaning..

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
