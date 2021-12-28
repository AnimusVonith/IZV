#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
from pandas.api.types import CategoricalDtype
import seaborn as sns
import numpy as np
import os

"""
Jakub Adamciak (xadamc07)
IZV PRJ2
"""


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """Loads, edits and returns dataframe used for plotting graphs.
    If verbose is used, writes size before and after using category dtype.
    """
    df = pd.read_pickle(filename)
    if(verbose):
        print("orig_size=%.1f MB" %
              (df.memory_usage(index=True, deep=True).sum() / 1048576))
    for x in df:
        if(x == "region"):
            continue
        if(x == "p2a"):
            df.rename(columns={"p2a": "date"}, inplace=True)
            df["date"] = df["date"].astype("datetime64")
            continue
        cat_type = CategoricalDtype(
            categories=df[x].unique().sort(), ordered=True)
        df[x] = df[x].astype(cat_type)
    if(verbose):
        print("new_size=%.1f MB" %
              (df.memory_usage(index=True, deep=True).sum() / 1048576))
    return df


# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic
def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    """Vykreslenie grafu z dodaného dataframu pre regiony:
    PHA, STC, JHC, PLK podla druhu cesty.
    """
    regions = ['PHA', 'STC', 'JHC', 'PLK']
    hf = df.copy()
    hf = hf[hf["region"].isin(regions)]

    hf["p21"].replace([1, 2, 3, 4, 5, 6, 0],
                      ["dvoupruhová", "třípruhová",
                       "čtyřpruhová", "čtyřpruhová",
                       "vícepruhová", "rychlostní komunikace",
                       "žádná z uvedených"], inplace=True)

    sns.displot(data=hf, x="region", hue="region", col="p21",
                col_wrap=3, height=4,
                facet_kws=dict(sharey=False, sharex=False))

    if(fig_location is not None):
        plt.savefig(fig_location)

    if(show_figure):
        plt.show()


# Ukol3: zavinění zvěří
def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """Vykreslenie grafu z dodaného dataframu pre regiony:
    PHA, STC, JHC, PLK podla druhu zavinenia zvery alebo vodica.
    """
    regions = ['PHA', 'STC', 'JHC', 'PLK']
    hf = df.copy()
    hf = hf[hf["region"].isin(regions)]
    hf = hf[hf["p58"] == 5]
    hf = hf[hf["date"].dt.year != 2021]
    hf["mesiac"] = hf["date"].dt.month
    hf["p10"].replace([1, 2, 3, 4, 5, 6, 7, 0],
                      ["řidičem", "řidičem",
                       "jiné", "zvěří", "jiné",
                       "jiné", "jiné", "jiné"],
                      inplace=True)

    g = sns.displot(data=hf, x="mesiac", hue="p10",
                    col="region", col_wrap=2,
                    height=4, multiple="dodge",
                    facet_kws=dict(sharey=False, sharex=False))
    g.set(xticks=hf["mesiac"].unique())

    if(fig_location is not None):
        plt.savefig(fig_location)

    if(show_figure):
        plt.show()


# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    """Vykreslenie grafu z dodaného dataframu pre regiony:
    PHA, STC, JHC, PLK podla druhu pocasia.
    """
    regions = ['PHA', 'STC', 'JHC', 'PLK']
    hf = df.copy()
    hf = hf[hf["region"].isin(regions)]
    hf = hf[hf["p18"] != 0]
    hf["p18"].replace([1, 2, 3, 4, 5, 6, 7],
                      ["neztížené", "mlha",
                       "mrholení", "déšť",
                       "sněžení", "námraza",
                       "vichřice"], inplace=True)
    hf.rename(columns={"p18": "podminky"}, inplace=True)
    hf = hf[hf["date"] < "2021-01-01"]
    hf["mesiac a rok"] = pd.to_datetime(
        df["date"].dt.year.astype(str) + "-" +
        df["date"].dt.month.astype(str), format="%Y-%m")
    hf = hf.sort_values("mesiac a rok")

    hf = hf.groupby(["mesiac a rok", "region", "podminky"]
                    ).size().reset_index(name="count")

    g = sns.relplot(data=hf, x="mesiac a rok",
                    y="count", col="region", kind="line",
                    hue="podminky", col_wrap=2,
                    facet_kws=dict(sharey=False, sharex=False))

    if(fig_location is not None):
        plt.savefig(fig_location)

    if(show_figure):
        plt.show()


if __name__ == "__main__":
    """Testovanie funkcií
    Vykreslenie, ulozenie a verbose mode je zapnutý."""
    df = get_dataframe("accidents.pkl.gz", True)
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
    plot_animals(df, "02_animals.png", True)
    plot_conditions(df, "03_conditions.png", True)
