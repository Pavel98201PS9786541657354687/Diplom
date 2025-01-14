import pyshark, os, shutil, csv, json, pathlib
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
from pathlib import Path

class actions_file():
    """Класс управления файлами"""

    def __init__(self):
        super().__init__()

        self.path()

    def path():
          myself = Path(__file__).resolve()
          res = myself.parents[0]
          return res

    def list_files():
        dirname = str(f"{actions_file.path()}/files_for_bd")
        dirfiles = os.listdir(dirname)
        fullpaths = map(lambda name: os.path.join(dirname, name), dirfiles)
        files = []
        for file in fullpaths:
            if os.path.isfile(file):
                filename = file.split("/",7)[7] 
                files.append(filename)

        return files

    def save_new_file(old_path, new_path):
        shutil.copyfile(old_path, new_path)

    def remove_file(filename):
        new_path = str(f"{actions_file.path()}/files_for_bd/{filename}")
        os.remove(new_path)

    def parameters_file(filename):
        """Метод для определения основных параметров файла"""
        filename, format_file = os.path.splitext(filename)
        return(format_file)

    def read_file(filename):
        """Метод для прочтения файла"""
        if actions_file.parameters_file(filename) == '.csv':
            df = pd.read_csv(f'{filename}', sep=';')
        elif actions_file.parameters_file(filename) == '.xlsx':
            df = actions_file.read_excell(filename)
        elif actions_file.parameters_file(filename) == '.pcap':
            df = actions_file.read_pcap(filename)
            df = actions_file.build_pivot_table(df)
        elif actions_file.parameters_file(filename) == '.txt':
            df = actions_file.read_txt(filename)
            df = actions_file.build_pivot_table(df)
        elif actions_file.parameters_file(filename) == '.json':
            df = actions_file.read_json(filename)
        else:
            df = pd.DataFrame()
        return df

    def read_pcap(path):

        packets = pyshark.FileCapture(path,use_json=True,include_raw=True)
        a = 0
        list_line = []
        dict_packets = {}
        df = pd.DataFrame()
        result = pd.DataFrame()

        for j in packets:
            pack = j
            for line in pack:
                list_line.append(line)
            dict_packets[0] = list_line
            a += 1
            list_line = []
            df = pd.DataFrame.from_dict(dict_packets[0])
            df['packet'] = a
            result = pd.concat([result, df]).reset_index(drop=True)
            df = pd.DataFrame()

        del df
        del list_line
        del dict_packets
        del a

        result = result.rename(columns={
            0 : 'information'
            }) 

        more_information = result.information.astype(str).str.split(r":\n", expand=True).stack()\
            .reset_index().drop(columns={
                'level_1'
                }).rename(columns={
                    0:'information'
                })

        result = result.reset_index().rename(columns={'index':'level_0'})
        result['layers'] = result.information.astype(str).str.split(":", expand=True)[0]
        merge = pd.merge(result[['layers','packet','level_0']], 
            more_information, on='level_0', how='left')

        del result
 
        more_information = merge['information'].astype(str).str.replace(r"\t","").str.split(r"\n", expand=True)\
            .stack()\
            .reset_index().drop(columns={
                'level_1'
                }).rename(columns={
                    0:'information'
                })

        merge = merge.drop(columns={'level_0'}).reset_index().rename(columns={'index':'level_0'})
        result = pd.merge(more_information, merge[['level_0','packet', 'layers']]
            , on='level_0', how='left')

        del merge
        del more_information

        srez = result.loc[result.information.astype(str).str.contains(":")]

        del result

        srez['flag'] = srez.information.astype(str).str.split(":",expand=True)[0]
        srez['value'] = srez.information.astype(str).str.split(":",expand=True)[1]

        srez = srez.drop(columns={
            'information',
            'level_0',
            })

        srez = srez[['packet','layers', 'flag', 'value']]

        return srez

    def read_csv(filename):
        df = pd.read_csv(f'{filename}', sep=';')
        df['need'] = "csv"
        return df

    def read_excell(filename):
        df = pd.read_excel(f'{filename}')
        df['need'] = 'excel'
        return df

    def read_json(path):
        try:
            #Загрузка дамп-файла
            df = pd.read_json(path, orient='records')

            #нормализация из json в dataframe
            data=df._source
            df3 = pd.DataFrame.from_dict(json_normalize(data), orient='columns')

            df = df3.copy()
            del df3
            del data

        except:
            try:
                packets = pyshark.FileCapture(path,use_json=True,include_raw=True)
                df = pd.DataFrame()
            except:
                df = pd.DataFrame()

        return df

    def read_txt(filename):
        # Чтение файла
        with open(filename) as f:
            packets = f.readlines()

        df = pd.DataFrame()
        df['need'] = packets

        del packets

        # формирование packet
        df['Frame'] = ""
        df.loc[df.need.str.contains(r"Frame \d{1,}:"), 'Frame'] = df.need.str.split(":", expand=True)[0]
        df.loc[df.need.str.contains(r"Frame \d{1,}:"), 'packet'] = df.Frame.str.split(" ", expand=True)[1]
        df = df.drop(columns={"Frame"})
        df['packet'] = df['packet'].fillna(method='ffill')
        df['packet'] = df['packet'].astype(int)
        df = df[df.need != "\n"].reset_index(drop=True)

        # Форматирование layers
        df['layers'] = None
        df.loc[(~df.need.str[0].isin([" ", "["])) & (~df.need.str.contains(r"Frame \d{1,}:")), 'layers'] = \
            df.loc[(~df.need.str[0].isin([" ", "["])) & (~df.need.str.contains(r"Frame \d{1,}:")), 'need'].str.split(",",
                expand=True)[0]
        df.loc[df.need.str.contains(r"Frame \d{1,}:"), 'layers'] = "Frame"
        df.loc[df.layers.notna(), 'need'] = df.loc[df.layers.notna(), 'need'].str.split(",", 1, expand=True)[1]
        df = df[~df.need.isna()]
        df.layers = df.layers.fillna(method='ffill')

        # Разделение строки по запятым на несколько строк
        df["count_z"] = df.need.str.count(",")
        df.loc[df.need.str.contains("Arrival Time"), "count_z"] = 0
        srez1 = df[df.count_z == 0]["need"].reset_index().rename(columns={'index': "level_0"})
        srez2 = df[df.count_z > 0].need.str.split(",", expand=True).stack().reset_index().drop(columns="level_1").rename(
            columns={
                0: 'need'
            })
        srez = pd.concat([srez1, srez2])
        del srez1
        del srez2

        for_merge = df[["packet", "layers"]].reset_index().rename(columns={"index": "level_0"}).copy()
        df = pd.merge(srez, for_merge, on="level_0", how="left").drop(columns={"level_0"})[["packet", "layers", "need"]]

        del srez
        del for_merge

        # Разделение need на flag и value
        df["count_d"] = df.need.str.count(":")
        df[['flag', 'value']] = df['need'].str.split(":", 1, expand=True).rename(columns={
            0: "flag",
            1: "value"
        })
        df['flag'] = df['flag'].str.replace(r"\n", "", regex=True)
        df['value'] = df['value'].str.replace(r"\n", "", regex=True)
        df = df[df.value.notna()]
        df = df.drop(columns={'need', 'count_d'})

        for i in df.columns:
            try:
                df[i] = df[i].str.replace(r"\s{1,}", " ")
            except:
                continue
            try:
                df.loc[df[i].str[0] == " ", i] = df[i].str[1:]
            except:
                continue

        return df

    def save_csv(df, new_filename):
        df.to_csv(f"{actions_file.path()}/files_for_bd/{new_filename}.csv",\
         index=False)

    def build_pivot_table(df):

        df['layers_flag'] = df['flag'].astype(str)

        df['layers_flag'] = df['layers_flag'].str.replace("[","", regex=True)

        pivot_table_test = pd.pivot_table(data=df, columns='layers_flag',\
            index='packet', values='value', \
            aggfunc=lambda x : x, fill_value=0).reset_index().rename(\
            columns={'packet':'Frame number'}, index={'layers_flag':'index'})

        del df

        df = pivot_table_test.copy()
        del pivot_table_test

        for i in df.columns:
            df = actions_file.columns_for_float(df, i) 
    
        return df

    def columns_for_float(df, column):
        try:
            df[column] = df[column].astype(float)
        except:
            pass
        return df

    def control_load_files(old_filename, new_filename):
        df = actions_file.read_file(old_filename)
        try:
            actions_file.save_csv(df, new_filename)
            symbol = 0
        except:
            symbol = 1
        return symbol