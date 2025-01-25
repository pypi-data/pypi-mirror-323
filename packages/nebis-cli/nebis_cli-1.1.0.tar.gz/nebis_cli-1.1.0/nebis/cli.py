import requests
import getpass

API_URL = "https://nebisdb.pythonanywhere.com"  

def register_user():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    email = input("Enter your email: ")

    response = requests.post(f"{API_URL}/register", json={
        "username": username,
        "password": password,
        "email": email
    })

    if response.status_code == 201:
        print("Registration successful:", response.json()["message"])
    else:
        try:
            error_message = response.json().get("error", "Unknown error.")
            print("Error registering:", error_message)
        except ValueError:
            print("Error registering: invalid response from server.")

def login_user():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    response = requests.post(f"{API_URL}/login", json={
        "username": username,
        "password": password
    })

    if response.status_code == 200:
        print("Login successful.")
        user_menu(username)  
    else:
        try:
            error_message = response.json()   
            print("Error logging in:", error_message)
        except ValueError:  
            print("Error logging in: invalid response from server.")

def user_menu(username):
    while True:
        print("\n--- User Menu ---")
        print("1. View databases")
        print("2. Create new database")
        print("3. Delete database")
        print("4. Get Nebis connection URL")
        print("5. Logout")
        choice = input("Select an option: ")

        if choice == '1':
            get_user_databases(username)
        elif choice == '2':
            create_new_database(username)
        elif choice == '3':
            delete_database(username)
        elif choice == '4':
            database_name = input("Enter the name of the database to get the URL: ") + ".json"
            get_nebis_url(username, database_name)   
        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

def get_user_databases(username):
    response = requests.get(f"{API_URL}/get_user_databases", params={"username": username})

    if response.status_code == 200:
        databases = response.json().get("databases", [])
        if databases:
            print("Databases associated with your account:")
            for db in databases:
                print(f"- {db.replace('.json', '')}")  
        else:
            print("There are no databases associated with your account.")
    else:
        print("Error getting databases:", response.json())

def create_new_database(username):
    filename = input("Enter the name of the new database file: ") + ".json"
    response = requests.post(f"{API_URL}/add_database", json={
        "username": username,
        "filename": filename
    })

    if response.status_code == 201:
        print("Database created successfully:", response.json()["message"])
    else:
        try:
            error_message = response.json()  
        except ValueError: 
            error_message = response.text  
        print("Error creating the database:", error_message)

def delete_database(username):
    filename = input("Enter the name of the database to delete: ") + ".json"
    response = requests.delete(f"{API_URL}/delete_database", json={"username": username, "filename": filename})

    if response.status_code == 200:
        print("Database deleted successfully.")
    else:
        try:
            error_message = response.json()  
            print("Error deleting the database:", error_message)
        except ValueError:  
            print("Error deleting the database: invalid response from server.")
            print("Server response:", response.text) 

def connect_to_database(username, password, database_name):
    db_url = f"nebis://{username}:{password}@{API_URL}/{database_name}.json"
    response = requests.post(f"{API_URL}/connect", json={"db_url": db_url})

    try:
        response_data = response.json()
    except ValueError:
        response_data = None

    if response.status_code == 200:
        print("Connected to the database.")
        return True
    else:
        print("Error connecting to the database:", response_data or response.text)
        return False
    
def get_nebis_url(username, database_name):
    password = getpass.getpass("Enter your password to connect to the database: ")
    if not connect_to_database(username, password, database_name):
        print("Could not connect to the database. Make sure the database exists and the password is correct.")
        return

    response = requests.get(f"{API_URL}/get_nebis_url", params={"username": username, "database": database_name, "password": password})

    if response.status_code == 200:
        print("Your connection URL is:", response.json()["nebis_url"].replace('.json', ''))
    else:
        try:
            error_message = response.json()
            print("Error getting the URL:", error_message)
        except ValueError:
            print("Error getting the URL: invalid response from server.")
            print("Server response:", response.text)

def main():
    while True:
        print("\n--- Nebis CLI ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()