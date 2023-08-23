from flask import Flask, request

app = Flask(__name__)

# Define a dictionary to hold search data
search_data = {}

# Read data from search.txt and populate the search_data dictionary
with open('search.txt', 'r') as file:
    lines = file.readlines()
    for line in lines:
        key, value = line.strip().split('@@')
        search_data[key] = value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('search')
    results = []

    if query in search_data:
        results.append(search_data[query])

    return render_template('search_results.html')  # Return the search results as plain text

if __name__ == '__main__':
    app.run(debug=True)
