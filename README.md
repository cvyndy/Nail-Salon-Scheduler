# Project1

This project is build and ran with WSL which allows me to run commands with the use of linux on Windows.

### How to set up Virtual Environment and install python libraries.

### Simple Project Summary
A website for a nail salon that lets customers book appointments online, sign in/manage their bookings, and view/leave reviews. It should also give the salon owner simple admin tools to see and manage the schedule and photos.

### How to run Flask 

To compile this code first clone the repository:
```
git clone https://github.com/cvyndy/Project1
```
Create a virtual environment to download flask
```
python -m venv venv
```
Activate the virtual environment
```
source venv/bin/activate
```
Download requirements.txt
```
pip install -r requirements.txt
```
### How to create PostgresSQL DB and run Flask
To create a PostgreSQL Database:
```
sudo -u postgres psql
```
This creates the database locally
```
CREATE DATABASE flask_db;
CREATE USER username WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE flask_db TO username;
```
Also, make an .env file to hide your credentials
```
DATABASE_URL = postgresql://username:password@localhost/flask_db
```
After you setup your database, run the app in the root directory
```
flask --app server.app run
```
OR run the app by going into the server directory and running it there
```
cd server
flask run
```
At [http://localhost:5000/test-db](http://localhost:5000/test-db), the database will show you if the connection is successful or not.

### How to run Python Black (a linting tool to automatically format your python code)
First install black with
```
pip install black
```
To run black on a specific file in a specific file(I used app.py), cd into the directory
```
python -m black insert_file
```
OR to run black on every python file in the main directory run
```
python -m black . --check --verbose
```
### How the Black Lint Check Pipeline works
This pipeline uses GitHub Actions with Python Black to make sure all Python files are formatted correctly. This pipeline runs on every push and pull request.
The workflow file is located at
```
.github/workflows/black.yml
```
If there is an error, fix formating locally through
```
python -m black .
```
### How I created the React App
I noticed that Next.js requires Node version 20 or higher, but I first installed nvm and updated Node. 

Install nvm and reload the terminal
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
```
Install Node 20
```
nvm install 20
nvm use 20
nvm alias default 20
```
Create the React app inside the client folder using Next.js
```
npx create-next-app@latest client
```
Go into the client directory and install the dependencies 
```
npm install
```
Run the app
```
npm run dev
```
 ### Database Schema

![Database Schema](db_schema.png)
 