from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import sqlite3, os
import requests
from scrapper import fetch_case

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev")

DB = 'cases.db'

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute('''
      CREATE TABLE IF NOT EXISTS queries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_type TEXT, case_number TEXT, filing_year TEXT,
        parties TEXT, filing_date TEXT, next_hearing TEXT,
        order_date TEXT, order_url TEXT,
        raw_html TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    ''')
    conn.commit(); conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        case_type = request.form['case_type']
        case_number = request.form['case_number']
        filing_year = request.form['filing_year']
        try:
            data = fetch_case(case_type, case_number, filing_year)
            # store
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute('''
              INSERT INTO queries(case_type,case_number,filing_year,
                parties,filing_date,next_hearing,order_date,order_url,raw_html)
              VALUES (?,?,?,?,?,?,?,?,?)
            ''', (
              case_type, case_number, filing_year,
              data['parties'], data['filing_date'], data['next_hearing'],
              data['latest_order']['date'] if data['latest_order'] else None,
              data['latest_order']['pdf_url'] if data['latest_order'] else None,
              data['raw_html']
            ))
            conn.commit(); conn.close()
            return render_template('results.html', data=data)
        except Exception as e:
            flash(f"Error fetching data: {str(e)}")
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/download')
def download():
    url = request.args.get('url')
    r = requests.get(url)
    with open('temp.pdf', 'wb') as f: f.write(r.content)
    return send_file('temp.pdf', as_attachment=True, attachment_filename='order.pdf')

if __name__ == '__main__':
    app.run(debug=True)
