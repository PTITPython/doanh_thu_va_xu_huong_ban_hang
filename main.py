import os
import sys
import pandas as pd
import xu_li_du_lieu as RetailData 


RAW_DATA = "\Data\raw_data.csv"
CLEAN_DATA = "\Data\clean_data.csv"

def tieu_de(line):
    print("\n" + "=" * 70)
    print(line)
    print("=" * 70)

def main():
    tieu_de("1.DOC VA KIEM TRA DU LIEU")
    du_lieu = RetailData(RAW_DATA)
    

