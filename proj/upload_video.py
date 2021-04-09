import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL

UPLOAD_FOLDER = '/home/shriya/Desktop/ooad_lab/proj/uploads'
ALLOWED_EXTENSIONS = {'mp4'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        # check if file was selected
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # if file was selected and is .mp4 format
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''

    <!doctype html>
    <title>Upload File</title>
    <style>
    body {
        background-image: url(https://i0.wp.com/banglarblog.com/media/img/bg/Black_Red_Fade_YouTube_Thumbnail_Background-BanglarBlog.jpg?w=1320);
    }
    .button {
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    .button1 {background-color: #000000;}

    </style>
    <body>
    <center>
        <h1>YouTube Player</h1>
        <br>
        <br>
        <h3>In order to maintain YouTube standards, fill out the following details to upload a video:</h3>
        <form method=post enctype=multipart/form-data>
            <h4>Enter Video Name:</h4>
            <input type="text" id="name" name="name" required></input>
            <br>
            <br>
            <h4>Enter Video Description:</h4>
            <input type="text" id="description" name="description"></input>
            <br>
            <br>
            <h4>Upload Video File:</h4>
            <input type=file name=file>
            <br>
            <br>
        <h3> By uploading a video, you promise to adhere by the guidelines and standards set by YouTube. </h3>
        <button class="button button1">Upload</button>
        </form>
    </center>
    </body>
    '''

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'StateCamp123!'
app.config['MYSQL_DB'] = 'ooad_youtube'
mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        details = request.form
        name = details['name']
        description = details['description']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO video_data(title, description) VALUES (%s, %s)", (name, description))
        mysql.connection.commit()
        cur.close()
        return 'success'
    return render_template('upload_video.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)