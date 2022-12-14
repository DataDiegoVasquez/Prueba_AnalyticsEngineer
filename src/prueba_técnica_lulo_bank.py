# -*- coding: utf-8 -*-
"""Prueba técnica Lulo Bank.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18D7Ll2BbASrh49roVoF98WN_pmIZUjVF
"""

'''
Iniciamos importando todas las librerias que serán utilies para el desarrollo
del analisis solicitado
**NOTA: Se instala directamente en el notebook la libreria de pandas profiling,
lo recomendado es instalarlo utilizando el gestor de paquetes pip ejecutando
el siguiente comando:
pip install -U pandas-profiling[notebook]
'''
import requests
import json
import urllib
import pandas as pd
!pip install https://github.com/ydataai/pandas-profiling/archive/master.zip
from pandas_profiling import ProfileReport
import sqlite3

d = {}
def ObtenerApi(anio,mes,dia):
  for x in (n+1 for n in range(dia)):
    url ='http://api.tvmaze.com/schedule/web'
    params= {"date":str(anio)+"-"+str(mes)+"-"+ "{:02d}".format(x)}
    response = requests.get(url, params)

    if response.status_code == 200:
      d[x] = json.loads(response.text)
      d[x] = pd.DataFrame.from_dict(d[x])
      d[x].to_json('File'+str(x)+'.json')
      #print("Export Succesfully")
    else:
      print(f"Error:{response.status_code}")

'''
De acuerdo con la petición se traen todas las
series que se emitieron en diciembre del 2020.
'''
ObtenerApi(2020,12,31)

'''
Normalize data included in the columns
Se normalizan las columnas de los json que vienen como
diccionarios en las columnas del DataFrame
'''
df3 = pd.concat(d.values(), ignore_index = True).reset_index(drop=True)#Une todos los dataframes extraidos en uno solo
df3['rating'] = pd.json_normalize(df3['rating']) #Extrae y reemplaza los valores del diccionario contenido en la columna rating
df4 = pd.json_normalize(df3['image']) #Extrae los valores del diccionario contenido en la columna image y los guarda en un nuevo dataframe
df3['image_medium'] = df4['medium'] # Agrega la columna extraida de image al Dataframe Consolidado
df3['image_original'] = df4['original'] # Agrega la columna extraida de image al Dataframe Consolidado
df3['Extract_links'] = pd.json_normalize(df3['_links']) #Extrae y crea una columna con los valores del diccionario contenido en la columna _links
df5 = pd.json_normalize(df3['_embedded']) #Extrae los valores del diccionario contenido en la columna _embedded y los guarda en un nuevo dataframe
df3 = df3.merge(df5,left_index=True,right_index=True) #Se une el dataframe Consolidado con los valores extraidos de la columna _embedded
df6 = df3.drop(['image','_links','_embedded'], axis=1) # Se eliminan las columnas que contenian diccionarios

df6.info()

df6.describe()

'''
De acuerdo con la visualización de los datos se eliminan las columnas que no traen
directamente datos o la mayoria de sus datos son nulos dado que estas no tendrán
significancia en el analisis de los datos
'''
df_final = df6.drop(['show.dvdCountry','show.image','show.network','show.webChannel','show.webChannel.country','show.network.officialSite','show.dvdCountry.code','show.dvdCountry.name','show.dvdCountry.timezone','show.externals.tvrage','show._links.nextepisode.href','show.network.country.code','show.network.country.name','show.network.country.timezone','show.network.id','show.network.name'], axis=1)

'''
Coverts string datetime into python date time object
Convertimos todos las fechas que se encuentran como objeto de texto en un formato
de fecha para usar estas en el analisis de datos
'''
df_final['airdate'] = pd.to_datetime(df_final['airdate'], infer_datetime_format=True)  
df_final['show.premiered'] = pd.to_datetime(df_final['show.premiered'], infer_datetime_format=True)
df_final['airstamp'] = pd.to_datetime(df_final['airstamp'], infer_datetime_format=True)
df_final['show.ended'] = pd.to_datetime(df_final['show.ended'], infer_datetime_format=True) 
df_final['Year_show.premiered'] = df_final['show.premiered'].dt.year #Column consists of years when the show was released
#df_final['Year_show.ended'] = df_final['show.ended'].dt.year
#df_final = df_final.reindex(df3.index)

profile = ProfileReport(df_final, minimal=True,title="Profiling Report")#
profile.to_file(output_file="profiling1.html")
profile.to_notebook_iframe()

df_final.info()

'''
Despues de analizar los datos se ve que la mayoria posee campos vacios dentro de
la tabla y se procede a rellenar la información 
'''
df_final[['number','airtime','runtime','rating','show.id','show.premiered','show.ended','show.schedule.time','show.rating.average','show.externals.thetvdb','show.externals.imdb','show.updated','Year_show.premiered']] = df_final[['number','airtime','runtime','rating','show.id','show.premiered','show.ended','show.schedule.time','show.rating.average','show.externals.thetvdb','show.externals.imdb','show.updated','Year_show.premiered']].fillna(0)
df_final[['summary','image_medium','image_original','Extract_links','show.url','show.name','show.officialSite','show.webChannel.officialSite','show.image.medium','show.image.original','show.summary','show._links.self.href','show._links.previousepisode.href']] = df_final[['summary','image_medium','image_original','Extract_links','show.url','show.name','show.officialSite','show.webChannel.officialSite','show.image.medium','show.image.original','show.summary','show._links.self.href','show._links.previousepisode.href']].fillna('NI')
df_final[['show.type','show.language','show.status','show.webChannel.name','show.webChannel.country.name','show.webChannel.country.code','show.webChannel.country.timezone']] = df_final[['show.type','show.language','show.status','show.webChannel.name','show.webChannel.country.name','show.webChannel.country.code','show.webChannel.country.timezone']].fillna('OTHER')
df_final[['show.genres','show.schedule.days']] = df_final[['show.genres','show.schedule.days']].fillna('[]')
df_final['show.weight'] = df_final['show.weight'].fillna(method='ffill', inplace=True)
#df_final = df_final[['show.runtime']].fillna(df_final['show.averageRuntime'])
#Season 2020 no exists
# No se puede rellenar un Id ya que este alteraria la referencialidad de las tablas 'show.webChannel.id'

series = df_final[['id','url','name','season','number','type','airdate','airtime','airstamp','runtime','rating','summary','image_medium','image_original','Extract_links']]
series = series.rename(columns = {'number':'series_number'}) 
show = df_final[['id','show.id','show.url','show.name','show.type','show.language','show.genres','show.status','show.runtime','show.averageRuntime','show.premiered','show.ended','show.officialSite','show.schedule.time','show.schedule.days','show.rating.average','show.weight','show.webChannel.id','show.webChannel.name','show.webChannel.country.name','show.webChannel.country.code','show.webChannel.country.timezone','show.webChannel.officialSite','show.externals.thetvdb','show.externals.imdb','show.image.medium','show.image.original','show.summary','show.updated','show._links.self.href','show._links.previousepisode.href','Year_show.premiered']]
show = show.rename(columns = {'id':'id_series'})

# Commented out IPython magic to ensure Python compatibility.
# %load_ext sql
# %sql sqlite:///database.db

database = "/content/database.db"
conn = sqlite3.connect(database)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS series (id INT PRIMARY KEY ,url TEXT,name TEXT,season NUMERIC,series_number NUMERIC,type TEXT ,airdate NUMERIC,airtime NUMERIC,airstamp NUMERIC,runtime NUMERIC ,rating NUMERIC,summary TEXT,image_medium TEXT,image_original TEXT,Extract_links TEXT)')
conn.commit()

#c.execute('CREATE TABLE IF NOT EXISTS show (id_series NUMERIC, show.id NUMERIC,show.url TEXT,show.name TEXT,show.type TEXT,show.language TEXT,show.genres TEXT,show.status TEXT,show.runtime INT,show.averageRuntime INT ,show.premiered NUMERIC,show.ended NUMERIC,show.officialSite TEXT,show.schedule.time NUMERIC,show.schedule.days TEXT,show.rating.average NUMERIC,show.weight INT,show.webChannel.id INT,show.webChannel.name TEXT,show.webChannel.country.name TEXT,show.webChannel.country.code TEXT,show.webChannel.country.timezone TEXT,show.webChannel.officialSite TEXT,show.externals.thetvdb INT,show.externals.imdb TEXT,show.image.medium TEXT,show.image.original TEXT,show.summary TEXT,show.updated INT,show._links.self.href TEXT,show._links.previousepisode.href TEXT,Year_show.premiered NUMERIC)')
c.execute('CREATE TABLE IF NOT EXISTS show (id_series NUMERIC, show_id NUMERIC,show_url TEXT,show_name TEXT,show_type TEXT,show_language TEXT,show_genres TEXT,show_status TEXT,show_runtime NUMERIC,show_averageRuntime NUMERIC ,show_premiered NUMERIC,show_ended NUMERIC,show_officialSite TEXT,show_schedule_time NUMERIC,show_schedule_days TEXT,show_rating_average NUMERIC,show_weight NUMERIC,show_webChannel_id NUMERIC,show_webChannel_name TEXT,show_webChannel_country_name TEXT,show_webChannel_country_code TEXT,show_webChannel_country_timezone TEXT,show_webChannel_officialSite TEXT,show_externals_thetvdb NUMERIC,show_externals_imdb TEXT,show_image_medium TEXT,show_image_original TEXT,show_summary TEXT,show_updated NUMERIC,show__links_self_href TEXT,show__links_previousepisode_href TEXT,Year_show_premiered NUMERIC)')
conn.commit()
#FOREIGN KEY(id_series) REFERENCES series(id)

series.to_sql('series', conn, if_exists='replace', index = False)

show.to_sql('show', conn, if_exists='replace', index = False)

# Commented out IPython magic to ensure Python compatibility.
# c.execute('''  
# SELECT * FROM series
#           ''')
# 
# %%sql
# select * from series limit 10