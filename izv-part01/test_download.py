#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tqdm import tqdm
import numpy as np
import zipfile
import requests
import re
import os
import io
import csv
import gzip
import pickle

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).

def sortMonth(val):
    return val[0]

class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions  Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
        "00" : "PHA",
        "01" : "STC",
        "02" : "JHC",
        "03" : "PLK",
        "04" : "ULK",
        "05" : "HKK",
        "06" : "JHM",
        "07" : "MSK",
        "14" : "OLK",
        "15" : "ZLK",
        "16" : "VYS",
        "17" : "PAK",
        "18" : "LBK",
        "19" : "KVK",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename

        """
        __init__(self, url=”https://ehw.fit.vutbr.cz/izv/”, folder=”data”, cache_filename=”data_{}.pkl.gz”)
            inicializátor - obsahuje volitelné parametry:
            ○ url - ukazuje, z jaké adresy se data načítají. Defaultně bude nastavený na
                výše uvedenou URL.
            ○ folder - říká, kam se mají dočasná data ukládat. Tato složka nemusí na
                začátku existovat!
            ○ cache_filename - jméno souboru ve specifikované složce, které říká, kam
                se soubor s již zpracovanými daty z funkce get_dict bude ukládat a odkud
                se budou data brát pro další zpracování a nebylo nutné neustále stahovat
                data přímo z webu. Složené závorky (formátovací řetězec) bude nahrazený
                tříznakovým kódem (viz tabulka níže) příslušného kraje. Pro jednoduchost
                podporujte pouze formát “pickle” s kompresí gzip.

        """

    def download_data(self):
        r = requests.get(self.url)
        found_zips = re.findall(r"\'.{1,30}?\.zip\'", r.text)
        os.makedirs(self.folder, exist_ok=True)
        downloaded = os.listdir(self.folder)
        for find in found_zips:
            name = find.strip('\'').split('/')[-1]
            if name in downloaded:
                continue
            d = requests.get(self.url+str(find.strip("'")), stream=True)
            with open(f"{self.folder}/{name}", "wb") as handle:
                for data in tqdm(d.iter_content(chunk_size=1024)):
                    handle.write(data)
        self.downloaded = [f for f in os.listdir(self.folder) if f.endswith('.zip')]
        """
        download_data(self)
            metoda stáhne do datové složky folder všechny soubory s daty z adresy url
            definované v inicializátoru. Je nutné načíst adresy ZIP souborů z HTML souboru z
            uvedené URL. Není dovoleno přímo odhadovat názvy ZIP souborů, mít adresy
            uložené přímo v kódu atd,

        """

    def parse_region_data(self, region):
        self.download_data()

        if (region == []) or (region is None):
            region = "all"

        done_years = []
        list_of_dates = []
        zips_to_do = []

        for dw_zip in self.downloaded:
            x = [re.findall(r'\d+', dw_zip), dw_zip]
            if len(x[0]) == 1:
                done_years.append(x[0])
                zips_to_do.append(x[1])
            else:
                if x[0] in done_years:
                    continue
                else:
                    list_of_dates.append(x)

        list_of_dates.sort(key=sortMonth,reverse=True)
        for date in list_of_dates:
            if [date[0][-1]] in done_years:
                list_of_dates.remove(date)
                continue
            else:
                done_years.append([date[0][-1]])
                zips_to_do.append(date[1])

        for downloaded_zip in zips_to_do:
            with zipfile.ZipFile(f"{self.folder}/{downloaded_zip}", 'r') as zf:
                for file_name in zf.namelist():
                    region_name = self.regions.get(file_name.split('.')[0], None)
                    if (region != "all") and (region_name != region):
                        continue
                    elif region_name is None:
                        continue
                    print(f"  {file_name}")
                    with zf.open(file_name, 'r') as f:
                        reader = csv.reader(io.TextIOWrapper(f, "cp1250"), delimiter=';', quotechar='"')
                        for row in tqdm(reader):
                            self.all_values[self.n] = np.array(row + [region_name], dtype=None)
                            self.n+=1
        
        
        """
        parse_region_data(self, region)
            pokud nejsou data pro daný kraj již stažena ve složce folder, stáhnou se voláním
            download_data. Poté se pro daný region specifikovaný tříznakovým kódem (viz
            tabulka níže) provede vždy (tj. data nejsou cachována) extrakce dat do slovníku
            (dict), kde klíčem bude řetězec odpovídající kódu sloupce (např. p1, p13b, p51, ..)
            a hodnotou pole NumpyArray, tzn. dle následujícího schematu
            dict(str: np.ndarray)
            Počet položek (klíčů) tohoto slovníku bude odpovídat počtu hlaviček plus navíc
            jeden nový klíč “region”, který bude obsahovat NumPy pole, ve kterém se bude
            opakovat tříznaký kód kraje.
            Musí platit to, že všechny hodnoty (tj. NumPy pole) ve slovníku mají stejný rozměr
            (včetně regionu). Pro každý sloupec zvolte vhodný datový typ (t.j. pokud je to
            možné, snažte se vyhnout textovým řetězcům a použít numerické typy, vyřešte
            desetinnou čárku, nepoužívejte PyObject atp.). Při otevírání souboru nezapomeňte
            specifikovat kódování: open(f, 'r', encoding="cp1250")
        """

    def get_dict(self, regions=None):
        self.all_values = np.ndarray((1000000, 65), dtype="<U30")
        self.n = 0
        holder = []



        if (regions == []) or (regions is None):
            print("parse all")
            self.parse_region_data(regions)
            self.all_values = self.all_values[:self.n]
            self.reg_dict = dict(zip(self.headers+["region"], self.all_values[:self.n].T))
            with gzip.open(self.cache_filename.format("all"), "wb", compresslevel=7) as f:
                pickle.dump(self.reg_dict, f)
            self.all_values = self.all_values[:self.n]
            self.reg_dict = dict(zip(self.headers+["region"], self.all_values.T))
        elif type(regions) is list:
            print("parse regions")
            for region in regions:
                print(f"parsing {region}")
                self.parse_region_data(region)
                self.reg_dict = dict(zip(self.headers+["region"], self.all_values[:self.n].T))
                self.x = filter(lambda c: c["region"] == region, self.reg_dict)
                with gzip.open(self.cache_filename.format(region), "wb", compresslevel=7) as f:
                    pickle.dump(self.x, f)
            self.all_values = self.all_values[:self.n]
            self.reg_dict = dict(zip(self.headers+["region"], self.all_values.T))
        else:
            #ERR
            return None

        for region in regions:
            with gzip.open(self.cache_filename.format(region), "rb", compresslevel=7) as f:
                self.reg_dict = pickle.load(f)

        print(self.reg_dict)

        """
        get_dict(self, regions = None)
            Vrací zpracovaná data pro vybrané kraje (regiony). Argument regions umožňuje
            specifikovat kraje, pro které chceme výsledek vrátit. Jedná se o seznam (list)
            obsahující třípísmenné kódy. Pokud je použito None nebo je seznam prázdný,
            zpracují se všechny kraje včetně města Prahy. Výstupem je složení výstupů funkce
            parse_region_data pro všechny kraje do jednoho asociativního pole (klíčem
            bude řetězec hlavičky např. p1, p15, region,... a hodnotami bude vždy np.ndarray
            - všechny o stejném rozměru).
            Metoda pracuje nad extrahovanými daty, které získá voláním metody
            parse_region_data Abychom co nejvíce zefektivnili manipulaci s daty a vyhnuli
            se opakovanému zpracování data, budou extrahovaná data uchovávána v paměti
            
            (v zvoleném atributu instance třídy) a současně ukládána do pomocného cache
            souboru pomocí následujícího schématu:
                ○ pokud už je výsledek načtený v paměti (tj. dostupný ve vámi zvoleném
                    atributu), vrátí tuto dočasnou kopii
                ○ pokud není uložený v paměti, ale je již zpracovaný v cache souboru, tak
                    načte výsledek z cache, uloží jej do atributu a vrátí.
                ○ jinak se zavolá funkce parse_region_data, výsledek volání se uloží do
                    cache, poté do paměti a výsledek vrátí

        """

def main():
    print("vypsani zakladnich informaci :-)")
    """
    Pokud bude skript spuštěný přímo (tj. nebude importovaný jako modul), stáhněte data pro 3
    vámi vybrané kraje (s využitím funkce get_dict) a vypište do konzole základní informace o
    stažených datech (jaké jsou sloupce, počet záznamů a jaké kraje jsou v datasetu).
    """
# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)


if __name__ == '__main__':
    main()