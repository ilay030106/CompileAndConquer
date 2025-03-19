import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool

# Updated configuration with the MySQL schema name "compile_and_conquer"
config = {
    'user': 'root',
    'password': '1234',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'compile_and_conquer'
}

def initialize_database():
    """
    Creates the schema and tables if they don't exist,
    then initializes a connection pool for background DB operations.
    """
    try:
        # Connect without specifying a database to create the schema with MySQL dialect options.
        cnx = mysql.connector.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        cursor = cnx.cursor()
        # Create schema with explicit charset and collation
        cursor.execute(
            "CREATE SCHEMA IF NOT EXISTS compile_and_conquer DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print("Schema 'compile_and_conquer' checked/created.")
        cursor.close()
        cnx.close()

        # Create a connection pool that uses the 'compile_and_conquer' schema.
        pool = MySQLConnectionPool(pool_name="mypool", pool_size=5, **config)
        cnx = pool.get_connection()
        cursor = cnx.cursor()

        # Create the users table with MySQL specific table options.
        users_table_definition = """
            CREATE TABLE IF NOT EXISTS users (
                id INT NOT NULL AUTO_INCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                age INT NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                email VARCHAR(50) NOT NULL,
                password VARCHAR(50) NOT NULL,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(users_table_definition)
        print("Table 'users' checked/created in schema 'compile_and_conquer'.")

        # Create the game_history table with a primary key and a foreign key to users.id.
        game_history_table_definition = """
            CREATE TABLE IF NOT EXISTS game_history (
                history_id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                time TIME NOT NULL,
                date DATE NOT NULL,
                money_spent INT NOT NULL,
                lives_amount INT NOT NULL,
                difficulty VARCHAR(20) NOT NULL,
                PRIMARY KEY (history_id),
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(game_history_table_definition)
        print("Table 'game_history' checked/created in schema 'compile_and_conquer'.")

        cnx.commit()
        cursor.close()
        cnx.close()

        return pool
    except Error as err:
        print(f"Error initializing database: {err}")
        return None

# Initialize the database and create a connection pool at module load.
db_pool = initialize_database()

def get_db_connection():
    """
    Returns a connection from the pool. This function can be imported
    and used by other files to fetch or write to the database.
    """
    if db_pool is not None:
        try:
            return db_pool.get_connection()
        except Error as err:
            print(f"Error getting database connection: {err}")
            return None
    else:
        print("Database pool not initialized.")
        return None

def close_database():
    """
    Closes all idle connections in the connection pool.
    Note: This only closes connections that are not currently in use.
    It's recommended to close any active connections before calling this method.
    """
    if db_pool is not None:
        try:
            # db_pool uses an internal queue (_cnx_queue) to store idle connections.
            while not db_pool._cnx_queue.empty():
                cnx = db_pool._cnx_queue.get()
                try:
                    cnx.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")
            print("All idle database connections have been closed.")
        except Exception as err:
            print(f"Error closing database pool: {err}")
    else:
        print("Database pool is not initialized or already closed.")