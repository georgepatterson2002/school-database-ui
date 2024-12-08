from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Define database configuration
db_config = {
    'host': '//',
    'user': '//',
    'password': '//',
    'database': '//'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def get_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall() if table[0]]
    conn.close()
    return tables

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch unique building names
    try:
        cursor.execute("SELECT DISTINCT Building_Name FROM Buildings")
        building_names = [row['Building_Name'] for row in cursor.fetchall()]
        print("Building names fetched:", building_names)  # Debugging statement
    except Exception as e:
        print("Error fetching building names:", e)
        building_names = []

    # Fetch unique professor names
    try:
        cursor.execute("SELECT DISTINCT CONCAT(First_Name, ' ', Last_Name) AS full_name FROM Professors")
        professor_names = [row['full_name'] for row in cursor.fetchall()]
        print("Professor names fetched:", professor_names)  # Debugging statement
    except Exception as e:
        print("Error fetching professor names:", e)
        professor_names = []

    cursor.close()
    conn.close()

    # Render index with no query results
    return render_template('index.html', 
                           tables=get_tables(),
                           building_names=building_names,
                           professor_names=professor_names,
                           query_results=None)  # Ensure no search triggers prematurely


@app.route('/table/<table_name>')
def show_table(table_name):
    error_message = request.args.get('error_message', None)

    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join(['%s'] * len(data))
    sql = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({placeholders})"
    try:
        cursor.execute(sql, list(data.values()))
        conn.commit()
        error_message = None
    except mysql.connector.Error as err:
        conn.rollback()
        error_message = f"SQL Error: {err}"
    finally:
        conn.close()

    if error_message:
        return redirect(url_for('show_table', table_name=table_name, error_message=error_message))
    else:
        return redirect(url_for('show_table', table_name=table_name))

@app.route('/delete/<table_name>/<int:id>')
def delete_entry(table_name, id):
    pk_column = {'Students': 'Student_ID', 'Buildings': 'Building_ID',
                 'Departments': 'Department_ID', 'Professors': 'Professor_ID',
                 'Classes': 'Class_ID'}.get(table_name)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE {pk_column} = %s", (id,))
        conn.commit()
        error_message = None
    except mysql.connector.Error as err:
        conn.rollback()
        error_message = f"SQL Error: {err}"
    finally:
        conn.close()

    if error_message:
        return redirect(url_for('show_table', table_name=table_name, error_message=error_message))
    else:
        return redirect(url_for('show_table', table_name=table_name))

@app.route('/query', methods=['GET'])
def query():
    # Fetch dropdown context first
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT DISTINCT Building_Name FROM Buildings")
        building_names = [row['Building_Name'] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT CONCAT(First_Name, ' ', Last_Name) AS full_name FROM Professors")
        professor_names = [row['full_name'] for row in cursor.fetchall()]
    except Exception as e:
        print("Error fetching dropdown values:", e)
        building_names = []
        professor_names = []
    finally:
        cursor.close()
        conn.close()

    # Check if any query parameter is provided; if none, return to index without showing results
    if not any(request.args.get(key) for key in ['building_name', 'professor_name', 'room_count', 'gpa_threshold', 'unit_count']):
        return render_template(
            'index.html',
            tables=get_tables(),
            building_names=building_names,
            professor_names=professor_names,
            query_results=None  # No results to show
        )

    # Execute the query only if parameters are provided
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Determine query logic
        if 'building_name' in request.args and request.args['building_name']:
            query_sql = """
                SELECT c.Class_Code, c.Class_Name, p.First_Name, p.Last_Name, b.Building_Name 
                FROM Classes c
                JOIN Professors p ON c.Professor_ID = p.Professor_ID
                JOIN Buildings b ON c.Building_ID = b.Building_ID
                WHERE b.Building_Name = %s
            """
            params = (request.args['building_name'],)

        elif 'professor_name' in request.args and request.args['professor_name']:
            query_sql = """
                SELECT c.Class_Code, c.Class_Name, c.Time, c.Day 
                FROM Classes c
                JOIN Professors p ON c.Professor_ID = p.Professor_ID
                WHERE CONCAT(p.First_Name, ' ', p.Last_Name) = %s
            """
            params = (request.args['professor_name'],)

        elif 'room_count' in request.args and request.args['room_count']:
            query_sql = """
                SELECT * 
                FROM Buildings 
                WHERE Number_of_Rooms < %s
            """
            params = (request.args['room_count'],)

        elif 'gpa_threshold' in request.args and request.args['gpa_threshold']:
            query_sql = """
                SELECT * 
                FROM Students 
                WHERE GPA > %s
            """
            params = (request.args['gpa_threshold'],)

        elif 'unit_count' in request.args and request.args['unit_count']:
            query_sql = """
                SELECT * 
                FROM Classes 
                WHERE Units = %s
            """
            params = (request.args['unit_count'],)

        else:
            # If no valid query params are provided
            query_results = []
            cursor.close()
            conn.close()
            return render_template(
                'index.html',
                tables=get_tables(),
                building_names=building_names,
                professor_names=professor_names,
                query_results=query_results
            )

        # Execute query safely
        cursor.execute(query_sql, params)
        query_results = cursor.fetchall()
    except mysql.connector.Error as err:
        query_results = []
        print(f"SQL Error: {err}")
    finally:
        cursor.close()
        conn.close()

    # Render results dynamically
    return render_template(
        'index.html',
        tables=get_tables(),
        building_names=building_names,
        professor_names=professor_names,
        query_results=query_results
    )


if __name__ == '__main__':
    app.run(debug=True)
