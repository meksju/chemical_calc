from flask import Flask, render_template, jsonify, redirect, request
from flask_mysqldb import MySQL
import re
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
    if count == 0:
        with open('data/PeriodicTableJSON.json') as f:
            data = json.load(f)
            elements = data['elements']
        # Parse response
        for item in elements:
            make_db_request("""INSERT INTO `elements` (`name`, `mass`) VALUES (%s, %s)""",
                            (item['symbol'], item['atomic_mass']))


@app.route('/')
def index():
    return render_template('pages/index.html')


@app.route('/check', methods=["GET"])
def check():
    result = request.args.get('formula')
    # Checks if user provided input
    if not result:
        return apology("please write a formula")
    else:
        elements = []
        elements = re.split("([A-Z][a-z]?)(\d+)?", result)
        print(elements)
        return redirect('/')

def make_db_request(query, variables):
    cursor = mysql.connection.cursor()
    if not variables:
        result = cursor.execute(query)
    else:
        result = cursor.execute(query, variables)
    mysql.connection.commit()
    return result


def apology(message):
    return render_template("pages/apology.html", message=message)


if __name__ == '__main__':
    app.run()
