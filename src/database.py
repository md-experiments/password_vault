import sqlite3

class SQLiteDB():
    '''
    Note assumes each line just contains one column: encrypted_text
    '''
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        
    def create_table(self, 
                     table_name, 
                     table_spec='encrypted_text TEXT'):
        cursor = self.connection.cursor()
        cursor.execute(f"CREATE TABLE {table_name} ({table_spec})")
        cursor.close()
        
    def select_all(self, table_name):
        cursor = self.connection.cursor()
        res=cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        res=[r[0] for r in res]
        cursor.close()  

        return res
    
    def add(self, table_name, data):
        cursor = self.connection.cursor()
        res=cursor.execute(f"INSERT INTO {table_name} VALUES ({data})")
        self.connection.commit()
        cursor.close()
        return res
    
    def update(self, table_name, data):
        pass

class FileDB():
    def __init__(self, file):
        self.file=file

    def save_to_file(self,msg):
        if isinstance(msg,list):
            msg='\n'.join(msg)

        with open(self.file,'w') as f:
            f.write(msg)

    def load_file(self):
        with open('file_to_encrypt.txt','r') as f:
            mylist = [line.rstrip('\n') for line in f] 
        return mylist