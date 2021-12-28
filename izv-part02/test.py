#!/usr/bin/env python3

"""
Skript pro rychle otestovani projektu, zda splnuje podminky.
Poustet v cistem adresari, kde je pouze vas odevzdavany soubor
`analysis.py`. 

Vysledkem by mely byt citelne obrazky ve formatu PNG.

Skript si sam stahne pozadovany soubor accidents.pkl.gz (neni
soucasti projektu).
"""

import os
import shutil
import requests
import analysis
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")


def download_file(url):
    """ Downloads file from the url """
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename


def report(name: str, cond: bool):
    """ Reports line with name and success / fail notification depending on condition """
    value = "[\033[92msuccess\033[0m]" if cond else "[\033[91mfail\033[0m]"
    print(f"{name: <30} {value}")


def main():
    download_file("https://ehw.fit.vutbr.cz/izv/accidents.pkl.gz")
    df = analysis.get_dataframe("accidents.pkl.gz")
    assert df.shape[0] > 570000, "wrong number of rows in the dataframe"
    assert df.shape[1] > 60, "wrong number of columns in the dataframe"

    report("get_dataframe", type(df) is pd.DataFrame)

    analysis.plot_roadtype(df, "f_roadtype.png")
    report("plot_roadtype", os.path.exists("f_roadtype.png"))

    analysis.plot_conditions(df, "f_conditions.png")
    report("plot_conditions", os.path.exists("f_conditions.png"))

    analysis.plot_animals(df, "f_animals.png")
    report("plot_animals", os.path.exists("f_animals.png"))


if __name__ == "__main__":
    main()