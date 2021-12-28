#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#xadamc07, Jakub Adamciak
import numpy as np
import zipfile
import requests
import re
import os
import io
import csv
import gzip
import pickle


def sortMonth(val):
    return val[0][0]


class DataDownloader:


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
    }

    #slovnik na prevod nazvu suboru na skratku regionu
    reverse_regions = {
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


    def download_data(self):
        r = requests.get(self.url)
        found_zips = re.findall(r"\'.{1,30}?\.zip\'", r.text) #najdem vsetky .zip z url kodu
        os.makedirs(self.folder, exist_ok=True)
        downloaded = os.listdir(self.folder)
        for find in found_zips:
            name = find.strip('\'').split('/')[-1]
            if name in downloaded:
                continue
            d = requests.get(self.url+str(find.strip("'")), stream=True) #stahovanie vsetkych najdenych .zip (stream - chunk size 1024)
            with open(f"{self.folder}/{name}", "wb") as handle:
                for data in d.iter_content(chunk_size=1024):
                    handle.write(data)
        self.downloaded = [f for f in os.listdir(self.folder) if f.endswith('.zip')] #ulozenie nazvy stiahnutych zipov do premennej (list)
        return self.downloaded


    def parse_region_data(self, region):
        self.download_data()
        done_years = []
        list_of_dates = []
        zips_to_do = []
        for dw_zip in self.downloaded:
            x = [re.findall(r'\d+', dw_zip), dw_zip] #najdenie a ulozenie cisiel z nazvov zipov a ulozenie do listu spolu s nazvom zipu
            if len(x[0]) == 1: #ak je v liste iba rok, to znamena ze je to posledny zaznam, summary roku - pridame do splnenych rokov a nazov do listu so zipmi, ktore budeme spracovavat
                done_years.append(x[0])
                zips_to_do.append(x[1])
            else:
                if x[0] in done_years: #ak sa rok nachadza v splnenych rokoch, skip
                    continue
                else:
                    list_of_dates.append(x) #zvysne pridame do druheho listu - v retrospektive, mohli sme proste mazat prvky v tom povodnom
        list_of_dates.sort(key=sortMonth,reverse=True) #sortneme datumy podla mesiacov, a zoberieme len najvyssie mesiace pre kazdy rok
        for date in list_of_dates:
            if [date[0][-1]] in done_years:
                list_of_dates.remove(date)
                continue
            else:
                done_years.append([date[0][-1]])
                zips_to_do.append(date[1])

        for downloaded_zip in zips_to_do: #prejdeme najdenymi zipmi
            with zipfile.ZipFile(f"{self.folder}/{downloaded_zip}", 'r') as zf:
                for file_name in zf.namelist():
                    region_number = file_name.split('.')[0]
                    region_name = self.reverse_regions.get(file_name.split('.')[0], None)
                    if region_name != region: #ak aktualny zip nie je zip pre region ktory spracuvavame, skip
                        continue
                    elif region_name is None: #ak region neexistuje v nasom slovniku - napr CHODCI
                        continue
                    with zf.open(file_name, 'r') as f:
                        reader = csv.reader(io.TextIOWrapper(f, "cp1250"), delimiter=';', quotechar='"') #musime pouzit iterovanie namiesto genfromtxt, kvoli zlym datam, potrebujeme identifikovat delimiter v quotechars - aby ho nebralo
                        for row in reader:
                            self.all_values[self.n] = np.array(np.array(row + [region])) #ulozenie do arrayu
                            self.n+=1
        self.all_values = np.where(self.all_values=='', '0', self.all_values) #ocistenie dat
        return self.all_values
        

    def get_dict(self, regions=None):
        self.all_values = np.ndarray((1000000, 65), dtype="U20") #predalokovany array, neskor ho zrezeme podla toho, kolko zaznamov budeme mat
        dump_load_holder = []
        self.n = 0

        if (regions == []) or (regions is None):
            regions=list(self.regions.keys())
        type_holder = []
        mod_headers = self.headers + ["region"]
        if type(regions) is list:
            for region in regions:
                try:
                    with gzip.open(f"{self.folder}/{self.cache_filename.format(region)}", "rb", compresslevel=7) as f: #load cache
                        if type(dump_load_holder) is list:
                            dump_load_holder = pickle.load(f)
                        else:
                            dump_load_holder = np.vstack([dump_load_holder, pickle.load(f)])
                except FileNotFoundError:
                    self.parse_region_data(region)
                    holder = np.array([f for f in self.all_values[:self.n] if f[-1]==region])
                    with gzip.open(f"{self.folder}/{self.cache_filename.format(region)}", "wb", compresslevel=7) as f: #save cache po spracovani
                        pickle.dump(holder, f)
            self.all_values = self.all_values[:self.n] #orezanie predalakovaneho arrayu
            if self.all_values.size == 0: #ak mam v arrayi 0 zaznamov (vsetko sme zobrali z cache) tak prepiseme, else pridame (vertical stack)
                self.all_values = dump_load_holder
            elif np.array(dump_load_holder).size != 0:
                self.all_values = np.vstack([self.all_values, dump_load_holder])
            self.all_values=self.all_values.T #transpone
            self.reg_dict = dict(zip(self.headers+["region"], self.all_values)) #vytvorenie slovnika
        else: #ak regions nie je list - zly vstup - return None
            return None
        return self.reg_dict

def main():
    downloader = DataDownloader()
    holder=downloader.get_dict(["PHA", "STC", "KVK"])
    #vypis zakladnych udajov pre ^------^------^--- regiony
    print(f"stlpce v zaznamoch: {[key for key in holder.keys()]}")
    print(f"počet záznamov: {holder['region'].size}")
    print(f"kraje v datasete: {np.unique(holder['region'])}")

if __name__ == '__main__':
    main()