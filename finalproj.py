import requests
import json
import sqlite3
from secrets import *
import plotly.plotly as py 
import plotly.graph_objs as go


yelpurl = 'https://api.yelp.com/v3/businesses/search'
header_yelp = {'authorization':'Bearer '+api_key}
CACHE_FNAME = 'cache_yelp.json'

CACHE_FNAME2 = 'cache_zomato.json'
zr_url = 'https://developers.zomato.com/api/v2.1/search'
header_zomato = {'user_key': zomato_key}

DBNAME = 'resto.db'


###Yelp cache
try:
    cache_file = open(CACHE_FNAME, "r")
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def make_request_using_cache(url):
    if url in CACHE_DICTION:
        print("Retrieving cached data...")
        return CACHE_DICTION[url]
    else:
        print("Retrieving new data...")
        resp = requests.get(url, headers = header_yelp)
        CACHE_DICTION[url] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[url]

def get_from_yelp(search_city, offset):
    baseurl = 'https://api.yelp.com/v3/businesses/search'
    parameters = {}
    parameters['term'] = 'restaurants'
    parameters['location'] = search_city
    parameters['offset'] = offset
    parameters['limit'] = 50
    responseurl = requests.get(yelpurl, params = parameters).url
    response = make_request_using_cache(responseurl)
    py_obj = json.loads(response)
    return py_obj


###Zomato cache
try:
    cache_file2 = open(CACHE_FNAME2, "r")
    cache_contents2 = cache_file2.read()
    CACHE_DICTION2 = json.loads(cache_contents2)
    cache_file2.close()
except:
    CACHE_DICTION2 = {}

def make_request_using_cache2(url):
    if url in CACHE_DICTION2:
        print("Retrieving cached data...")
        return CACHE_DICTION2[url]
    else:
        print("Retrieving new data...")
        resp2 = requests.get(url, headers = header_zomato)
        CACHE_DICTION2[url] = resp2.text
        dumped_json_cache2 = json.dumps(CACHE_DICTION2)
        fw = open(CACHE_FNAME2,"w")
        fw.write(dumped_json_cache2)
        fw.close()
        return CACHE_DICTION2[url]

def get_zomato_city_id(city):
    z_url = 'https://developers.zomato.com/api/v2.1/cities'
    parameters = {'q':city, 'count':1}
    id_dic = requests.get(z_url, params = parameters, headers = header_zomato).json()
    city_id = id_dic['location_suggestions'][0]['id']
    return city_id

def get_from_zomato(city,start):
    zr_url = 'https://developers.zomato.com/api/v2.1/search'
    parameters = {'entity_id':get_zomato_city_id(city), 'entity_type':'city', 'start':start, 'count':20}
    resto_url = requests.get(zr_url, params = parameters).url
    resto_resp = make_request_using_cache2(resto_url)
    py_obj = json.loads(resto_resp)
    return py_obj


###DB creation
def create_db_tables():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'DROP TABLE IF EXISTS "YelpResto";'
    cur.execute(statement)
    conn.commit()

    statement = 'DROP TABLE IF EXISTS "ZomatoResto";'
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'YelpResto' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'CategoryID' TEXT,
            'CategoryName' TEXT,
            'Rating' REAL,
            FOREIGN KEY ('CategoryID') REFERENCES Categories('Id')
            );
        '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'ZomatoResto' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'CuisineID' TEXT,
            'Cuisine' TEXT,
            'Rating' REAL,
            FOREIGN KEY ('CuisineID') REFERENCES Cuisines('Id')
            );
        '''
    cur.execute(statement)
    conn.commit()
    conn.close()


###inserting data into yelp and zomato tables
def insert_tables():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    yelp_lis_hund_rec = []
    for i in range (1,100,50):
        yelp_lis_hund_rec.append(get_from_yelp(city_inp, i)['businesses'])
    
    for each in yelp_lis_hund_rec:
        for ea in each:
            yelp_ins = (None, ea['name'],'', ea['categories'][0]['title'], ea['rating'])
            statement ='''
                INSERT INTO 'YelpResto'
                VALUES (?, ?, ?, ?, ?);
                '''
            cur.execute(statement,yelp_ins)
    conn.commit()

    zomato_lis_hund_rec = []
    for i in range (0,100,20):
        zomato_lis_hund_rec.append(get_from_zomato(city_inp, i)['restaurants'])
    
    for each in zomato_lis_hund_rec:
        for ea in each:
            z_resto = ea['restaurant']['name']
            z_cuis = ea['restaurant']['cuisines'].split(',')[0]
            z_rate = float(ea['restaurant']['user_rating']['aggregate_rating'])
            if z_cuis == '':
                z_cuis = 'Unspecified'
                zomato_ins = (None, z_resto, '', z_cuis, z_rate)
                statement ='''
                    INSERT INTO 'ZomatoResto'
                    VALUES (?, ?, ?, ?, ?);
                    '''
                cur.execute(statement, zomato_ins)
            else:
                zomato_ins = (None, z_resto, '', z_cuis, z_rate)
                statement ='''
                    INSERT INTO 'ZomatoResto'
                    VALUES (?, ?, ?, ?, ?);
                    '''
                cur.execute(statement, zomato_ins)
        conn.commit()
    conn.close()


###creating unique categories
def create_categories():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'DROP TABLE IF EXISTS "Categories";'
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Categories' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'CategoryName' TEXT,
            'AveRating' REAL
            );
        '''
    cur.execute(statement)
    conn.commit()

    statement = 'SELECT Distinct (CategoryName) FROM YelpResto ORDER BY CategoryName ASC'
    cur.execute(statement)
    categ_l = cur.fetchall()

    for each in categ_l:
        ea_categ = each[0]
        categ_ins = (None, ea_categ, '')
        statement ='INSERT INTO "Categories" VALUES (?, ?, ?);'
        cur.execute(statement, categ_ins)
    conn.commit()
    conn.close()


###creating unique cuisines
def create_cuisines():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'DROP TABLE IF EXISTS "Cuisines";'
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Cuisines' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Cuisine' TEXT,
            'AveRating' REAL
            );
        '''
    cur.execute(statement)
    conn.commit()

    statement = 'SELECT Distinct (Cuisine) FROM ZomatoResto ORDER BY Cuisine ASC'
    cur.execute(statement)
    cuisine_l = cur.fetchall()

    for each in cuisine_l:
        ea_cuisine = each[0]
        cuisine_ins = (None, ea_cuisine, '')
        statement ='INSERT INTO "Cuisines" VALUES (?, ?, ?);'
        cur.execute(statement, cuisine_ins)
    conn.commit()
    conn.close()


###updating category and cuisine ids
def upd_ids():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'SELECT c.Id, c.CategoryName FROM Categories AS c, YelpResto as y WHERE c.CategoryName = y.CategoryName;'
    cur.execute(statement)
    cat_l = cur.fetchall()

    for each in cat_l:
        cat_tup = (each[0], each[1])   
        yelp_id_update = 'UPDATE YelpResto SET CategoryID=? WHERE CategoryName=?;'
        cur.execute(yelp_id_update, cat_tup)

    conn.commit()

    statement = 'SELECT c.Id, c.Cuisine FROM Cuisines AS c, ZomatoResto as z WHERE c.Cuisine = z.Cuisine;'
    cur.execute(statement)
    cuis_l = cur.fetchall()

    for each in cuis_l:
        cuis_tup = (each[0], each[1])   
        zomato_id_update = 'UPDATE ZomatoResto SET CuisineID = ? WHERE Cuisine=?;'
        cur.execute(zomato_id_update, cuis_tup)

    conn.commit()
    conn.close()


###updating average rating
def upd_ave_rating():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
        SELECT CategoryID, ROUND(AVG(Rating),1) FROM YelpResto
        GROUP BY CategoryID
        '''
    cur.execute(statement)
    for each in cur.fetchall():
        ave_tup = (each[1], each[0])
        cat_ave = 'UPDATE Categories SET AveRating = ? WHERE Id=?;'
        cur.execute(cat_ave, ave_tup)
    conn.commit()

    statement = '''
        SELECT CuisineID, ROUND(AVG(Rating),1) FROM ZomatoResto
        GROUP BY CuisineID
        '''
    cur.execute(statement)
    for each in cur.fetchall():
        ave_tup = (each[1], each[0])
        cui_ave = 'UPDATE Cuisines SET AveRating = ? WHERE Id=?;'
        cur.execute(cui_ave, ave_tup)
    conn.commit()
    conn.close()


###command function
def process_command(command):
    inp_command = command.split()
    
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
   
    st_yelp = '''
        SELECT c.CategoryName, c.AveRating, T1.Highest, T1.Lowest
        FROM Categories as c
        JOIN
        (SELECT y.CategoryID, y.CategoryName, MAX(y.Rating) AS Highest, MIN(y.Rating) as Lowest
        FROM YelpResto as y GROUP BY y.CategoryID) as T1 on c.ID = t1.Categoryid
        ORDER BY AveRating DESC
        '''
    cur.execute(st_yelp)
    yelp_results = cur.fetchall()

    st_zomato = '''
        SELECT c.Cuisine, c.AveRating, T1.Highest, T1.Lowest
        FROM Cuisines as c
        JOIN
        (SELECT z.CuisineID, z.Cuisine, MAX(z.Rating) AS Highest, MIN(z.Rating) as Lowest
        FROM ZomatoResto as z GROUP BY z.CuisineID) as T1 on c.ID = t1.Cuisineid
        ORDER BY AveRating DESC
        '''
    cur.execute(st_zomato)
    zomato_results = cur.fetchall()

    valid_tot_yelp = len(yelp_results)
    valid_tot_zomato = len(zomato_results)

    if inp_command[1] == 'yelp' or inp_command[1] == 'zomato':
        ordby = 'DESC'
        lim = ''
        limby = ''
        ret_error = False

        try:
            if inp_command[2] is not None:
                if inp_command[2] != 'top' and inp_command[2] != 'bottom':
                    ret_error = True
                    print('Check that third command is either "top" or "bottom".')

                if inp_command[2] == 'top':
                    ordby = 'DESC'

                if inp_command[2] == 'bottom':
                    ordby = 'ASC'
        except:
            pass

        try:
            if inp_command[3] is not None:
                try:
                    lim = 'LIMIT'
                    limby_int = int(inp_command[3])

                    if inp_command[1] == 'yelp':
                        if limby_int <= valid_tot_yelp:
                            limby = limby_int
                        else:
                            lim = ''
                            ret_error = True
                            print('Number entered is greater than total number of records.')

                    if inp_command[1] == 'zomato':
                        if limby_int <= valid_tot_zomato:
                                    limby = limby_int
                        else:
                            lim = ''
                            ret_error = True
                            print('Number entered is greater than total number of records.')
                except:
                    lim = ''
                    ret_error = True
                    print('Check that fourth command is valid.')
        except:
            pass

        global yelp_count
        global zomato_count

        yelp_count = 0
        zomato_count = 0

        if inp_command[1] == 'yelp' and ret_error is False:
            st_yelp2 = '''
                SELECT c.CategoryName, c.AveRating, T1.Highest, T1.Lowest
                FROM Categories as c
                JOIN
                (SELECT y.CategoryID, y.CategoryName, MAX(y.Rating) AS Highest, MIN(y.Rating) as Lowest FROM YelpResto as y GROUP BY y.CategoryID) as T1 on c.ID = t1.Categoryid
                ORDER BY AveRating {}
                {} {}
                '''.format(ordby, lim, limby)

            cur.execute(st_yelp2)
            yelp_results2 = cur.fetchall()
            yelp_count += 1

            return yelp_results2

        elif inp_command[1] == 'zomato' and ret_error is False:
            st_zomato2 = '''
                SELECT c.Cuisine, c.AveRating, T1.Highest, T1.Lowest
                FROM Cuisines as c
                JOIN
                (SELECT z.CuisineID, z.Cuisine, MAX(z.Rating) AS Highest, MIN(z.Rating) as Lowest
                FROM ZomatoResto as z GROUP BY z.CuisineID) as T1 on c.ID = t1.Cuisineid
                ORDER BY AveRating {}
                {} {}
                '''.format(ordby, lim, limby)

            cur.execute(st_zomato2)
            zomato_results2 = cur.fetchall()
            zomato_count += 1

            return zomato_results2
        
        else:
            return []

    conn.close()


###class for data processing
class ResultList():
    def __init__(self, init_tuple):
        self.category = init_tuple[0]
        self.averate = init_tuple[1]
        self.maxrate = init_tuple[2]
        self.minrate = init_tuple[3]


###help text
def load_help_text():
    with open('help.txt') as f:
        return f.read()


###interactive commands
def ask_next():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    global yelp_ret_val
    global zomato_ret_val

    yelp_ret_val = []
    zomato_ret_val = []
    
    while True:
        inputcommand = input('\nEnter command (type "help" to view list of commands or "exit" to quit): ').lower()
        inp_command_lis = inputcommand.split()
        valid_start = ['list', 'plot', 'new', 'help', 'exit']

        try:
            if inp_command_lis[0] in valid_start:
                go_on = True
            else:
                go_on = False
                print('Invalid command.')
        except:
            go_on = False
            print('Invalid command.')

        if go_on == True:
            if inp_command_lis[0] == 'exit':
                print('Bye!\n')
                break

            if inp_command_lis[0] == 'new':
                ask_user()
                yelp_ret_val= []
                zomato_ret_val = []
                break

            if inp_command_lis[0] == 'help':
                help_text = load_help_text()
                print(help_text)

            if inp_command_lis[0] == 'list':

                try:
                    if inp_command_lis[1] is not None and inp_command_lis[1] == 'yelp' and inp_command_lis[2] is not None:
                        yelp_ret_val = process_command(inputcommand)

                        if yelp_ret_val != []:

                            print('\nRESTAURANT CATEGORIES AND RATINGS FROM ' + inp_command_lis[1].upper())
                            print('{:25} {:^10} {:^10} {:^10}'.format('\nCATEGORY', ' AVE', ' MAX', ' MIN'))

                            my_objects = []
                            for each_tup in yelp_ret_val:
                                my_objects.append(ResultList(each_tup))

                            for obj in my_objects:
                                print('{:25} {:^10} {:^10} {:^10}'.format(obj.category, obj.averate, obj.maxrate, obj.minrate))

                    elif inp_command_lis[1] is not None and inp_command_lis[1] == 'zomato' and inp_command_lis[2] is not None:
                        zomato_ret_val = process_command(inputcommand)

                        if zomato_ret_val != []:

                            print('\nRESTAURANT CUISINES AND RATINGS FROM ' + inp_command_lis[1].upper())
                            print('{:25} {:^10} {:^10} {:^10}'.format('\nCUISINE', ' AVE', ' MAX', ' MIN'))

                            my_objects = []
                            for each_tup in zomato_ret_val:
                                my_objects.append(ResultList(each_tup))

                            for obj in my_objects:
                                print('{:25} {:^10} {:^10} {:^10}'.format(obj.category, obj.averate, obj.maxrate, obj.minrate))
                    
                    else:
                        print('Check source input.')
                
                except:
                    print('Invalid command.')                
        
            if inp_command_lis[0] == 'plot':
                valid_charts = ['bar', 'groupedbar', 'pie', 'donut']

                st_group = '''
                    SELECT ca.CategoryName, ca.AveRating, cu.AveRating
                    FROM Categories as ca, Cuisines as cu 
                    WHERE ca.CategoryName = cu.Cuisine;
                '''
                cur.execute(st_group)
                group_results = cur.fetchall()

                st_pie_yelp = '''
                    SELECT CategoryName, COUNT(Id) from YelpResto
                    GROUP BY CategoryName
                    ORDER BY COUNT(Id) DESC
                    '''
                cur.execute(st_pie_yelp)
                pie_yelp = cur.fetchall()

                st_pie_zomato = '''
                    SELECT Cuisine, COUNT(Id) from ZomatoResto
                    GROUP BY Cuisine
                    ORDER BY COUNT(Id) DESC
                    '''
                cur.execute(st_pie_zomato)
                pie_zomato = cur.fetchall()

                st_donut = '''
                    SELECT T2.CategoryName, T2.yelp_count, T1.zomato_count
                    FROM
                    (SELECT z.Cuisine, COUNT(z.Id) as zomato_count
                    FROM ZomatoResto as z
                    GROUP BY z.Cuisine) as T1,
                    (SELECT y.CategoryName, COUNT(y.Id) as yelp_count
                    FROM YelpResto as y
                    GROUP BY y.CategoryName) as T2
                    WHERE T2.CategoryName = T1.Cuisine
                '''
                cur.execute(st_donut)
                donut_results = cur.fetchall()
               
                try:
                    if inp_command_lis[1] is not None and inp_command_lis[1] in valid_charts:
                        cont = True

                    elif inp_command_lis[1] is not None and inp_command_lis[1] not in valid_charts:
                        cont = False
                        print('Invalid chart type.')
                    else:
                        pass
                except:
                    cont = False
                    print('Invalid chart type.')
    
                if cont == True:
                    if inp_command_lis[1] == 'bar' and len(inp_command_lis) == 2:
                        if yelp_ret_val != [] or zomato_ret_val != []:
                            if yelp_ret_val != [] and zomato_ret_val == []:
                                x_names = []
                                y_averate = []
                                for each in yelp_ret_val:
                                    x_names.append(each[0])
                                    y_averate.append(each[1])
                                data = [go.Bar(x = x_names,y = y_averate)]
                                py.plot(data, filename='yelp-bar', auto_open=True)

                            elif yelp_ret_val == [] and zomato_ret_val != []:
                                x_names = []
                                y_averate = []
                                for each in zomato_ret_val:
                                    x_names.append(each[0])
                                    y_averate.append(each[1])

                                data = [go.Bar(x = x_names,y = y_averate)]
                                py.plot(data, filename='zomato-bar', auto_open=True)

                            elif yelp_ret_val != [] and zomato_ret_val != []:
                                    if yelp_count > zomato_count:
                                        x_names = []
                                        y_averate = []
                                        for each in yelp_ret_val:
                                            x_names.append(each[0])
                                            y_averate.append(each[1])
                                        
                                        data = [go.Bar(x = x_names,y = y_averate)]
                                        py.plot(data, filename='yelp-bar', auto_open=True)
                                    
                                    else:
                                        x_names = []
                                        y_averate = []
                                        for each in zomato_ret_val:
                                            x_names.append(each[0])
                                            y_averate.append(each[1])

                                        data = [go.Bar(x = x_names,y = y_averate)]
                                        py.plot(data, filename='zomato-bar', auto_open=True)

                        else:
                            print('No result set to map. Use the "list" command to generate a result set.')

                    elif inp_command_lis[1] == 'groupedbar' and len(inp_command_lis) == 2:
                        yelp_x_names = []
                        yelp_y_averate = []
                        for each in group_results:
                            yelp_x_names.append(each[0])
                            yelp_y_averate.append(each[1])

                        zomato_x_names = []
                        zomato_y_averate = []
                        for each in group_results:
                            zomato_x_names.append(each[0])
                            zomato_y_averate.append(each[2])

                        trace1 = go.Bar(
                            x = yelp_x_names,
                            y = yelp_y_averate,
                            name = 'Yelp'
                        )
                        trace2 = go.Bar(
                            x = zomato_x_names,
                            y = zomato_y_averate,
                            name = 'Zomato'
                        )

                        data = [trace1, trace2]
                        layout = go.Layout(
                            barmode = 'group'
                        )

                        fig = go.Figure(data=data, layout=layout)
                        py.plot(fig, filename='grouped-bar-yz', auto_open=True)

                    elif inp_command_lis[1] == 'pie' and len(inp_command_lis) == 3:

                        try:
                            if inp_command_lis[2] == 'yelp':

                                yelp_labels = []
                                yelp_values = []
                                for each in pie_yelp:
                                    yelp_labels.append(each[0])
                                    yelp_values.append(each[1])

                                labels = yelp_labels
                                values = yelp_values

                                trace = go.Pie(labels=labels, values=values)

                                py.plot([trace], filename='basic_pie_chart_yelp', auto_open=True)

                            elif inp_command_lis[2] == 'zomato':
                                zomato_labels = []
                                zomato_values = []
                                for each in pie_zomato:
                                    zomato_labels.append(each[0])
                                    zomato_values.append(each[1])

                                labels = zomato_labels
                                values = zomato_values

                                trace = go.Pie(labels=labels, values=values)

                                py.plot([trace], filename='basic_pie_chart_zomato', auto_open=True)
                            else:
                                print('Check source input.')
                        except:
                            print('Invalid command.')

                    elif inp_command_lis[1] == 'donut' and len(inp_command_lis) == 2:
                        labels = []
                        yelp_values = []
                        zomato_values = []

                        for each in donut_results:
                            labels.append(each[0])
                            yelp_values.append(each[1])
                            zomato_values.append(each[2])

                        fig = {
                            "data": [
                            {
                              "values": yelp_values,
                              "labels": labels,
                              "domain": {"x": [0, .48]},
                              "name": "Yelp",
                              "hoverinfo":"label+percent+name",
                              "hole": .4,
                              "type": "pie"
                            },     
                            {
                              "values": zomato_values,
                              "labels": labels,
                              "text":"Zomato",
                              "textposition":"inside",
                              "domain": {"x": [.52, 1]},
                              "name": "Zomato",
                              "hoverinfo":"label+percent+name",
                              "hole": .4,
                              "type": "pie"
                            }],
                          "layout": {
                                "title":"Yelp vs Zomato Restaurant Count",
                                "annotations": [
                                    {
                                        "font": {
                                            "size": 20
                                        },
                                        "showarrow": False,
                                        "text": "Yelp",
                                        "x": 0.20,
                                        "y": 0.5
                                    },
                                    {
                                        "font": {
                                            "size": 20
                                        },
                                        "showarrow": False,
                                        "text": "Zomato",
                                        "x": 0.8,
                                        "y": 0.5
                                    }
                                ]
                            }
                        }
                        py.plot(fig, filename='donut', auto_open = True)

                    else:
                        print('Invalid command.')

    conn.close()


###ask user to choose city
def ask_user():
    global city_inp
    terminate = False

    places = ['Atlanta, GA', 'Austin, TX', 'Boston, MA', 'Charleston, SC', 'Chicago, IL', 'Columbus, OH', 'Dallas, TX', 'Denver, CO', 'Detroit, MI', 'Houston, TX', 'Las Vegas, NV', 'Los Angeles, CA', 'Miami, FL', 'Nashville, TN', 'New Orleans, LA', 'New York, NY', 'Orlando, FL', 'Portland, OR', 'San Antonio, TX', 'San Diego, CA', 'San Francisco, CA', 'Savannah, GA', 'Seattle, WA', 'St. Louis, MO', 'Washington, DC']
    
    print('\nTop 25 Places to Visit in the US:')
    for number, each in enumerate(places, start = 1):
        print(number, each)

    while True:
        place_index = input('\nEnter number to search or type "exit" to quit: ').lower()

        if place_index == 'exit':
            print('Program terminated.\n')
            terminate = True
            break
        
        else:
            try:
                city_inp = places[int(place_index) -1].split(',')[0]
                if int(place_index) < 26:
                    print('\nSearching Yelp and Zomato for restaurants in ' + city_inp + '... (max no. of records per source = 100)\n')
                    break
                else:
                    print('Enter a valid number.')
            except:
                print('Enter a valid number.')

    if terminate == False:
        create_db_tables()
        insert_tables()
        create_categories()
        create_cuisines()
        upd_ids()
        upd_ave_rating()
        ask_next()


### RUN PROGRAM ###

if __name__=="__main__":
    ask_user()

