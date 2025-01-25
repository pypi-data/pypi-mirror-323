""" Support files called by the entry file.
Last updated by Jasper Sheeds 1/21/25 """

from dotenv import find_dotenv, set_key
import tkinter
from tkinter import filedialog
import os
from email.message import EmailMessage
import smtplib
global error_log_file
error_log_file = []

def find_file_loc():
    """ Calls a dialog window to select an exe file. Then calls function to change env file. """
    tkinter.Tk().withdraw()
    folder_path = filedialog.askopenfile(initialdir="C:\\Program Files (x86)", title="Select SL-Dog File",
                                         filetypes=[("exe files", "*.exe")])
    set_file_loc(folder_path.name)

def set_file_loc(loc):
    """ Sets location in .env file. """
    os.environ["sl_dog_path"] = loc
    dotenv_path = find_dotenv()
    set_key(dotenv_path, "sl_dog_path", os.environ["sl_dog_path"])

def email_send(message):
    """ Uses the port number for outlook to send an email with a given message. """
    port = 587
    email_from = os.getenv('email')
    email_pass = os.getenv('email_password')

    email = EmailMessage()
    email["From"] = email_from
    email["To"] = email_from
    email["Subject"] = "Error Email SLDOG"
    email.set_content(message)

    smtp = smtplib.SMTP("smtp-mail.outlook.com", port)
    smtp.starttls()
    smtp.login(email_from, email_pass)
    smtp.sendmail(email_from, email_from, email.as_string())
    smtp.quit()

def error_log(error):
    """ Writes error to list. """
    error_log_file.append(error)

def get_errors():
    """ Returns errors in list. """
    return error_log_file