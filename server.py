from flask import Flask, request, send_from_directory, send_file

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')


@app.route('/rss')
def send_rss():
    return send_file('test.xml', mimetype="application/atom+xml")


if __name__ == "__main__":
    app.run()
