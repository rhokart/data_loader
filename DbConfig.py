import psycopg2

def db_conn():
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        host="database-1.ct0gsawqmj6m.ap-south-1.rds.amazonaws.com",
        password="Q5GfD6iyf3AO3d7PptY4",
        port=5432
    )


class DbConfig:
    def __init__(self):
        pass