import argparse
import pymysql

# Database configuration
DB_HOST = 'searchtool-vidyagms9634-891a.a.aivencloud.com'
DB_PORT = 19887
DB_USER = 'avnadmin'
DB_PASSWORD = 'AVNS_2iOj7NTyvvRq3T2Yte0'
DB_NAME = 'defaultdb'

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

def search_in_db(query):
    results = []

    try:
        # Remove 't_' prefix
        keyword = query[2:]

        # SQL query to search for the keyword
        query_conditions = "query LIKE %s AND state != 'Deleted'"
        query_param = '%' + keyword + '%'

        # Search in the db for records with state 'Added' and not 'Deleted'
        cursor = db.cursor()
        sql_query = f"SELECT result FROM data WHERE {query_conditions}"
        cursor.execute(sql_query, (query_param,))
        results = cursor.fetchall()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cursor.close()

    return results

def display_results(results):
    if results:
        for result in results:
            print(result['result'])
    else:
        print("No results found.")

def main():
    parser = argparse.ArgumentParser(description='Search in the database.')
    parser.add_argument('query', type=str, help='Search query with underscore (e.g., t_fav)')

    args = parser.parse_args()
    query = args.query

    search_results = search_in_db(query)
    display_results(search_results)

if __name__ == "__main__":
    main()
