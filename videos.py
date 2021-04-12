import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='')
 
# connect to databse
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'StateCamp123!'
app.config['MYSQL_DB'] = 'ooad_youtube'

# initialise mysql
mysql = MySQL(app)

class Video:
    def __init__(self, title, desc, path, filename):
        self.title = title
        self.desc = desc
        self.path = path
        self.filename = filename

    def display_data(self):
        print("Video Title: ", self.title)
        print("Description: ", self.desc)
        print("Filename: ", self.filename)
        print("Path: ", self.path)
    
    def upload_to_db(self):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO video_data(video_title, video_description, video_url, filename) VALUES (%s, %s, %s, %s)", (self.title, self.desc, self.path, self.filename))
        mysql.connection.commit() # commit query
        cur.close() # close connection
    
    def delete_from_db(self, l):
        cur = mysql.connection.cursor()
        for name in l: # for every id to be deleted 
            query = "DELETE FROM video_data WHERE id = %s"
            cur.execute(query, (name,))
            mysql.connection.commit()


class Playlist:
    def __init__(self, name, video_names):
        self.name = name
        self.video_names = video_names
    def display_playlists(self):
        print("Playlist Name: ", self.name)
        print("Videos: ", self.video_names)
    def playlist_to_db(self):
       # str1 = ''.join(list1)
        cur = mysql.connection.cursor()
        for video in self.video_names:
            cur.execute("INSERT INTO playlists(playlist_name, video_names) VALUES (%s, %s)", (self.name, video))
            mysql.connection.commit()
        cur.close()

    def del_playlist(self, l):
        cur = mysql.connection.cursor()
        for name in l:
            query = "DELETE FROM playlists WHERE playlist_name= %s"
            cur.execute(query, (name,))
            mysql.connection.commit()
        cur.close()
    def is_empty(self, l):
        if not l:
            return True


UPLOAD_FOLDER = './static/uploads' # define path to save all uploaded videos
ALLOWED_EXTENSIONS = {'mp4'} # allowed file types
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# format the file url
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# the first page we see is index.html (/ is root directory)
@app.route('/', methods=['GET', 'POST'])
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT video_title, video_description, filename FROM video_data")
    data = cur.fetchall()
    print(len(data))
    mysql.connection.commit()
    cur.close()
    if len(data) == 0:
        return render_template('index.html') # takes us to index.html (open index.html to understand flow)
    else:
        return render_template('index.html', filename=data) # takes us to index.html (open index.html to understand flow)

# upon clicking a button in index.html, we arrive at /manage-video.py
@app.route('/manage-video.py', methods=['GET', 'POST'])
def manage():
    # if a button was clicked, the method will be 'POST'
    if request.method == 'POST':
        if request.form['submit_button'] == 'Upload Video':
            return render_template('upload.html') # if Upload Video button was clicked, open upload.html file to trace the flow

        elif request.form['submit_button'] == 'Delete Video':
            cur = mysql.connection.cursor() # establish connection
            cur.execute("SELECT video_title, filename, id, video_description FROM video_data") 
            data = cur.fetchall() # fetches all data retrieved in previous SQL statement
            if len(data) == 0:
                return render_template('/error_handle.html', filename='You do not have any videos to delete.')
            mysql.connection.commit() # commit query
            cur.close() # close connection
            return render_template('delete_video.html', filename=data) # send data fetched to delete_video.html

        elif request.form['submit_button'] == 'Create Playlist':
            cur = mysql.connection.cursor()
            cur.execute("SELECT video_title, filename, video_description FROM video_data")
            data = cur.fetchall()
           # print(data)
            if len(data)==0: 
                return render_template('/error_handle.html', filename='You do not have videos. Go back to Home to upload videos.')
            #print(data)
            l = []
            for i in range(len(data)):
                l.append(data[i][0])
            return render_template('create_playlist.html', filename=data)

        elif request.form['submit_button'] == 'Delete Playlist':
            cur = mysql.connection.cursor()
            cur.execute("SELECT playlist_name FROM playlists")
            playlist_data = cur.fetchall()
            print(playlist_data)
            s = set()
            for name in playlist_data:
                s.add(name[0])
            print(s)
            if len(s)==0:
                return render_template('/error_handle.html', filename='You have deleted all your playlists. Go back Home to create new playlist.')
            cur = mysql.connection.cursor()
            cur.execute("SELECT video_title, video_description, filename FROM video_data")
            data2 = cur.fetchall()
            if len(data2)==0:
                return render_template("/error_handle.html", filename='You do not have any videos yet.')
            mysql.connection.commit()
            cur.close()
            return render_template('delete_playlist.html', filename=s, data=data2)
    # if neither, go back to index.html for user to choose 
    return render_template(index.html)

# on clicking Upload in upload.html, we arrive at /upload.py
@app.route('/upload.py', methods=['GET', 'POST'])
def upload_video():
    if request.method == "POST":
        path = ''
        filename = ''
        details = request.form # get the form details from upload.html form
        title = details['video_title'] # video titles are stored by indexing 'name' attribute 
        description = details['video_description'] # description is stored by indexing 'name' attribute
        file = request.files['file'] 
        if file and allowed_file(file.filename): # checks if file is uploaded and if it is a valid file name
            filename = secure_filename(file.filename) # ASCII-only secure file name
            #print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # save file
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # create path
            video = Video(title, description, path, filename)
            video.display_data()
           
            #return redirect(url_for('uploaded_file', filename=filename))
        cur = mysql.connection.cursor() # establish connection
        video.upload_to_db()
        # code to display all videos in DB
        cur.execute("SELECT video_title, filename, video_description FROM video_data")
        data = cur.fetchall() # fetches data returned by previous SQL statement
        #print(data)
        mysql.connection.commit() # commits the query
        cur.close() # close the sql connection

        # pass the fetched data to html file
        return render_template('uploaded_video.html', filename=data) # once a file is uploaded, go to uploaded_video.html

# upon clicking Delete button in delete_video.html, we are routed to /deleted.py 
# it deletes entries from db and then displays which videos are left
@app.route('/deleted.py', methods=['GET', 'POST'])
def delete_from_db():
    if request.method == 'POST':
        details = request.form
        l = details.getlist('videos') # gets all videos selected for deletion in the form of a list
        cur = mysql.connection.cursor()
        for name in l: # for every id to be deleted 
            query = "DELETE FROM video_data WHERE id = %s"
            cur.execute(query, (name,))
            mysql.connection.commit()

    cur.execute("SELECT video_title, filename, video_description FROM video_data") # select remaining videos
    data = cur.fetchall()
    if len(data)==0:
        return render_template("/error_handle.html", filename='You do not have any videos. Go back to Home to upload new videos.')
   # print(data)
    mysql.connection.commit()
    cur.close()
    return render_template('uploaded_video.html', filename=data) # send fetched data to uploaded_video.html (reusing a file here)


@app.route('/your-playlist.py', methods=['GET', 'POST'])
def create_playlist():
    if request.method == 'POST':
        details = request.form
        playlist_name = details['playlist_name']
        l = details.getlist('videos')
        playlist = Playlist(playlist_name, l)
        playlist.display_playlists()
        cur = mysql.connection.cursor()
        query = "SELECT playlist_name FROM playlists WHERE playlist_name=%s"
        cur.execute(query, (playlist_name,))
        data = cur.fetchall()
        if len(data) > 0:
            return render_template('/error_handle.html', filename='Playlist Name already exists.')
        playlist.playlist_to_db()
        #print(l)
        if playlist.is_empty(l):
            return render_template('/error_handle.html', filename=playlist_name, data='Your playlist is empty.')
        else:
            cur = mysql.connection.cursor()
            l2 = []
            for name in l:
                query = "SELECT filename, video_title FROM video_data WHERE video_title = %s"
                cur.execute(query, (name,))
                data = cur.fetchall()
                l2.append(data[0])
                mysql.connection.commit()
            cur.close()
            #print(l2)
            return render_template('/your-playlist.html', filename=l2, data=playlist_name)

@app.route('/deleted-playlist.py', methods = ['GET', 'POST'])
def delete_playlist():
    if request.method == 'POST':
        playlist = Playlist("", "")
        details = request.form
        l = details.getlist('playlist')
        print(l)
        playlist.del_playlist(l)
       #print("check")
       # print(l)
        cur = mysql.connection.cursor()
        cur.execute("SELECT playlist_name FROM playlists")
        data = cur.fetchall()
        if len(data) == 0:
            return render_template('/error_handle.html', filename='You do not have any playlists.')
        print(data)
        s = set()
        for name in data:
            s.add(name[0])
        print(s)
        cur.close()
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT video_title, video_description, filename FROM video_data")
    data2 = cur.fetchall()
    if len(data2)==0:
        return render_template("/error_handle.html", filename='You do not have any videos yet.')
    mysql.connection.commit()
    cur.close()
    return render_template('display_playlists.html', filename = s, data=data2)
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True) # allow debugging only in production mode

