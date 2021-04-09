import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
 

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'StateCamp123!'
app.config['MYSQL_DB'] = 'ooad_youtube'

mysql = MySQL(app)
#mysql.init_app(app)

@app.route('/')
def testing():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT video_url FROM video_data')
    data = cursor.fetchall()
    print(data)
    #data = cur.fetchall()
    mysql.connection.commit()
    cursor.close()

    temp = data[0]['video_url']
    print(temp)
    #print(data[last][0])

    return '''
        <html>
            <body>
                <p>hello from html</p>
                <video width="320" height="240" controls>
                <source src="/uploads/{{filename}}" type="video/mp4" controls/>
                </video>
            </body>
        </html>
    '''
    return 'success'



if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)



