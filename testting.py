from flask import Flask, jsonify, request, redirect, url_for
import pymysql
import os
import pandas as pd
from dotenv import load_dotenv
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

load_dotenv()

app.config['DB_HOST'] = os.getenv('DB_HOST')
app.config['DB_USER'] = os.getenv('DB_USER')
app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['DB_NAME'] = os.getenv('DB_NAME')
app.config['DB_PORT'] = int(os.getenv('DB_PORT'))


def create_connection():
    return pymysql.connect(host=app.config['DB_HOST'], user=app.config['DB_USER'], password=app.config['DB_PASSWORD'],
                           database=app.config['DB_NAME'], port=app.config['DB_PORT'])


@app.route('/perform_search', methods=['GET'])
def search_results():
    connection = create_connection()
    to_search = request.args.get('search_input')
    print(f"Search query: {to_search}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT * FROM search WHERE search.state !='Deleted' AND search.query LIKE '%{to_search}%' ORDER BY search.updated""")
            search_results_data = cursor.fetchall()
            print(f"Search results: {search_results_data}")
            search_dataframe = pd.DataFrame(search_results_data, columns=[x[0] for x in cursor.description])
            return search_dataframe.to_json(orient="records")
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
