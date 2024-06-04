if __name__== '__main__':

    import sqlite3 
    from sqlite3 import Error 
    import pandas as pd

    # чистка данных в Pandas

    df_1 = pd.read_csv('data/employess_dict.txt')
    # не сделано

    df_2 = pd.read_csv('data/salary.csv', delimiter=';')
    df_2 = df_2.drop_duplicates()
    df_2 = df_2.drop(1, axis='index').reset_index()
    df_2 = df_2.drop(columns=['index', 'Unnamed: 4'], axis=1)
    df_2['DATE'] = pd.to_datetime(df_2['DATE'])
    df_2['ID'] = df_2['ID'].astype(int)
    df_2['VALUE'] = df_2['VALUE'].astype(int)

    df_3 = pd.read_parquet('data/emails.gzip', engine='pyarrow')
    df_3 = df_3.drop(columns=['ID'], axis=1)
    df_3 = df_3.drop_duplicates()
    df_3['PERSON_ID'] = df_3['PERSON_ID'].astype(int)

    # подключение к базе
    def create_connection(path):
    
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection successful to DB")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    db = 'dar_bd.db'
    connection = create_connection(db)

    # запрос к базе execute

    def execute_query(connection, query):

        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            print("The execute query is successful")
        except Error as e:
            print(f"The error '{e}' occurred")

    # ф-я выполнения скрипта и вывода результата

    def sql_fetch(con, sql_script):
        cur = con.cursor()
        cur.execute(sql_script)
        rows = cur.fetchall()
        for row in rows:
            print(row)

    # создание и заполнение таблицы employee

    create_table = f"""
    CREATE TABLE IF NOT EXISTS (employee) (
    empl_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name1 STRING,
    name2 STRING,
    name3 STRING
    );
    """

    execute_query(connection, create_table)
    df_1.to_sql('employee', connection, if_exists='replace', index=False)

    # создание и заполнение таблицы salary

    create_table = f"""
CREATE TABLE IF NOT EXISTS salary (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dt DATETIME,
  salary_type STRING,
  amount DOUBLE
);
"""

    execute_query(connection, create_table)
    df_2.to_sql('salary', connection, if_exists='replace', index=False)

    # создание и заполнение таблицы email

    create_table = f"""
    CREATE TABLE IF NOT EXISTS email (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER,
    email STRING
    );
    """

    execute_query(connection, create_table)
    df_3.to_sql('email', connection, if_exists='replace', index=False)

    # создание и печать отчета

    sql_fetch(connection, "select e.empl_id as Empl_ID, \
                CONCAT (e.name1, ' ', e.name2, ' ', e.name3) as FIO, \
                avg(VALUE) FILTER (WHERE type = 'salary') as Salary, \
                avg(VALUE) FILTER (WHERE type = 'bonus') as Bonus,  \
                em.email as Email\
                from employee e left join salary s on e.empl_ID =  s.id \
                left join email em on em.person_id = e.empl_id \
            ;")

    connection.close()
