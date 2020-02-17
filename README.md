# Bank Marketing Application

### Software Requirements:
    • Ubuntu 18.0.4 LTS
    • python 3.6
    • python3-venv
    • pip3

### Installation Instructions
1. Download the zipped project files.
2. Unzip the project files.
3. Open a command line instance and navigate to the root directory of the unzipped project files.
4. Create the virtual environment: ```python3 -m venv env```
5. Activate the virtual environment: ```source env/bin/activate```
6. Install requirements: ```pip3 install -r requirements.txt```
7. Create the database: ```flask db init```
8. Run database migrations: ```flask db upgrade```
9. Load DB seeds: ```flask seed run```
10. Run the app: ```flask run```
11. In your web browser, navigate to URL http://127.0.0.1:5000/
12. Log in using the following credentials:
    * Username: test
    * Password: test

### References
Jacob, S. (2018, August 29). Bank_Loan_modelling. Retrieved February 5, 2020, from https://www.kaggle.com/itsmesunil/bank-loan-modelling