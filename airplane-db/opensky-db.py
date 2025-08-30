import sqlite3
import csv

def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(name) 
        FROM sqlite_master 
        WHERE type='table' AND name=?
        """, (tablename,))
    exists = dbcur.fetchone()[0] == 1
    dbcur.close()
    return exists

def get_table_info(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return [col[1] for col in columns]  # col[1] is column name

def create_opensky_table_from_csv(conn, csv_file, table_name):
    print(f"Creating table {table_name} from {csv_file}")
    'icao24','operatorIata','operatorIcao','owner','prevReg','regUntil','registered','registration','selCal','serialNumber','status','typecode','vdl'

    csv_columns = ["icao24",
                   "manufacturerName",
                   "model",
                   "operator",
                   "registration"
                   ]
    sql_columns = ["icao24",
                     "mfr",
                     "model",
                     "name",
                     "n_number"
                     ]

    columns = "icao24 TEXT, mfr TEXT, model TEXT, name TEXT, n_number TEXT"

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    print(create_table_sql)
    conn.execute(create_table_sql)

    create_index_sql = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_icao24 ON {table_name} (icao24)"
    conn.execute(create_index_sql)
    create_index_sql = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_model ON {table_name} (model)"
    conn.execute(create_index_sql)

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, quotechar="'")
        data = []
        for row in reader:
            output = []
            for column in csv_columns:
                if column == "icao24":
                    output.append(row[column].upper().rstrip())
                else:
                    output.append(row[column].rstrip())
            data.append(output)
        insert_sql = f"INSERT INTO {table_name} VALUES ({','.join(['?' for _ in sql_columns])})"
        conn.executemany(insert_sql, data)
        conn.commit()

                
# Connect to SQLite database
conn = sqlite3.connect("ledger.db")

# Example usage:
if not checkTableExists(conn, "opensky"):
    create_opensky_table_from_csv(conn, 'aircraft-database-complete-2025-02.csv', 'opensky')

# Print column names
if checkTableExists(conn, "opensky"):
    columns = get_table_info(conn, "opensky")
    print("OpenSky Table")
    print("Columns:", ", ".join(columns))

# Example query
cursor = conn.execute("SELECT * FROM opensky LIMIT 10")
for row in cursor:
    print(row)

conn.close()