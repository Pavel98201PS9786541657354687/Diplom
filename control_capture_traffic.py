import pyshark, json, re, netifaces, os
import pandas as pd
from pandas.io.json import json_normalize
from control_actions_files import actions_file
from connect_db import control_db

class control_capture():

     def trasnform_to_mode_monitor(int_cap):
          os.system(f"sudo ifconfig {int_cap} down")
          os.system(f"sudo iwconfig {int_cap} mode monitor")
          os.system(f"sudo ifconfig {int_cap} up")
          #print(f"ИНтерфейс {int_cap} переведён в режим мониторинга")

     def capture(int_cap, seconds):
          capture = pyshark.LiveCapture(interface=int_cap)
          capture.sniff(timeout=seconds)
          return capture

     def timer_for_capture(int_cap, seconds):
          capture = pyshark.LiveCapture(interface=int_cap)
          capture.sniff(timeout=seconds)
          return capture

     def transform_traffic(packets):
          
          try:
               a = 0
               list_line = []
               dict_packets = {}
               df = pd.DataFrame()
               result = pd.DataFrame()
               for j in range(len(packets)):
                    pack = packets[j]
                    for line in pack:
                         list_line.append(line)
                    dict_packets[0] = list_line
                    a += 1
                    list_line = []
                    df = pd.DataFrame.from_dict(dict_packets[0])
                    df['packet'] = a
                    result = pd.concat([result, df]).reset_index(drop=True)

               del df
               del list_line
               del dict_packets
               del a

               result = result.rename(columns={
                    0 : 'information'
                    })
               
               more_information = result['information'].astype(str).str.split(r":\n", expand=True).stack()\
                    .reset_index().drop(columns={
                         'level_1'
                         }).rename(columns={
                         0:'information'
                         })

               result = result.reset_index().rename(columns={'index':'level_0'})
               result['layers'] = result['information'].astype(str).str.split(":", \
                    expand=True)[0]
               merge = pd.merge(result[['layers','packet','level_0']], 
                    more_information, on='level_0', how='left')

               del result
 
               more_information = merge['information'].astype(str).\
               str.replace(r"\t","", regex=True).str.split(r"\n", expand=True)\
                    .stack()\
                    .reset_index().drop(columns={
                         'level_1'
                         }).rename(columns={
                              0:'information'
                         })

               merge = merge.drop(columns={'level_0'}).reset_index().\
               rename(columns={'index':'level_0'})
               result = pd.merge(more_information, merge[['level_0','packet', 'layers']]
                    , on='level_0', how='left')

               del merge
               del more_information

               srez = result.loc[result['information'].astype(str).str.contains(":")]

               del result

               srez['flag'] = srez['information'].astype(str).str.split(":", \
                    expand=True)[0]
               srez['value'] = srez['information'].astype(str).str.split(":", \
                    expand=True)[1]
               srez.loc[srez['value'].astype(str).str[0] == " ", 'value'] = \
                    srez['value'].astype(str).str[1:]
               srez = srez.drop(columns={
                    'information',
                    'level_0',
                    })

               srez = srez[['packet','layers', 'flag', 'value']]

               srez = actions_file.build_pivot_table(srez)
          
          except:
               srez = pd.DataFrame()
               
          return srez

     def save_traffic(df, filename):
          result_path = \
          path = str(f"{actions_file.path()}/files_for_bd/{filename}.csv")
          df.to_csv(result_path, index=False)
          return result_path

     def save_traffic_db(df, table_name):
          list_conn = control_db.connect_db()
          cur = list_conn[0]
          conn = list_conn[1]
          engine = list_conn[2]

          df.to_sql(table_name, con=engine, index=False, if_exists='replace')
          
          conn.commit()
          cur.close()
          conn.close()

     def list_interfaces():
          return netifaces.interfaces()

     def main_func(filename, int_cap, seconds):
          #Функция управления
          control_capture.trasnform_to_mode_monitor(int_cap)
          capture = control_capture.capture(int_cap, seconds)
          df = control_capture.transform_traffic(capture)
          del capture
          try:
               try:
                    control_capture.save_traffic_db(df, filename)
                    text = "Трафик захвачен\nДанные загружены в БД"
               except:
                    control_capture.save_traffic(df, filename)
                    text = str(\
                         f"Трафик захвачен\nДанные загружены в файл {filename}.csv")
          except:
               df = pd.DataFrame()
               text = "Трафик не захвачен"
          list_result = [df,text]
               
          return list_result