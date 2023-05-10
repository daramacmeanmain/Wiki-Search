import paramiko
from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect

import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['ENV'] = "Development"
app.config['DEBUG'] = True


# initial home page
@app.route('/')
def home():
    return render_template("index.html")


# returns "I have no clue" result for Task 1 - unused in final program
@app.route('/searchAction')
def search_action():
    return render_template("result.html")


# returns initial output from wiki.py on first VM, before data is cached
@app.route('/content')
def get_content():
    newSearch = request.args.get('newSearch')  # this is the term we would like to search
    content = ""
    # declare credentials
    host = '127.0.0.1'
    port = 2233
    username = 'VM_USERNAME'
    password = 'VM_PASSWORD'
    # connect to server
    con = paramiko.SSHClient()
    con.load_system_host_keys()
    con.connect(hostname=host, port=port, username=username, password=password)
    stdin, stdout, stderr = con.exec_command('python3 /home/VM_USERNAME/wiki.py "' + newSearch + '"')
    outerr = stderr.readlines()
    print("ERRORS: ", outerr)
    output = stdout.readlines()
    htmlOutput = '''
                 <!DOCTYPE html>
                 <html lang="en">
                 <head>
                 <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KK94CHFLLe+nY2dmCWGMq91rCGa5gtU4mk92HdvYe+M/SXH301p5ILy+dN9+nJOZ" crossorigin="anonymous">
                 <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ENjdO4Dr2bkBIFxQpeoTz1HIcje39Wm4jDKdf19U8gI4ddQ3GYNS7NTKfAdVQSZe" crossorigin="anonymous"></script>
                 <meta charset="UTF-8">
                 <title>Wiki-Search</title>
                 </head>
                 <body>
                 <div class="container">
                 <h1>Wiki-Search</h1>
                 <form action="/getCache" method="post">
                    <label for="search">Search for something else:</label> <input type="text" id="search" name="search"><br>
                    <input type="submit" value="Submit">
                 </form><br>
                '''
    for items in output:
        htmlOutput += items + "<br>"
        content += items
    htmlOutput += '''
                 </div>
                 </body>
                 </html>
                '''
    cache(newSearch, content)  # pass the search term and data from wiki to the cache function
    return htmlOutput


# retrieve the cached version of the searched article
@app.route('/getCache', methods=['POST'])
def get_cache():
    search = request.form.get("search")
    try:
        connection = mysql.connector.connect(host='127.0.0.1',
                                             port='7888',
                                             database='wikipedia',
                                             user='root',
                                             password='mypassword')
        if connection.is_connected():
            myquery = "SELECT * FROM wikis WHERE title='" + search + "'"
            print(myquery)
            cursor = connection.cursor()
            result = cursor.execute(myquery)
            records = cursor.fetchall()

            # check if the term was searched before - if not, perform a new search using the wiki script
            if cursor.rowcount == 0:
                return redirect(url_for('get_content', newSearch=search))
            htmlOutput = '''
             <!DOCTYPE html>
             <html lang="en">
             <head>
             <link rel="stylesheet" href="static/styles/mainStyles.css">
             <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KK94CHFLLe+nY2dmCWGMq91rCGa5gtU4mk92HdvYe+M/SXH301p5ILy+dN9+nJOZ" crossorigin="anonymous">
             <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ENjdO4Dr2bkBIFxQpeoTz1HIcje39Wm4jDKdf19U8gI4ddQ3GYNS7NTKfAdVQSZe" crossorigin="anonymous"></script>
             <meta charset="UTF-8">
             <title>Wiki-Search</title>
             </head>
             <body>
             <div class="container">
             <h1>Wiki-Search</h1>
                 <form action="/getCache" method="post">
                    <label for="search">Search for something else:</label> <input type="text" id="search" name="search"><br>
                    <input type="submit" value="Submit">
                 </form><br>
            '''
            for row in records:
                htmlOutput += "<pre><p>" + row[1] + "</p></pre>"
            htmlOutput += '''
            </div>
             </body>
             </html>
            '''
            return htmlOutput
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return render_template("index.html")


# send the data to be cached in the database
@app.route('/cache', methods=['POST'])
def cache(search, content):
    content = content.replace("'", "\\'")  # escape any apostrophes in the data
    try:
        connection = mysql.connector.connect(host='127.0.0.1',
                                             port='7888',
                                             database='wikipedia',
                                             user='root',
                                             password='mypassword')
        if connection.is_connected():
            myquery = "INSERT INTO wikis (title, article) values ('" + search + "', '" + content + "');"
            cursor = connection.cursor()
            result = cursor.execute(myquery)
            connection.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
