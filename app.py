from flask import Flask, render_template
from flask_mysqldb import MySQL
# noinspection PyUnresolvedReferences
import json
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'chemical_calc'

mysql = MySQL(app)


@app.before_first_request
def insert_elements():
    count = make_db_request("""SELECT * FROM `elements`""", "")
    print(count)
    if count == 0:
        with open('data/PeriodicTableJSON.json') as f:
            data = json.load(f)
            elements = data['elements']
        # Parse response
        for item in elements:
            make_db_request("""INSERT INTO `elements` (`name`, `mass`) VALUES (%s, %s)""",
                            (item['symbol'], item['atomic_mass']))


@app.route('/')
def hello_world():
    result = make_db_request("""SELECT * FROM `elements`""", "")
    print(result)
    return render_template('pages/index.html')


def make_db_request(query, variables):
    cursor = mysql.connection.cursor()
    if not variables:
        result = cursor.execute(query)
    else:
        result = cursor.execute(query, variables)
    mysql.connection.commit()
    return result


if __name__ == '__main__':
    app.run()
