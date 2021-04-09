from flask import Flask, request,render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/upload_video')
def upload_video():
    return render_template('upload_video.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)