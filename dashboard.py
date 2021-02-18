import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd 
import dash_table
import json
import pprint
import webbrowser

with open('json_test.json',encoding = 'utf-8') as f: #открыли файл с данными
    text = json.load(f) #загнали все, что получилось в переменную
    
df = pd.DataFrame (text['Sluzhebka'])
ser = pd.Series(text['Sluzhebka']['Poruchenie2'])
print(ser)
webbrowser.open_new('http://127.0.0.1:8050')
app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='TABLE',
    columns=[{"name": i, "id": i}  
    for i in df],
    data=df.to_dict('records'),
)
if __name__ == '__main__':
    app.run_server(debug=True)


    