import mysql.connector
import json

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] config.json not found. Please create it.")
        return None
    except json.JSONDecodeError:
        print("[ERROR] config.json is not valid JSON. Please correct it.")
        return None

config = load_config()

if config is None:
    exit()

def create_connection():
    db_config = config['database']
    return mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        port=db_config['port']
    )

def create_levels_table():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                discord_id BIGINT PRIMARY KEY,
                xpt INT DEFAULT 0,
                ovxpt INT DEFAULT 0,
                tlevel INT DEFAULT 1,
                xpv INT DEFAULT 0,
                ovxpv INT DEFAULT 0,
                vlevel INT DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
        print("[INFO] Table 'levels' created or already exists.")
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error creating table: {err}")

create_levels_table()

def get_user_data(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM levels WHERE discord_id = %s", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result
        else:
            return {
                'discord_id': user_id,
                'xpt': 0,
                'ovxpt': 0,
                'tlevel': 1,
                'xpv': 0,
                'ovxpv': 0,
                'vlevel': 1
            }
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")
        return None

def update_user_data(user_id, xpt, ovxpt, tlevel, xpv, ovxpv, vlevel):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            REPLACE INTO levels (discord_id, xpt, ovxpt, tlevel, xpv, ovxpv, vlevel)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, xpt, ovxpt, tlevel, xpv, ovxpv, vlevel))
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")

def get_top_text_users(offset=0, limit=10):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM levels ORDER BY ovxpt DESC LIMIT %s OFFSET %s", (limit, offset))
        result = cursor.fetchall()
        conn.close()
        return result
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")
        return []

def get_top_voice_users(offset=0, limit=10):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM levels ORDER BY ovxpv DESC LIMIT %s OFFSET %s", (limit, offset))
        result = cursor.fetchall()
        conn.close()
        return result
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")
        return []
