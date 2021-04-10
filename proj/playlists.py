import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='')
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'StateCamp123!'
app.config['MYSQL_DB'] = 'ooad_youtube'

mysql = MySQL(app)

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def playlists():
    return render_template('manage_playlist.html')


@app.route('/manage.py', methods=['GET', 'POST'])
def manage_playlist():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT video_title, filename FROM video_data")
        data = cur.fetchall()
        #print(data)
        l = []
        for i in range(len(data)):
            l.append(data[i][0])
        if request.form['submit_button'] == 'Create Playlist':
            return render_template('create_playlist.html', filename=data)
        elif request.form['submit_button'] == 'Delete Playlist':
            cur.execute("SELECT id, playlist_name FROM playlists")
            playlist_data = cur.fetchall()
            return render_template('delete_playlist.html', filename=playlist_data)
    return render_template('manage_playlist.html')


@app.route('/your-playlist.py', methods=['GET', 'POST'])
def create_playlist():
    if request.method == 'POST':
        details = request.form
        playlist_name = details['playlist_name']
        l = details.getlist('videos')
        l2 = []
        #print(l)
        cur = mysql.connection.cursor()
        for name in l:
            #print(type(name))
            cur.execute("INSERT INTO playlists(playlist_name, video_names) VALUES (%s, %s)", (playlist_name, name))
            query = "SELECT filename, video_title FROM video_data WHERE video_title = %s"
            cur.execute(query, (name,))
            data = cur.fetchall()
            #print(data)
            l2.append(data[0])
            #print(l2)
            mysql.connection.commit()
        cur.close()
        return render_template('/your-playlist.html', filename=l2, data=playlist_name)

@app.route('/deleted.py', methods = ['GET', 'POST'])
def delete_playlist():
    if request.method == 'POST':
        details = request.form
        l = details.getlist('playlist')
       #print("check")
       # print(l)
        cur = mysql.connection.cursor()
        for p_id in l:
            query = "DELETE FROM playlists WHERE id= %s"
            cur.execute(query, (p_id,))
            mysql.connection.commit()
        cur.execute("SELECT * FROM playlists")
        data = cur.fetchall()
        print(data)
        cur.close()
    return render_template('display_playlists.html', filename = data)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
