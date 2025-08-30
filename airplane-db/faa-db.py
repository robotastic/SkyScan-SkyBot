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

def create_photos_table(conn):
    print("Creating Photos table")
    create_table_sql = """
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icao24 TEXT,
    timestamp INTEGER,
    image_path TEXT,
    thumb_path TEXT,
    n_number TEXT,
    year_mfr INTEGER,
    type_registrant TEXT,
    name TEXT,
    type_aircraft TEXT,
    mfr TEXT,
    model TEXT,
    num_eng INTEGER,
    num_seats INTEGER,
    weight TEXT,
    speed INTEGER
)
"""
    conn.execute(create_table_sql)
    create_table_sql = create_table_sql + """
CREATE INDEX IF NOT EXISTS idx_photos_icao24 ON photos (icao24)
CREATE INDEX IF NOT EXISTS idx_photos_timestamp ON photos (timestamp)
CREATE INDEX IF NOT EXISTS idx_photos_model ON photos (model)
"""
    with open('photos.sql', 'w') as f:
        f.write(create_table_sql)

def create_model_table_from_csv(conn, csv_file, table_name):
    print(f"Creating table {table_name} from {csv_file}")
    csv_columns = ["CODE",
                   "MFR",
                   "MODEL",
                   "NO-ENG",
                   "NO-SEATS",
                   "AC-WEIGHT",
                   "SPEED"
                   ]
    sql_columns = ["code",
                     "mfr",
                     "model",
                     "num_eng",
                     "num_seats",
                     "weight",
                     "speed"
                     ]

    columns = "code TEXT, mfr TEXT, model TEXT, num_eng INTEGER, num_seats INTEGER, weight INTEGER, speed INTEGER"

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    print(create_table_sql)
    conn.execute(create_table_sql)

    create_index_sql = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_code ON {table_name} (code)"
    conn.execute(create_index_sql)

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            data.append([row[header].rstrip() for header in csv_columns])
        insert_sql = f"INSERT INTO {table_name} VALUES ({','.join(['?' for _ in sql_columns])})"
        conn.executemany(insert_sql, data)
        conn.commit()

                   

def create_aircraft_table_from_csv(conn, csv_file, table_name):
    print(f"Creating Aircraft table {table_name} from {csv_file}")
    sql_columns = ["n_number",
                   "mfr_mdl_code",
                   "year_mfr",
                   "type_registrant",
                   "name",
                   "type_aircraft",
                   "icao24"
                   ]
    csv_columns = ["n-number",
                   "mfr mdl code",
                    "year mfr",
                    "type registrant",
                    "name",
                    "type aircraft",
                    "mode s code hex"]
    columns = [f"{header} TEXT" for header in sql_columns]
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join(columns)})"
    print(create_table_sql)
    conn.execute(create_table_sql)
    create_index_sql = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_icao24 ON {table_name} (icao24)"
    conn.execute(create_index_sql)

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            data.append([row[header.upper()].rstrip() for header in csv_columns])
        insert_sql = f"INSERT INTO {table_name} VALUES ({','.join(['?' for _ in sql_columns])})"
        conn.executemany(insert_sql, data)
        conn.commit()

# Connect to SQLite database
conn = sqlite3.connect("ledger.db")

# Example usage:
if not checkTableExists(conn, "aircraft"):
    create_aircraft_table_from_csv(conn, 'ReleasableAircraft/MASTER.txt', 'aircraft')

if not checkTableExists(conn, "model"):
    create_model_table_from_csv(conn, 'ReleasableAircraft/ACFTREF.txt', 'model')

if not checkTableExists(conn, "photos"):
    create_photos_table(conn)


# Print column names
if checkTableExists(conn, "aircraft"):
    columns = get_table_info(conn, "aircraft")
    print("Aircraft Table")
    print("Columns:", ", ".join(columns))

if checkTableExists(conn, "model"):
    columns = get_table_info(conn, "model")
    print("Model Table")
    print("Columns:", ", ".join(columns))

if checkTableExists(conn, "photos"):
    columns = get_table_info(conn, "photos")
    print("Photos Table")
    print("Columns:", ", ".join(columns))

# Example query
cursor = conn.execute("SELECT * FROM aircraft JOIN model ON aircraft.mfr_mdl_code = model.code LIMIT 10")
for row in cursor:
    print(row)



conn.close()