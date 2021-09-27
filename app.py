import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for
from urllib.parse import urlparse
from ipaddress import ip_address
from waitress import serve

db = 'efurls.db'

def get_db_connection():
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'changeme'
app.config.from_pyfile('config.py')

hashids = Hashids(min_length=8, salt=app.config['SECRET_KEY'])

@app.route('/')
def gotoapi():
    return redirect(url_for('index'))

@app.route('/api/v1/shorten/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        if not urlparse(url).scheme and not urlparse(url).netloc:
            print(urlparse(url))
            flash('The URL is invalid. Format required is protocol/name (https://element.io)')
            return redirect(url_for('index'))

        try:
            ip_address(url.replace('http://', '').replace('https://', ''))
            flash('Please use names rather than IP addresses')
            return redirect(url_for('index'))
        except ValueError:
            pass

        url_data = conn.execute('INSERT INTO efurls (original_url) VALUES (?)',
                                (url,))
        conn.commit()
        conn.close()

        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.url.replace("shorten", "lookup") + hashid

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/api/v1/lookup/<id>')
def url_redirect(id):
    conn = get_db_connection()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url, clicks FROM efurls'
                                ' WHERE id = (?)', (original_id,)
                                ).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        conn.execute('UPDATE efurls SET clicks = ? WHERE id = ?',
                     (clicks+1, original_id))

        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))

@app.route('/api/v1/stats')
def stats():
    conn = get_db_connection()
    db_urls = conn.execute('SELECT id, created, original_url, clicks FROM efurls'
                           ).fetchall()
    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    return render_template('stats.html', urls=urls)

if __name__ == "__main__":
    serve(app, listen='*:8000')
