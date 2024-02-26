from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import pymysql
import os
import json
import re
from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = b'@\x87)sO\x13\xdfKK\xd8\xcd-\x10\xb6>\xab\xe95\xba^\x81n\x8fw'

# searchbase configuration
DB_HOST = 'searchtool-vidyagms9634-891a.a.aivencloud.com'
DB_PORT = 19887
DB_USER = 'avnadmin'
DB_PASSWORD = 'AVNS_2iOj7NTyvvRq3T2Yte0'
DB_NAME = 'defaultdb'
SSL_MODE = 'REQUIRED'



# Set the time zone to 'Asia/Kolkata'
# try:
#     cursor = db.cursor()
#     cursor.execute("SET time_zone = 'Asia/Kolkata'")
#     db.commit()
# except Exception as e:
#     print(f"An error occurred while setting the time zone: {str(e)}")
# finally:
#     cursor.close()


@app.route("/")
def hello_world():
    return render_template("index.html", saved=False)

@app.route('/perform_search', methods=['GET', 'POST'])
def perform_search():
    # Establish a connection to the database
    db = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = db.cursor()
    search_query = request.form.get('search')
    results_dict = {}

    try:
        keywords = search_query.split()
        for keyword in keywords:
            sql_query = f"SELECT result FROM search WHERE query LIKE '%{keyword}%' AND state != 'Deleted'"
            cursor.execute(sql_query)
            keyword_results = cursor.fetchall()
            for result in keyword_results:
                result_name = result['result']
                if result_name not in results_dict:
                    results_dict[result_name] = result
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    cursor.close()
    db.close()

    results = list(results_dict.values())  # Get the values of the dictionary as a list

    return render_template('search_results.html', results=results)


@app.route('/save_search', methods=['POST'])
def save_search():
    return redirect(url_for('edit_results'))


@app.route('/edit_results', methods=['GET', 'POST'])
def edit_results():
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
    cursor = db.cursor()
    query = request.form['search']
    result = ''
    state = '' 

    try:
        cursor = db.cursor()
        cursor.execute("SELECT result, state FROM search WHERE LOWER(query) = LOWER(%s)", (query,))
        result_row = cursor.fetchone()
        
        if result_row:
            result = result_row['result']
            state = result_row['state'] 

        if request.method == 'POST':
            modified_query = request.form['modified_query']
            modified_results = request.form['modified_results']
            
            if state == '':
                # Insert the new query into the search table
                cursor.execute("INSERT INTO search (query, result, state) VALUES (%s, %s, %s)", (modified_query, modified_results, 'Added'))
                db.commit()
            elif state == 'Deleted' or state == 'Added':
                # If the query is in 'Deleted' or 'Added' state, update the results and change state to 'Updated'
                cursor.execute("UPDATE search SET result = %s, state = 'Updated' WHERE LOWER(query) = LOWER(%s)", (modified_results, modified_query))
            else:
                # If the query is in 'Updated' state, just update the results
                cursor.execute("UPDATE search SET result = %s WHERE LOWER(query) = LOWER(%s)", (modified_results, modified_query))
            
            # Always add an entry to 'search_history_new' table
            cursor.execute("INSERT INTO search_history_new (query, results, state) VALUES (%s, %s, 'Added')", (modified_query, modified_results))
            db.commit()

            return redirect(url_for('hello_world', success=True))
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    cursor.close()
    db.close()

    return render_template('edit_results.html', query=query, result=result)



@app.route('/remove_search', methods=['POST'])
def remove_search():
    # Establish a connection to the database
    db = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = db.cursor()
    query_value = request.form.get('query')
    db.autocommit(True)
    
    try:
        cursor = db.cursor()
        row = cursor.execute(f"""SET @searchid:=(SELECT search.id FROM search WHERE search.query=%s AND search.state!='Deleted')""",query_value)
        rows_affected = cursor.execute("UPDATE search SET state = 'Deleted' WHERE search.id=@searchid")
        
        # Redirect to the HTML page after successful removal
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        flash("An error occurred while removing the search", "error")
        clear_results = False
    cursor.close()
    db.close()
    return redirect(url_for('hello_world', success=True))

    # Return JSON response with success message and clear_results indication
    # return jsonify({'message': 'Search successfully removed', 'clear_results': clear_results})

@app.route('/reset', methods=['POST'])
def reset_website():
    return redirect(url_for('hello_world', reset=True))

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=6061, debug=True)
    app.run(debug=True)