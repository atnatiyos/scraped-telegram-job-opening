import dash
import Database
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output 
import re
import pandas as pd

# Specify dtype='float64' explicitly
empty_series = pd.Series(dtype='float64')
app = Dash(__name__)

Database.reconnect()

Query_job_category = "SELECT Job_category, Count(Job_category) as count from Jobs Group by Job_category"
Database.cursor.execute(Query_job_category)
Data = Database.cursor.fetchall()
list_jobCategory = [{'label':'all','value':'all'}]
for jobCategory in Data:
    list_jobCategory.append({'label':jobCategory[0],'value':jobCategory[0]})



app.layout = html.Div(
    [
    html.H1("Telegram freelance job posts data analysis dashboard", style={'text-align': 'center'}),
    dcc.Dropdown(id='job_sector',
                 options=list_jobCategory,
                 multi = False,
                 value='all',
                 style={'width': "50%","display": "inline-block", "grid-gap": "10px"}
                 ),

    dcc.Dropdown(id='professional_level',
                 options=[],
                 value='all',
                 multi = False,
                 style={'width': "30%", "display": "inline-block","grid-gap": "10px"}),
                 

    dcc.Graph(id="job_category", figure={}, style={'width': "65%",'hieght':'100%', "display": "inline-block", "grid-gap": "10px"}),
    dcc.Graph(id="job_level",figure={},style={'width': "30%",'hieght':'100%', "display": "inline-block", "grid-gap": "10px"}),
    dcc.Graph(id='gender_distribution',figure={},style={'width':'30%','hieght':'80%',"display": "inline-block",}),
    dcc.Graph(id='location_distribution',figure={},style={'width':'60%','hieght':'80%',"display": "inline-block",}),
    
    dcc.Dropdown(id='year',
                 options=[{'label':'2023','value':'23'},
                          {'label':'2024','value':'24'}],
                 value='23',
                 multi = False,
                 style={'width': "30%","grid-gap": "10px"}),

    dcc.Graph(id='time_series',figure={},style={'width':'100%','hieght':'80%',"display": "inline-block",})
   
   ])

@app.callback(
    [Output(component_id="job_category", component_property="figure"),
     Output(component_id='professional_level',component_property='options'),
     Output(component_id='job_level',component_property='figure'),
     Output(component_id='gender_distribution',component_property='figure'),
     Output(component_id='location_distribution',component_property='figure'),
     Output(component_id='time_series',component_property='figure')
    
     
    ],
    [Input("job_sector", "value"),
     Input('professional_level','value'),
     Input('year','value')
    ]
)
def first_part(sector,level,year):
     # Check if the sector value has changed
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "job_sector":
        level = "all"

    
    Job_category_count = []
    Job_categories = []

    levels = []
    professional_level= []
    number_of_level_request=[]

    gender_distribution = []
    genders = []
    def sector_gender(clause = None):
            
        gender_query = f"select Required_applicant, Count(Required_applicant) from Jobs {clause} Group by Required_applicant"
        
        try:
            Database.cursor.execute(gender_query)
            result = Database.cursor.fetchall()

            if len(result) == 0:
                
                gender_query = f"select Required_applicant, Count(Required_applicant) from Jobs Group by Required_applicant"

                Database.cursor.execute(gender_query)
                result = Database.cursor.fetchall()    
                return list(map(lambda dist : dist[1],result)), list(map(lambda dist : dist[0] if dist[0] != '' else 'not specified',result))
            else:
                return list(map(lambda dist : dist[1],result)), list(map(lambda dist : dist[0] if dist[0] != '' else 'not specified',result))
        except Exception as e:
            print(e)
            return
        
    cities = []
    city_counts = []

    def location_based(filter = ""):
        city_query = f"select  Job_location, Count(Job_location) from Jobs {filter}  Group by Job_location"
        try:
            Database.cursor.execute(city_query)
            result = Database.cursor.fetchall()
            return list(map(lambda city:city[0],result)), list(map(lambda city:city[1],result))
        except Exception as e:
            print(e)


    months = f'select Distinct SUBSTRING(Time_of_post, 4, 2) from Jobs where SUBSTRING(Time_of_post, 7, 4) = {year}'  
    x_values = []
    y_values = {}
    try:
        Database.cursor.execute(months)
        result = Database.cursor.fetchall()
        
        x_values =list(map(lambda x:x[0], result))
        print(x_values)
    except:None

    def multi_line_graph(type,selector):
        category_count_query = f"select Distinct({type}),Count({type}),SUBSTRING(Time_of_post, 4, 2) AS month,SUBSTRING(Time_of_post, 7, 4) AS year from Jobs where  {selector} and  SUBSTRING(Time_of_post, 7, 4) = {year} Group by {type}, SUBSTRING(Time_of_post, 4, 2),SUBSTRING(Time_of_post, 7, 4)"
        try:
            
            Database.cursor.execute(category_count_query)
            result = Database.cursor.fetchall()
            
            y_val = []
            for month in result:
                if month[2] in x_values:
                    y_val.append(month[1])
                else:
                    y_val.append(0)
           
            name = re.search(r"'(.*?)'", selector)
            y_values[name.group(1)] = y_val
            # print(y_values)

        except Exception as e: print(e)
   

    if sector == 'all':
        for row in Data:
            data = row[0].split(" ")
            Job_categories.append(data[0])
        Job_category_count = [row[1] for row in Data]

        levels = [{'label':'all','value':'all'}]
        level_query = 'select Exprience_level,Count(Exprience_level) from Jobs Group by Exprience_level'
        try: 
            Database.cursor.execute(level_query)
            exprience_level = Database.cursor.fetchall()

            professional_level = list(map( lambda level: level[0],exprience_level))
            number_of_level_request = list(map(lambda required: required[1],exprience_level))
        except Exception as e:
            print(e)
        gender_distribution,genders = sector_gender()
        cities, city_counts = location_based()

        for job_sector in Data:
            selector = f" Job_category = '{job_sector[0]}' "
            multi_line_graph("Job_category",selector)
    else:
        
        sectors = []
        query = "SELECT Job_sector, COUNT(Job_sector) as count FROM Jobs WHERE Job_category = '" +str(sector) +"' GROUP BY Job_sector"
        try:
            # Job_categories.clear()
            # Job_category_count.clear()  

            Database.cursor.execute(query)
            job_sectors = Database.cursor.fetchall()
            
            
            Job_category_count = [job_sector[1] for job_sector in job_sectors]
            # Job_categories = [sector[0] for sector in job_sectors]

            def minimize_text(text):
                return text[:10] + '...'

            Job_categories = list(map(minimize_text, [job_sector[0] for job_sector in job_sectors]))
 
            levels = [{'label': 'all', 'value': 'all'}] + [{'label': f'{i}', 'value': f'{i}'} for i in [job_sector[0] for job_sector in job_sectors]]

            sectors = list(map(lambda x:x[0],job_sectors))
            

        except Exception as e:
            print(f"Error: {e}")

        
        
        def all(filter):
                
            level_query = f"select Exprience_level,Count(Exprience_level) from Jobs {filter} Group by Exprience_level"
            Database.cursor.execute(level_query)
            exprience_level = Database.cursor.fetchall()

            if len(exprience_level) == 0:
                
                level_query = f"select Exprience_level,Count(Exprience_level) from Jobs  Group by Exprience_level"
                Database.cursor.execute(level_query)
                exprience_level = Database.cursor.fetchall()
                return list(map( lambda level: level[0],exprience_level)),list(map(lambda required: required[1],exprience_level))
            else:
                return list(map( lambda level: level[0],exprience_level)),list(map(lambda required: required[1],exprience_level))



        if level == 'all' or  level == None:
            professional_level,number_of_level_request = all(f" where Job_category = '{sector}'")
            gender_distribution,genders = sector_gender(f" where Job_category = '{sector}' ")
            cities, city_counts = location_based(f" where Job_category = '{sector}' ")
       
            for job_sector in sectors:
                selector = f" Job_sector = '{job_sector}' "    
                multi_line_graph("Job_sector",selector)
        else:
            professional_level,number_of_level_request = all(f" where Job_category = '{sector}' and Job_sector = '{level}'")
            gender_distribution,genders = sector_gender(f" where Job_category = '{sector}' and Job_sector = '{level}' ")
            cities, city_counts = location_based(f" where Job_category = '{sector}' and Job_sector = '{level}' ")
            for job_sector in sectors:
                selector = f" Job_sector = '{job_sector}' "    
                multi_line_graph("Job_sector",selector)

    experience_level_dist = level if level != 'all' else sector  
    fig = px.bar(x=Job_categories, y=Job_category_count, title="Job category distribution", color=Job_category_count)
    prof_level = px.pie(names=professional_level,values=number_of_level_request,title=f'Exprience level for {experience_level_dist }')
    
    require_app_gender = level if level != 'all' else sector
    pie_chart = px.pie(names=genders,values=gender_distribution,title=f"Required applicants for {require_app_gender}")
    
    city_fig = go.Figure(data=[go.Bar(x=city_counts, y=cities, orientation='h')])
    city_fig.update_layout(
        title=f" Number of {level if level != 'all' else sector} job posted in each city",
        # marker_color=colors[city_counts],
        xaxis_title='Cities'
    )


    trace = []
    for key,value in y_values.items():
        trace.append(go.Scatter(x=x_values, y=value, mode='lines', name=f'{key}'))
   
    figx = go.Figure()
    for tracer in trace:
        figx.add_trace(tracer)
   

# Update layout
    figx.update_layout(title=f'{sector} Job posted over time',
                  xaxis_title='Months',
                  yaxis_title='Number of job post')
    
    
    
    return [fig,levels,prof_level,pie_chart,city_fig,figx]


if __name__ == '__main__':
    app.run_server(debug=True)
