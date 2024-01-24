from flask import Flask, render_template, request, redirect, url_for
import pymysql
import os
import json
import re
from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)

# Database configuration
DB_HOST = 'searchtool-vidyagms9634-891a.a.aivencloud.com'
DB_PORT = 19887
DB_USER = 'avnadmin'
DB_PASSWORD = 'AVNS_2iOj7NTyvvRq3T2Yte0'
DB_NAME = 'defaultdb'
SSL_MODE = 'REQUIRED'

# Establish a connection to the database
db = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_NAME,
    # ssl-mode= ssl-mode,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route("/")
def hello_world():
    return render_template("index.html", saved=False)

@app.route('/perform_search', methods=['GET', 'POST'])
def perform_search():
    search_query = request.form.get('search')
    results = []

    try:
        if search_query is not None:
            # Split the search query into keywords
            keywords = search_query.split()

            # SQL query to search for each keyword
            query_conditions = " OR ".join(["query LIKE %s" for _ in keywords])
            query_params = ['%' + keyword + '%' for keyword in keywords]

            # Search in the db for records with state 'Added' and not 'Deleted'
            cursor = db.cursor()
            sql_query = f"SELECT result FROM data WHERE ({query_conditions}) AND state != 'Deleted'"
            cursor.execute(sql_query, query_params)
            results = cursor.fetchall()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cursor.close()

    return render_template('search_results.html', results=results)


@app.route('/save_search', methods=['POST'])
def save_search():
    query = request.form['search']
    results = request.form.get('results', '')

    # Remove HTML tags from results
    results = re.sub(r'<[^>]+>', '', results)

    try:
        # Check if the query is present in the data table
        cursor = db.cursor()
        cursor.execute("SELECT * FROM data WHERE LOWER(query) = LOWER(%s)", (query,))
        existing_record = cursor.fetchone()

        if existing_record and existing_record['state'] != 'Deleted':
            # If the query is present and its state is not 'Deleted', update the results
            cursor.execute("UPDATE data SET result = %s WHERE LOWER(query) = LOWER(%s)", (results, query))
            db.commit()
        else:
            # If the query is not present or its state is 'Deleted', insert into both tables with 'Added' state
            cursor.execute("INSERT INTO data (query, result, state) VALUES (%s, %s, 'Added')", (query, results))
            db.commit()

        cursor.execute("INSERT INTO search_history_new (query, results, state) VALUES (%s, %s, 'Added')", (query, results))
        db.commit()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cursor.close()

    return redirect(url_for('edit_results', query=query))


@app.route('/edit_results', methods=['GET', 'POST'])
def edit_results():
    query = request.args.get('query')
    result = None

    try:
        # Fetch the result for the given query
        cursor = db.cursor()
        cursor.execute("SELECT result FROM data WHERE LOWER(query) = LOWER(%s) AND state != 'Deleted'", (query,))
        result = cursor.fetchone()['result']
        
        if request.method == 'POST':
            # Update the query and result in the 'data' table
            modified_query = request.form['modified_query']
            modified_results = request.form['modified_results']
            cursor.execute("UPDATE data SET query = %s, result = %s WHERE LOWER(query) = LOWER(%s)", (modified_query, modified_results, query))
            db.commit()

            # Check if there's an entry in 'search_history_new' table
            cursor.execute("SELECT * FROM search_history_new WHERE LOWER(query) = LOWER(%s)", (query,))
            existing_entry = cursor.fetchone()

            # Update or insert into 'search_history_new' table
            if existing_entry:
                cursor.execute("UPDATE search_history_new SET query = %s, results = %s WHERE LOWER(query) = LOWER(%s)", (modified_query, modified_results, query))
            else:
                cursor.execute("INSERT INTO search_history_new (query, results, state) VALUES (%s, %s, 'Added')", (modified_query, modified_results))
            
            db.commit()

            return redirect(url_for('hello_world', success=True))
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cursor.close()

    return render_template('edit_results.html', query=query, result=result)


@app.route('/remove_search', methods=['POST'])
def remove_search():
    query = request.form.get('query')
    
    try:
        cursor = db.cursor()
        rows_affected = cursor.execute("UPDATE data SET state = 'Deleted' WHERE LOWER(query) LIKE LOWER(%s)", ('%' + query + '%',))
        db.commit()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cursor.close()

    return redirect(url_for('hello_world', removed=True))


@app.route('/reset', methods=['POST'])
def reset_website():
    return redirect(url_for('hello_world', reset=True))

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6061)