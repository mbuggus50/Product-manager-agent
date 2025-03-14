class DatabaseTool:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_table(self, table_name, columns):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(f"CREATE TABLE {table_name} ({columns})")
        conn.commit()
        conn.close()

    def insert_data(self, table_name, data):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(f"INSERT INTO {table_name} VALUES ({data})")
        conn.commit()
        conn.close()

    def select_data(self, table_name, columns):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(f"SELECT {columns} FROM {table_name}")
        return c.fetchall()

    def delete_table(self, table_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(f"DROP TABLE {table_name}")
        conn.commit()
        conn.close()