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
    return render_template('index.html') # takes us to index.html (open index.html to understand flow)

# upon clicking a button in index.html, we arrive at /manage-video.py
@app.route('/manage-video.py', methods=['GET', 'POST'])
def manage_video():
    # if a button was clicked, the method will be 'POST'
    if request.method == 'POST':
        if request.form['submit_button'] == 'Upload Video':
            return render_template('upload.html') # if Upload Video button was clicked, open upload.html file to trace the flow

        elif request.form['submit_button'] == 'Delete Video':
            cur = mysql.connection.cursor() # establish connection
            cur.execute("SELECT video_title, filename, id FROM video_data") 
            data = cur.fetchall() # fetches all data retrieved in previous SQL statement
            mysql.connection.commit() # commit query
            cur.close() # close connection
            return render_template('delete_video.html', filename=data) # send data fetched to delete_video.html

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
           
            #return redirect(url_for('uploaded_file', filename=filename))
        cur = mysql.connection.cursor() # establish connection
        # insert all video related data into a table called video_data in databse ooad_youtube
        cur.execute("INSERT INTO video_data(video_title, video_description, video_url, filename) VALUES (%s, %s, %s, %s)", (title, description, path, filename))

        # code to display all videos in DB
        cur.execute("SELECT video_title, filename FROM video_data")
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

    cur.execute("SELECT id, video_title, filename FROM video_data") # select remaining videos
    data = cur.fetchall()
   # print(data)
    mysql.connection.commit()
    cur.close()
    return render_template('uploaded_video.html', filename=data) # send fetched data to uploaded_video.html (reusing a file here)
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True) # allow debugging only in production mode

