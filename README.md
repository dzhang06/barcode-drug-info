# barcode-drug-info
Get drug data from 2d and linear barcodes on drug packaging 

Will fill out readme later...

### Sample 2d barcode examples:

*note: Must configure barcode scanner to read FNC1 codes inside the barcode and program to add tab*

- ``012037086010010821TXZ811R4ZKNC	1723022810MT005`` 
    - azithromycin 500 mg box
- ``01003633232956152155656222103517	17210630106019894`` 
    - vanco 5 gm vial box 363323295615 upc
- ``010030049052083621303978156223	172207311033006308`` 
    - pen g 5 mil unit vial box
- ``012037086012130121F83768X2HM3P	17220131109B08TQ`` 
    - zosyn 3.375 gm vial box (01)20370860121301 upc
- ``01003442062511022126386940975151	1722102010P100149569``
- ``010036068740583421100000968736	172202281020B88``
- ``010036846233190321EAEV63DY6T9T	172112311019200264``
- ``01003666851001152120000000010964	1721103110KC7045``
- ``01203633232842002140366616241856	1721022810167918``
- ``01003633232956152116749482636589	17210630106019894``
- ``012037086012130121FZ7N875BGT7Z	17220131109B08TQ``
- *linear barcodes to follow*


2d Barcodes are broken down into components:

- 01: GTIN
    - The GTIN is comprised of 3 prefix digits, a 10 digit NDC, and a 1 digit suffix. The NDC can be extracted from 
    this barcode component
- 21: serial number
    - The serial number. I have never really figured out a practical use. Possibly for internal tracking purposes?
- 17: expiration date
    - Expiration date formatted as YYMMDD. 
    - Sometimes, the day component will be 00 which is officially discouraged but 
    generally means end of that month. I recall seeing this very occasionally on the human-readable portion of the 
    barcode on the box but don't think it happens anymore as part of the actual barcode.
- 10: LOT
    - Self explanatory
    
Here are a few examples of the above broken down into its components:

- ``01  2 03 7086010010 8  21  TXZ811R4ZKNC   17 230228 10 MT005`` 
- ``01  0 03 6332329561 5  21  55656222103517 17 210630 10 6019894``  -- 363323295615 upc
- ``01  0 03 0049052083 6  21  303978156223   17 220731 10 33006308`` 
- ``01  2 03 7086012130 1  21  F83768X2HM3P   17 220131 10 9B08TQ`` 
- ``01  0 03 1234567890 6  21  SN345678       17 181127 10 LN145``

### General overview of codes

This is the most important resource I used to learn about how to deconstruct the barcodes. Very useful.

https://www.cardinalhealth.com/content/dam/corp/web/documents/data-sheet/Cardinal-Health-barcode-quick-start-guidelines.pdf

### Complicated hiccup

One issue I ran into when I originally started to work on this was how to parse those four components of the barcode 
into their individual components. First I tried isolating out the 01, 21, 17, and 10 codes and then realized that these 
2 digit combinations are not exactly unique and could appear in the middle of the components I was looking for. 

What I ended up finding out (after messing with figuring out that GTINs were exactly 14 characters long and expiration 
dates were exactly 6 digits long) was that coded into the datamatrix barcode is a barcode scanner-readable FNC1 signal 
that cleaves the data into two halves, the 01 and 21 (GTIN and SN) half and 17 and 10 (EXP and LOT) half. This basically 
solves the problem where you find '17' characters inside the SN and '10' characters inside the EXP. 

The scanner I use is a Honeywell scanner. I stumbled upon this nifty example guide on how to program it to show the 
TAB input from the scanner in place of the FNC1 signal. This is why the sample barcode strings above have a gap in the 
middle.

https://support.honeywellaidc.com/s/article/How-to-substitute-the-FNC1-GS-characters-in-GS1-128-UCC-EAN128-or-GS1-Datamatrix-bar-code

For anyone else reading this, you may need to find a way to do this with your own scanners before this script works for
you. 
