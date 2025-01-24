import sqlite3
import os
#from importlib import resources


__db=""

def setDBName(path: str):
    global __db
    print("Setting DB to: " + path)
    __db = path
    #with resources.path('sql_testing_tools', path) as db_path:
    #    __db = str(db_path)
    #    print(__db)


#setDBName("databases/bayern.db")

def run(sql: str):
    con = sqlite3.connect(__db)
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    return cur

def runFromFile(path: str):
    sql = getSQLFromFile(path)
    if not sql:
        raise Exception("\nSQL-Datei ist leer. Aufgabe wurde noch nicht bearbeitet.")


    if sql.lower().find("drop") != -1:
        raise Exception("Guter Versuch, aber die Datenbank wird bei jedem Upload zurückgesetzt ;)")

    try:
        res = run(sql)
    except Exception as e:
        raise Exception(f"\n\nSyntax-Fehler in der SQL-Abfrage:\n{str(e)}")

    headers = [h[0] for h in res.description] if res.description else []
    rows = res.fetchall() if res else []

    return headers, rows


def runAndGetStringTable_fromFile(path: str, count: int = 5, maxLineLength: int = 85):
    try:
        headers, rows = runFromFile(path)
        resultCount = len(rows)
        rows = rows[:count]
        s = ""

        matrix = [] #[[]*(len(rows)+1)]*len(headers)

        for col in range(len(headers)):
            matrix.append([])
            matrix[-1].append(headers[col])

        if rows is not None:
            for col in range(len(matrix)):
                for row in range(0, len(rows)):
                    if len(rows[row]) > col:
                        matrix[col].append(rows[row][col])

            for col in range(len(matrix)):
                maxLength = max([len(str(x)) for x in matrix[col]])

                for row in range(0, len(matrix[col])):
                    matrix[col][row] = str(matrix[col][row]).ljust(maxLength)

            normalizedRows = []
            spacing = "  "
            spacingLength = len(spacing) * (len(matrix[0]) - 1)

            lineLength = sum([len(x[0]) for x in matrix]) + spacingLength
            
            

            if lineLength > maxLineLength:
                valLength = lineLength - spacingLength
                maxColLength = int(maxLineLength/len(matrix))

                for col in range(len(matrix)):
                    for row in range(0, len(matrix[col])):
                        cutContent = len(matrix[col][row].strip()) > maxColLength
                        if cutContent:
                            matrix[col][row] = matrix[col][row][:maxColLength-2] + ".."
                        else:
                            matrix[col][row] = matrix[col][row][:maxColLength]


            for row in range(min(count+1, len(matrix[0]))):
                normalizedRows.append(spacing.join([str(matrix[col][row]) for col in range(len(matrix))]))
            normalizedRows.insert(1, len(normalizedRows[0])*"-")

            s = "\n".join(normalizedRows[:count+2])
            s += "\n" + normalizedRows[1]

            if (resultCount > count):
                s += "\n... " + str(resultCount - count) + " weitere Zeilen"
            else:
                s += "\n... keine weiteren Zeilen"

        #longestLineInS = 85 # max([len(x.replace("\t", "    ")) for x in s.split("\n")])

        #s = "-" * longestLineInS + "\n" + s + "\n" + "-" * longestLineInS
        s = "\n\nDiese Meldung sagt nichts über die Korrektheit der Abgabe aus!\nDie ersten " + str(
            count) + " Zeilen des Ergebnisses der SQL-Abfrage:\n\n" + s

        return s.replace("None", "NULL")
    except Exception as ex:
        raise ex

def getSQLFromFile(path: str):
    try:
        with open(path, "r") as f:
            s = f.read()
            if not s:
                raise Exception("\nSQL-Datei ist leer. Aufgabe wurde noch nicht bearbeitet.")
            return s
    except FileNotFoundError:
        raise Exception(f"\nSQL-Datei nicht gefunden! Überprüfe, dass der Name korrekt ist ({path.split('/')[-1]}) und die Datei nicht gelöscht oder in einen Unterordner verschoben wurde.")



def getWorkingDir():
    return os.getcwd()


def getWorkingDirFiles():
    return os.listdir()

def mapDatabaseTypes(t):
    # Map SQLite types to Python types
    type_mapping = {
        "INTEGER": "int",
        "TEXT": "str",
        "VARCHAR": "str",
        "REAL": "float",
        "BLOB": "bytes",
        "NUMERIC": "float",
        "DOUBLE": "float"
    }
    t = t.upper()
    t = type_mapping.get(t, t)

    if "INT" in t:
        t = "int"
    elif "VARCHAR" in t:
        t = "str"
    elif "CHAR" in t:
        t = "str"

    return t




def getTableDict():
    res = run("SELECT name FROM sqlite_master WHERE type='table';")
    tables = res.fetchall()

    table_dict = {}
    for table in tables:
        res = run(f"PRAGMA table_info({table[0]})")
        r = res.fetchall()
        if table[0] == "sqlite_sequence":
            continue
        table_dict[table[0]] = [[c[1], mapDatabaseTypes(c[2])] for c in r]

    return table_dict