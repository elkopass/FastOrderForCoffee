def sql_connection():
 
    try:
 
        con = sqlite3.connect('mydatabase.db')
 
        return con
 
    except Error:
 
        print(Error)
 
def sql_user(con):
 
    cursorObj = con.cursor()
 
    cursorObj.execute("CREATE TABLE users(id integer PRIMARY KEY, idUser text)")
 
    con.commit()
 
def sql_order(con):
    cursorObj = con.cursor()
 
    cursorObj.execute("CREATE TABLE orders(id integer PRIMARY KEY, idUser text, status text,time text,FOREIGN KEY (idUser) REFERENCES users(id))")
 
    con.commit()

