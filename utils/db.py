import psycopg2

def get_connection():
    """
    Returns a psycopg2 connection object
    """
    return psycopg2.connect(
        database="postgres",
        user="postgres",
        host="localhost",
        password="postgres"
    )
    