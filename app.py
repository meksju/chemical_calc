import requests
from flask import Flask, render_template, redirect, request
from flask_mysqldb import MySQL
import re
import json
from flask import flash

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'chemical_calc'

mysql = MySQL(app)


@app.before_first_request
def insert_elements():
    count = make_db_request("""SELECT count(*) FROM `elements`""", "")
    if count[0][0] == 0:
        with open('data/PeriodicTableJSON.json') as f:
            data = json.load(f)
            elements = data['elements']
        # Parse response
        for item in elements:
            make_db_request("""INSERT INTO `elements` (`name`, `mass`) VALUES (%s, %s)""",
                            (item['symbol'], item['atomic_mass']))
        # add existed formulas from wiki
        r = requests.get("https://en.wikipedia.org/wiki/Glossary_of_chemical_formulae")
        try:
            from BeautifulSoup import BeautifulSoup
        except ImportError:
            from bs4 import BeautifulSoup
        html = r.text
        parsed_html = BeautifulSoup(html, "html.parser")
        table_data = parsed_html.find_all('table', attrs={'class': 'wikitable'})
        for table in table_data:
            lines = table.text.split("\n")
            for line in lines:
                if line != "" and line[0].isupper():
                    make_db_request("""INSERT INTO `formulas` (compound) VALUES (%s)""", [line])


@app.route('/')
def index():
    return render_template('pages/index.html')


@app.route('/check', methods=["GET"])
def check():
    global data
    result = request.args.get('formula')
    # Checks if input exists in db formulas
    match = make_db_request("""SELECT compound FROM `formulas` WHERE compound=%s""", [result])
    if len(match) == 0:
        flash("There is no such compound!")
        return redirect("/")
    else:
        # Creats array for parsed elements
        element_number = []
        parsed_elements = []
        elements = re.split("([A-Z][a-z]?)(\d+)?", result)
        for element in elements:
            if element:
                parsed_elements.append(element)
        # Loops through parsed elements and their indexes to check element and it`s number
        for index, object in enumerate(parsed_elements):
            # Checks if current object is string and if it isn't last element in array
            if object.isalpha():
                element_number.append(object)
                # Checks next element
                if index + 1 < len(parsed_elements):
                    if parsed_elements[index + 1].isalpha():
                        element_number.append("1")
                    elif parsed_elements[index + 1].isdigit():
                        element_number.append(parsed_elements[index + 1])
                if index == len(parsed_elements) - 1 and object.isalpha():
                    element_number.append("1")
        # Makes operations with array of elements
        formula = []
        info = {}
        for element in element_number:
            if re.match(r'^([\s\d]+)$', element):
                info["number"] = int(element)
            else:
                data = make_db_request("""SELECT name, mass FROM `elements` WHERE name=%s""", [element])
                # Splitting by line data elements to get list
                for item in data:
                    info["name"] = item[0]
                    info["mass"] = item[1]
            if "name" in info and "mass" in info and "number" in info:
                formula.append(info)
                info = {}
        return render_template('pages/index.html', formula=formula)


def make_db_request(query, variables):
    cursor = mysql.connection.cursor()
    if not variables:
        cursor.execute(query)
        result = cursor.fetchall()
    else:
        cursor.execute(query, variables)
        result = cursor.fetchall()
    cursor.close()
    mysql.connection.commit()
    return result


def apology(message):
    return render_template("pages/apology.html", message=message)


if __name__ == '__main__':
    app.run()
