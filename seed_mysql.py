import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database credentials from .env
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

def run_seed_script():
    """Run the SQL seed script using the mysql command line tool"""
    script_path = os.path.join(os.path.dirname(__file__), 'seed_data.sql')
    
    if not os.path.exists(script_path):
        print(f"Error: Seed script not found at {script_path}")
        return False
    
    # Construct the mysql command
    mysql_cmd = [
        'mysql',
        f'--user={DB_USER}',
        f'--password={DB_PASSWORD}',
        f'--host={DB_HOST}',
        f'--port={DB_PORT}',
        DB_NAME,
        '-e',
        f'source {script_path}'
    ]
    
    print("Running seed script...")
    print(f"Command: mysql --user={DB_USER} --host={DB_HOST} --port={DB_PORT} {DB_NAME} -e 'source {script_path}'")
    
    try:
        # Run the command
        result = subprocess.run(mysql_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error running seed script: {result.stderr}")
            return False
        
        print("Seed script executed successfully!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        
        return True
    except Exception as e:
        print(f"Error running seed script: {e}")
        return False

if __name__ == "__main__":
    success = run_seed_script()
    sys.exit(0 if success else 1) 