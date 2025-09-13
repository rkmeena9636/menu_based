import streamlit as st
import Password
from Password import *
import pywhatkit
import smtplib
import subprocess
from openai import OpenAI
import tempfile
import tweepy
from datetime import datetime
import time
import pyautogui
import os
from instagrapi import Client
import pandas
from sklearn.linear_model import LinearRegression
from mysql.connector import Error
from Speak import speak
from googlesearch import search
import mysql.connector

def run_ssh_command(user, ip, command):
    full_cmd = f'ssh {user}@{ip} "{command}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

def linux_operations():
    st.subheader("🔧 Linux Remote Shell")
    user = st.text_input("Enter Username")
    ip = st.text_input("Enter Remote IP")
    if "linux_path" not in st.session_state:
        st.session_state.linux_path = "~"
    options = [
        "Know Current Directory","List Files & Directories","Change Directory","Create Directory",
        "Create File", "Edit File",
        "Read File", "Remove File", "Remove Directory"]
    Choose = st.selectbox("Choose Operation", options)
    extra_input = ""
    if Choose in ["Change Directory", "Create Directory", "Edit File", "Create File", "Remove File", "Read File", "Remove Directory"]:
        extra_input = st.text_input("Enter Name:")
    if st.button("Execute"):
        current_path = st.session_state.linux_path
        if Choose == "Know Current Directory":
            output = run_ssh_command(user, ip, f"cd {current_path} && pwd")
        elif Choose == "List Files & Directories":
            output = run_ssh_command(user, ip, f"cd {current_path} && ls")
        elif Choose == "Read File":
            output = run_ssh_command(user, ip, f"cat {current_path}/{extra_input}")
        elif Choose == "Change Directory":
            test = run_ssh_command(user, ip, f"cd {current_path}/{extra_input}")
            if "No such file" not in test:
                st.session_state.linux_path = f"{current_path}/{extra_input}".replace("//", "/")
                output = f"Changed to directory: {st.session_state.linux_path}"
            else:
                output = "Directory does not exist."
        elif Choose == "Create Directory":
            output = run_ssh_command(user, ip, f"cd {current_path} && mkdir {extra_input}")
        elif Choose == "Create File":
            output = run_ssh_command(user, ip, f"cd {current_path} && touch {extra_input}")
        elif Choose == "Remove File":
            output = run_ssh_command(user, ip, f"cd {current_path} && rm -f {extra_input}")
        elif Choose == "Remove Directory":
            output = run_ssh_command(user, ip, f"cd {current_path} && rmdir {extra_input}")
        elif Choose == "Edit File":
            output = "Use the Edit File section below to modify file content."
        st.text_area("📤 Command Output:", output, height=300)
    if Choose == "Edit File" and user and ip and extra_input:
        current_path = st.session_state.linux_path
        out = run_ssh_command(user, ip, f"cd {current_path} && cat {extra_input}")
        data = st.text_area("Edit File Content:", out, height=300, key="edit_area")
        if st.button("Save Changes to File"):
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                tmp.write(data)
                tmp_path = tmp.name
            scp_cmd = f"scp {tmp_path} {user}@{ip}:{current_path}/{extra_input}"
            result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ File updated successfully.")
            else:
                st.error(f"❌ Error while uploading: {result.stderr}")
            os.remove(tmp_path)

def docker_operations():
    st.subheader("🐳 Docker Control Panel")
    user = st.text_input("Enter Username")
    ip = st.text_input("Enter Remote IP")
    docker_options = [
        "Launch New Container", "Stop Container", "Remove Container", "Start Container",
        "See All Images", "List All Containers", "Pull Image from Docker Hub"]
    Choose = st.selectbox("Choose Docker Operation", docker_options)
    c1, c2 = st.columns(2)
    name = c1.text_input("Container/Image Name (if needed)")
    image = c2.text_input("Image Name (for launching container)")
    if st.button("Execute Docker Command"):
        if Choose == "Launch New Container":
            output = run_ssh_command(user, ip, f"docker run -dit --name {name} {image}")
        elif Choose == "Stop Container":
            output = run_ssh_command(user, ip, f"docker stop {name}")
        elif Choose == "Remove Container":
            output = run_ssh_command(user, ip, f"docker rm -f {name}")
        elif Choose == "Start Container":
            output = run_ssh_command(user, ip, f"docker start {name}")
        elif Choose == "See All Images":
            output = run_ssh_command(user, ip, "docker images")
        elif Choose == "List All Containers":
            output = run_ssh_command(user, ip, "docker ps -a")
        elif Choose == "Pull Image from Docker Hub":
            output = run_ssh_command(user, ip, f"docker pull {name}")
        else:
            output = "Invalid Choose"
        st.text_area("📤 Docker Output:", output, height=300)

def run_code_explainer():

    st.header("Code Explainer Using Gemini")

    KEY = "apikey"

    gemini_model = OpenAI(
        api_key=KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    code_input = st.text_area("Paste your code snippet here:", height=250)

    if st.button("Explain Code"):
        if code_input.strip() == "":
            st.warning("Please enter a code snippet to explain.")
        else:
            mymsg = [
                {"role": "system", "content": "Explain this code in 4-5 simple lines, specify the programming language, and detect if it’s AI-written or human-written."},
                {"role": "user", "content": code_input}
            ]

            response = gemini_model.chat.completions.create(
                messages=mymsg,
                model='gemini-2.5-flash'
            )

            explanation = response.choices[0].message.content

            st.success("Explanation generated successfully:")
            st.write(explanation)

def marks_model():
    st.subheader("Marks Predictor based on study Hours")
    data = pandas.read_csv("marks.csv")
    x = data["hrs"].values.reshape(-1, 1)
    y = data["marks"].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, y)
    hours = st.number_input(" Enter hours of study:")
    if hours <=10:
        if st.button(" Predict Marks"):
            prediction = model.predict([[hours]])
            st.success(f" Predicted Marks for {hours} hours:{prediction[0][0]}%")
    else:
        st.error("Hours mustreamlit be Less than or equal to 10")

def Bms():
    def create_connection():
        connection = None
        try:
            connection = mysql.connector.connect(host="localhost",user="root",password="Rahul@420",database="bms")  # Changed Sawan@420 → Rahul@420
        except Error as e:
            st.error(f"The error '{e}' occurred")
        return connection
    def get_users(connection):
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    def create_user(connection, name, email, balance):
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, balance) VALUES (%s, %s, %s)", (name, email, balance))
            connection.commit()
        except Error as e:
            st.error(f"Error creating user: {e}")
    def add_transaction(connection, user_id, type, amount):
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO transactions (user_id, type, amount) VALUES (%s, %s, %s)", (user_id, type, amount))
            connection.commit()
        except Error as e:
            st.error(f"Error adding transaction: {e}")
    def update_balance(connection, user_id, amount, is_deposit=True):
        cursor = connection.cursor()
        try:
            if is_deposit:
                cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, user_id))
            else:
                cursor.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, user_id))
            connection.commit()
        except Error as e:
            st.error(f"Error updating balance: {e}")
    def get_transactions(connection, user_id):
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        return cursor.fetchall()
    def Bms_main():
        st.title("Banking Management System")
        connection = create_connection()
        if connection is None:
            st.error("Failed to connect to the database. Please check the connection settings.")
            return
        menu = ["Create User", "View Users", "Deposit", "Withdraw", "View Transactions"]
        Choose = st.sidebar.selectbox("Menu", menu)
        if Choose == "Create User":
            st.subheader("Create New User")
            name = st.text_input("Name")
            email = st.text_input("Email")
            balance = st.number_input("Initial Balance", min_value=0.0)
            if st.button("Create"):
                create_user(connection, name, email, balance)
                msg=f"User {name} created successfully with balance {balance}"
                st.success(msg)
                speak(text="User Created Successfully")
        elif Choose == "View Users":
            st.subheader("View All Users")
            users = get_users(connection)
            for user in users:
                st.write(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}, Balance: {user['balance']}")
        elif Choose == "Deposit":
            st.subheader("Deposit Money")
            user_id = st.number_input("User ID", min_value=1)
            amount = st.number_input("Amount", min_value=0.01)
            if st.button("Deposit"):
                if amount <= 0:
                    speak(text="Amount should be greater than zero")
                    st.error("Amount should be greater than zero")
                else:
                    add_transaction(connection, user_id, 'deposit', amount)
                    update_balance(connection, user_id, amount, is_deposit=True)
                    msg= f"Deposited {amount} to user ID {user_id}"
                    st.success(msg)
                    speak(msg)
        elif Choose == "Withdraw":
            st.subheader("Withdraw Money")
            user_id = st.number_input("User ID", min_value=1)
            amount = st.number_input("Amount", min_value=0.01)
            if st.button("Withdraw"):
                if amount <= 0:
                    speak(text="Amount should be greater than zero")
                    st.error("Amount should be greater than zero")
                else:
                    cursor = connection.cursor()
                    cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
                    user_balance = cursor.fetchone()
                    if user_balance[0] >= amount:
                        add_transaction(connection, user_id, 'withdrawal', amount)
                        update_balance(connection, user_id, amount, is_deposit=False)
                        st.success(f"Withdrew {amount} from user ID {user_id}")
                        speak(text=f"Withdrew {amount} from user ID {user_id}")
                    else:
                        speak("Insufficient balance or user not found")
                        st.error("Insufficient balance or user not found")
        elif Choose == "View Transactions":
            st.subheader("View User Transactions")
            user_id = st.number_input("User ID", min_value=1)
            if st.button("View Transactions"):
                transactions = get_transactions(connection, user_id)
                if transactions:
                    for transaction in transactions:
                        st.write(f"ID: {transaction['id']}, Type: {transaction['type']}, Amount: {transaction['amount']}, Date: {transaction['created_at']}")
                else:
                    speak("No transactions found for this user.")
                    st.write("No transactions found for this user.")
        connection.close()
    Bms_main()

# WhatsApp function
def whatsapp():
    st.subheader("WhatsApp Message Sender")
    phone = st.text_input("Enter phone number (with country code):")
    message = st.text_area("Enter message:")
    hour = st.number_input("Hour (24-hour format):", min_value=0, max_value=23)
    minute = st.number_input("Minute:", min_value=0, max_value=59)
    
    if st.button("Schedule WhatsApp Message"):
        try:
            pywhatkit.sendwhatmsg(phone, message, hour, minute)
            st.success("WhatsApp message scheduled successfully!")
            speak("WhatsApp message scheduled successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# Twilio WhatsApp function
def Twilio_whatsapp():
    st.subheader("WhatsApp Message via Twilio")
    st.info("This feature requires Twilio setup. Please configure your Twilio credentials in Password.py")
    phone = st.text_input("Enter phone number (with country code):")
    message = st.text_area("Enter message:")
    
    if st.button("Send WhatsApp Message"):
        st.warning("Twilio WhatsApp integration not implemented yet. Please use regular WhatsApp option.")

# Email function
def send_email():
    st.subheader("Email Sender")
    to_email = st.text_input("To Email:")
    subject = st.text_input("Subject:")
    body = st.text_area("Message Body:")
    
    if st.button("Send Email"):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL_ADDRESS, to_email, message)
            server.quit()
            st.success("Email sent successfully!")
            speak("Email sent successfully!")
        except Exception as e:
            st.error(f"Error sending email: {e}")

# Instagram function
def instagram():
    st.subheader("Instagram Post")
    st.info("This feature requires Instagram API setup. Please configure your Instagram credentials in Password.py")
    caption = st.text_area("Post Caption:")
    image_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
    
    if st.button("Post to Instagram"):
        st.warning("Instagram posting not implemented yet. Please configure Instagram API.")

# Twitter function
def Twitter():
    st.subheader("Twitter Post")
    st.info("This feature requires Twitter API setup. Please configure your Twitter credentials in Password.py")
    tweet = st.text_area("Tweet Content:")
    
    if st.button("Post Tweet"):
        st.warning("Twitter posting not implemented yet. Please configure Twitter API.")

# LinkedIn function
def linkedin():
    st.subheader("LinkedIn Post")
    st.info("This feature requires LinkedIn API setup. Please configure your LinkedIn credentials in Password.py")
    content = st.text_area("Post Content:")
    
    if st.button("Post to LinkedIn"):
        st.warning("LinkedIn posting not implemented yet. Please configure LinkedIn API.")

# Phone call function
def call():
    st.subheader("Phone Call via Twilio")
    st.info("This feature requires Twilio setup. Please configure your Twilio credentials in Password.py")
    phone = st.text_input("Enter phone number (with country code):")
    message = st.text_area("Message to speak:")
    
    if st.button("Make Call"):
        st.warning("Phone calling not implemented yet. Please configure Twilio API.")

# SMS function
def message():
    st.subheader("SMS via Twilio")
    st.info("This feature requires Twilio setup. Please configure your Twilio credentials in Password.py")
    phone = st.text_input("Enter phone number (with country code):")
    message = st.text_area("SMS Message:")
    
    if st.button("Send SMS"):
        st.warning("SMS sending not implemented yet. Please configure Twilio API.")

# Google Search function
def run_google_search_app():
    st.subheader("Google Search")
    query = st.text_input("Enter search query:")
    num_results = st.number_input("Number of results:", min_value=1, max_value=10, value=5)
    
    if st.button("Search"):
        try:
            results = list(search(query, num_results=num_results))
            st.success(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                st.write(f"{i}. {result}")
        except Exception as e:
            st.error(f"Search error: {e}")

def Python_projects():
    st.subheader("Python Projects")
    st.write("This section will contain various Python projects.")

    ch = ["Whatsapp Message",
        "Whatsapp Msg (without Reveal Your No.)",
        "Email",
        "Instagram Post",
        "Twitter Post",
        "Linkedin Post",
        "Phone Call (without Reveal Your No.)",
        "message (without Reveal Your No.)",
        "Bank Management System","Google Search"]
    
    Choose = st.selectbox("Choose Any One",ch)
    if st.button("Execute"):
        if Choose == "Whatsapp Message":
            whatsapp()
        elif Choose == "Whatsapp Msg (without Reveal Your No.)":
            Twilio_whatsapp()
        elif Choose == "Email":
            send_email()
        elif Choose == "Instagram Post":
            instagram()
        elif Choose == "Twitter Post":
            Twitter()
        elif Choose == "Linkedin Post":
            linkedin()
        elif Choose == "Phone Call (without Reveal Your No.)":
            call()
        elif Choose == "message (without Reveal Your No.)":
            message()
        elif Choose == "Bank Management System":
            Bms()
        elif Choose == "Google Search":
            run_google_search_app()
    

st.set_page_config(page_title="Menu-Based Remote Ops", layout="centered")

def main_menu():
    st.title("LinuxWorld Informatics Pvt. Ltd.")
    st.title("Welcome To RAHUL's World")  # Updated name here
    st.title("Menu Based Project")

    menu = st.sidebar.radio(
        "Select Module",
        [
            "Python Projects",
            "AI Models",
            "Machine Learning",
            "Linux Shell",
            "Docker Manager",
            "CODE EXPLAINER",
            "Marks Predictor",
            "Bank Management System"
        ]
    )

    if menu == "Linux Shell":
        linux_operations()
    elif menu == "Python Projects":
        Python_projects()
    elif menu == "Docker Manager":
        docker_operations()
    elif menu == "CODE EXPLAINER":
        run_code_explainer()
    elif menu == "Marks Predictor":
        marks_model()
    elif menu == "Bank Management System":
        Bms()

main_menu()
