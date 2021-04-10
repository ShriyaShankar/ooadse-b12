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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/manage-video.py', methods=['GET', 'POST'])
def manage_video():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Upload Video':
            return render_template('upload.html')
        elif request.form['submit_button'] == 'Delete Video':
            cur = mysql.connection.cursor()
            cur.execute("SELECT video_title, filename, id FROM video_data")
            data = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return render_template('delete_video.html', filename=data)
    return render_template(index.html)


@app.route('/upload.py', methods=['GET', 'POST'])
def upload_video():
    if request.method == "POST":
        path = ''
        filename = ''
        details = request.form
        title = details['video_title']
        description = details['video_description']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
           
            #return redirect(url_for('uploaded_file', filename=filename))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO video_data(video_title, video_description, video_url, filename) VALUES (%s, %s, %s, %s)", (title, description, path, filename))

        cur.execute("SELECT video_title, filename FROM video_data")
        data = cur.fetchall()
        print(data)
        l = []
        for i in range(len(data)):
            l.append(data[i][0])
        print(l)
        mysql.connection.commit()
        cur.close()
        return render_template('uploaded_video.html', filename=data)

@app.route('/deleted.py', methods=['GET', 'POST'])
def delete_from_db():
    if request.method == 'POST':
        details = request.form
        l = details.getlist('videos')
        cur = mysql.connection.cursor()
        for name in l:
            query = "DELETE FROM video_data WHERE id = %s"
            cur.execute(query, (name,))
            mysql.connection.commit()

    cur.execute("SELECT video_title, filename FROM video_data")
    data = cur.fetchall()
   # print(data)
    l = []
    for i in range(len(data)):
        l.append(data[i][0])
   # print(l)
    mysql.connection.commit()
    cur.close()
    return render_template('uploaded_video.html', filename=data)
        

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

