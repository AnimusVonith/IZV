#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#xadamc07, Jakub Adamciak
import numpy as np
import argparse
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as clr
# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader


def plot_stat(data_source,
              fig_location=None,
              show_figure=False):
    reg_arr = []

    #vyberieme si unikatne regiony a zistime ich zaciatocny a konecny index
    for reg in np.unique(data_source["region"]):
        reg_arr.append([np.where(data_source["region"]==reg)[0][0], np.where(data_source["region"]==reg)[0][-1], reg])

    #vytvorime holder na finalne hodnoty (sucty)
    end = np.zeros((6, 14), dtype=np.int32)

    #iterujeme len cez regiony a ziskame county pre vsetky unikatene hodnoty v danom rozmedzi
    for i,reg_i in enumerate(reg_arr):
        uniques, counts = np.unique(data_source["p24"][reg_i[0]:reg_i[1]], return_counts=True)
        for n,uni in enumerate(uniques): #ulozenie danych countov ku prislusnemu regionu a unikatnej hodnote
            end[int(uni)-1][i] = counts[n]
    
    #nastavenie labelov a tickov
    x_labelings = np.unique(data_source["region"])
    y_labelings = ["Přerušovaná žlutá", "Semafor mimo provoz", "Dopravní značky", "Přenosné dopravní značky", "Nevyznačená", "Žádná úprava"]
    x_tickings = np.array(range(np.array(x_labelings).size))
    y_tickings = np.array(range(np.array(y_labelings).size))

    #inicializacia figure a subplotov (2 riadky, 1 stlpec o velkosti 11x7(cm?))
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(11,7))

    #nastavenie danych parametrov grafov aby vyzerali ako v zadani
    ax1.set_title("Absolutně")
    im1 = ax1.imshow(end, cmap="viridis", norm=clr.LogNorm(vmin=1, vmax=10**5))
    ax1.set_xticks(x_tickings)
    ax1.set_xticklabels(x_labelings)
    ax1.set_yticks(y_tickings)
    ax1.set_yticklabels(y_labelings)
    clrb1 = fig.colorbar(im1, ax=ax1)
    clrb1.ax.set_ylabel("Počet nehod")

    end_norm = []

    #normalizacia riadkov, iterovanie len cez line vo vypocitanych datach (14 riadkov) (*100 = %)
    for line in end:
        end_norm.append(np.array(line/np.sum(line))*100)

    end_norm = np.array(end_norm, dtype=np.float32)
    end_norm[end_norm == 0] = np.nan
    #nuly nahradime nanmi aby sa nevykreslovali

    #nastavenia druheho grafu
    im2 = ax2.imshow(end_norm, cmap="plasma", vmin=0)
    ax2.set_title("Relativně vůči příčine")
    ax2.set_xticks(x_tickings)
    ax2.set_xticklabels(x_labelings)
    ax2.set_yticks(y_tickings)
    ax2.set_yticklabels(y_labelings)
    clrb2 = fig.colorbar(im2, ax=ax2)
    clrb2.ax.set_ylabel("Podíl nehod pro danou příčinu [%]")

    #ak je fig_location zadany, ulozit do daneho miesta 
    if fig_location:
        plt.savefig(fig_location)
    #ak je show_figure true tak vykreslit grafy
    if show_figure:
        plt.show()

def main():
	#parsovanie argumentov
    parser=argparse.ArgumentParser()
    parser.add_argument("--fig_location", help="path and filename where to save stats", action="store")
    parser.add_argument("--show_figure" , help="use if you want to show stats" , action="store_true")
    args = parser.parse_args(sys.argv[1:])
    
    downloader = DataDownloader()
    holder=downloader.get_dict([])

    plot_stat(holder, args.fig_location, args.show_figure)
    return
    
if __name__ == '__main__':
    main()