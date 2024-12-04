from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL connection details
db_config = {
    'host': '//',     # server address
    'user': '//',          # username
    'password': '//',  # password
    'database': '//'   # database name
}

def get_tables():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall() if table[0]]
    conn.close()
    return tables

@app.route('/')
def index():
    tables = get_tables()
    return render_template('index.html', tables=tables)

@app.route('/table/<table_name>')
def show_table(table_name):
    # Retrieve the error message if present in the query string
    error_message = request.args.get('error_message', None)

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = [col['Field'] for col in cursor.fetchall()]
    conn.close()

    return render_template('table.html', table_name=table_name, rows=rows, columns=columns, error_message=error_message)


@app.route('/add/<table_name>', methods=['POST'])
def add_entry(table_name):
    data = request.form.to_dict()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    placeholders = ', '.join(['%s'] * len(data))
    sql = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({placeholders})"
    try:
        cursor.execute(sql, list(data.values()))
        conn.commit()
        error_message = None
    except mysql.connector.Error as err:
        conn.rollback()  # Rollback in case of error
        error_message = f"SQL Error: {err}"
    finally:
        conn.close()
    
    # Show error message
    if error_message:
        return redirect(url_for('show_table', table_name=table_name, error_message=error_message))
    else:
        return redirect(url_for('show_table', table_name=table_name))

@app.route('/delete/<table_name>/<int:id>')
def delete_entry(table_name, id):
    pk_column = {'Students': 'Student_ID', 'Buildings': 'Building_ID',
                 'Departments': 'Department_ID', 'Professors': 'Professor_ID',
                 'Classes': 'Class_ID'}.get(table_name)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE {pk_column} = %s", (id,))
        conn.commit()
        error_message = None
    except mysql.connector.Error as err:
        conn.rollback()  # Rollback in case of error
        error_message = f"SQL Error: {err}"
    finally:
        conn.close()

    # Redirect back to the table page with the error message if there was an issue
    if error_message:
        return redirect(url_for('show_table', table_name=table_name, error_message=error_message))
    else:
        return redirect(url_for('show_table', table_name=table_name))

@app.route('/execute_query', methods=['POST'])
def execute_query():
    query = request.form['query']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = cursor.column_names
        query_results = {
            'rows': rows,
            'columns': columns
        }
        error_message = None
    except mysql.connector.Error as err:
        query_results = None
        error_message = f"SQL Error: {err}"
    finally:
        conn.close()

    return render_template('index.html', tables=get_tables(), query_results=query_results, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
