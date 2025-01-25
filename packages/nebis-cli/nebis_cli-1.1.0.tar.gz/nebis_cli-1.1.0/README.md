# Nebis CLI

Nebis CLI is a command line tool for managing databases on the Nebis platform. It allows users to register, login, and perform operations such as creating, deleting, and getting database connection URLs.

## Features

- User registration.
- Secure login with hidden password.
- Database management (create, list, and delete).
- Getting the connection URL in a secure format.

## Requirements

- Python 3.6 or higher.
- Required modules:
- `requests`
- `getpass`

You can install the required modules with:

```bash
pip install requests
```

## Installation

1. Clone this repository:

```bash
git clone https://github.com/nebis-db/nebis-cli.git
```

2. Go to the project directory:

```bash
cd nebis-cli
```

3. Run the main script:

```bash
python cli.py
```

## Usage

Running the script will display an interactive menu:

```bash
--- Nebis CLI ---
1. Register
2. Login
3. Exit
Select an option:
```

### User Registration

Select option `1` and enter the required information:

```
Enter your username: johndoe
Enter your password: ********
Enter your email: johndoe@example.com
```

### Login

Select option `2` and enter your credentials (It is important to confirm your account, otherwise you will not be able to log in no matter how many times you try):

```
Enter your username: johndoe
Enter your password: ********
```

### User Menu

After logging in, you will be able to perform the following actions:

1. View associated databases.
2. Create a new database.
3. Delete a database.
4. Get the Nebis URI.
5. Log out.

### Get the connection URL

To get the connection URL for a database, select the corresponding option and enter the password. The URL provided will be in the format:

```bash
nebis://username:password@nebisdb.pythonanywhere.com/database_name
```

## Contribution

If you would like to contribute to Nebis CLI, please follow these steps:

1. Fork the repository.
2. Create a new branch with your changes.
3. Submit a pull request for review.