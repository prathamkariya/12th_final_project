import tkinter as tk
from tkinter import messagebox
import mysql.connector
from PIL import Image, ImageTk
import bcrypt


# Employee credentials
employee_id = {
    "username": "emp_007",
    "password": bcrypt.hashpw(b"007", bcrypt.gensalt())
}

# Database Connection
def create_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='12345',
            database='bank_management'
        )
        return connection
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Connection failed: {e}")
        return None


# Employee Login 
def employee_login(username, password):
    """Handle employee login."""
    if username == employee_id["username"] and bcrypt.checkpw(password.encode('utf-8'), employee_id["password"]):
        messagebox.showinfo("Login Successful", f"Welcome to DT Bank, {username}!")
        return True
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password. Please try again.")
        return False

# Customer Account Management Functions

#1.Create Customer
def create_customer(account_number, name, dob, phone, email, aadhar_number, address, account_type, initial_balance):
    """Create a new customer account in the database."""
    try:
        initial_balance = float(initial_balance)
        if initial_balance < 0:
            raise ValueError("Initial balance must be a non-negative number.")
        
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
        return

    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO customers (account_number, name, date_of_birth, phone_number, email, aadhar_number, address, account_type, balance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (account_number, name, dob, phone, email, aadhar_number, address, account_type, initial_balance))
        connection.commit()
        messagebox.showinfo("Success", "Customer created successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

#View Customer
def view_customer(account_number):
    """View customer details based on account number."""
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    query = "SELECT * FROM customers WHERE account_number = %s"
    
    try:
        cursor.execute(query, (account_number,))
        customer = cursor.fetchone()

        if customer:
            details = (f"Account Number: {customer[0]}\n"
                       f"Name: {customer[1]}\n"
                       f"DOB: {customer[2]}\n"
                       f"Phone: {customer[3]}\n"
                       f"Email: {customer[4]}\n"
                       f"Aadhar: {customer[5]}\n"
                       f"Address: {customer[6]}\n"
                       f"Account Type: {customer[7]}\n"
                       f"Balance: ₹{customer[8]:,.2f}")
            messagebox.showinfo("Customer Details", details)
        else:
            messagebox.showerror("Error", "Customer not found.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

#Update Customer
def update_customer(account_number, field, new_value):
    """Update customer information in the database."""
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()

    if field not in ['name', 'phone_number', 'email', 'aadhar_number', 'address', 'account_type']:
        messagebox.showerror("Error", "Invalid field for update.")
        cursor.close()
        connection.close()
        return
        
        messagebox.showerror("Input Error", "Invalid email format.")
        cursor.close()
        connection.close()
        return

    query = f"UPDATE customers SET {field} = %s WHERE account_number = %s"
    cursor.execute(query, (new_value, account_number))
    connection.commit()

    if cursor.rowcount > 0:
        messagebox.showinfo("Success", f"Updated {field} successfully!")
    else:
        messagebox.showerror("Error", "Failed to update customer details.")

    cursor.close()
    connection.close()

#Delete Customer
def delete_customer(account_number):
    """Delete a customer from the database."""
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    query = "DELETE FROM customers WHERE account_number = %s"
    cursor.execute(query, (account_number,))
    connection.commit()

    if cursor.rowcount > 0:
        messagebox.showinfo("Success", "Customer deleted successfully!")
    else:
        messagebox.showerror("Error", "Customer not found.")

    cursor.close()
    connection.close()

#Perform Transactions
def perform_transaction(account_number, amount, transaction_type):
    """Perform a deposit or withdrawal transaction."""
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()

    try:
        amount = float(amount)
        if amount <= 0:
            messagebox.showerror("Input Error", "Amount must be a positive number.")
            return

        if transaction_type == 'Deposit':
            update_query = "UPDATE customers SET balance = balance + %s WHERE account_number = %s"
            cursor.execute(update_query, (amount, account_number))
        elif transaction_type == 'Withdrawal':
            cursor.execute("SELECT balance FROM customers WHERE account_number = %s", (account_number,))
            balance = cursor.fetchone()
            if balance is None:
                messagebox.showerror("Error", "Account not found.")
                return
            if balance[0] < amount:
                messagebox.showerror("Error", "Insufficient funds.")
                return
            update_query = "UPDATE customers SET balance = balance - %s WHERE account_number = %s"
            cursor.execute(update_query, (amount, account_number))
        else:
            messagebox.showerror("Error", "Invalid transaction type.")
            return

        connection.commit()
        messagebox.showinfo("Success", f"{transaction_type} of ₹{amount:,.2f} completed successfully!")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for the amount.")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Transaction failed: {err}")
    finally:
        cursor.close()
        connection.close()

#Check Balance
def check_balance(account_number):
    """Check the balance of a customer account."""
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    query = "SELECT name, balance FROM customers WHERE account_number = %s"
    cursor.execute(query, (account_number,))
    result = cursor.fetchone()

    if result:
        name, balance = result
        messagebox.showinfo("Balance Inquiry", f"Account Holder: {name}\nCurrent Balance: ₹{balance:,.2f}")
    else:
        messagebox.showerror("Error", "Account not found.")

    cursor.close()
    connection.close()

# GUI Functions

#1.Window for Create Customer Account

def create_customer_account():
    create_window = tk.Toplevel()
    create_window.title("Create Customer Account")
    create_window.geometry("500x700")  
    create_window.configure(bg="#E0F2F1")

    tk.Label(create_window, text="Create Customer Account", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=10)

    labels = [
        "Account Number:", "Name:", "Date of Birth (YYYY-MM-DD):", 
        "Phone Number:", "Email:", "Aadhar Number:", 
        "Address:", "Account Type:", "Initial Balance:"
    ]
    entries = []

    for label in labels:
        tk.Label(create_window, text=label, bg="#E0F2F1").pack(pady=5)
        entry = tk.Entry(create_window)
        entry.pack(pady=5, padx=20, fill=tk.X)
        entries.append(entry)

    tk.Button(create_window, text="Submit", bg="#87CEFA", command=lambda: create_customer(
        entries[0].get(), entries[1].get(), entries[2].get(), 
        entries[3].get(), entries[4].get(), entries[5].get(), 
        entries[6].get(), entries[7].get(), entries[8].get()
    )).pack(pady=20)


#2.Window for View Customer Account
def view_customer_details():
    view_window = tk.Toplevel()
    view_window.title("View Customer Details")
    view_window.geometry("500x300")
    view_window.configure(bg="#E0F2F1")

    tk.Label(view_window, text="View Customer Details", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=10)

    tk.Label(view_window, text="Account Number:", bg="#E0F2F1").pack(pady=5)
    acc_num_entry = tk.Entry(view_window)
    acc_num_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Button(view_window, text="View Details", bg="#87CEFA", command=lambda: view_customer(acc_num_entry.get())).pack(pady=10)

#3.Window for Displaying Customer Details
def update_customer_details():
    update_window = tk.Toplevel()
    update_window.title("Update Customer Details")
    update_window.geometry("500x300")
    update_window.configure(bg="#E0F2F1")

    tk.Label(update_window, text="Update Customer Details", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=10)

    tk.Label(update_window, text="Account Number:", bg="#E0F2F1").pack(pady=5)
    acc_num_entry = tk.Entry(update_window)
    acc_num_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Label(update_window, text="Field to Change (e.g., name, phone_number):", bg="#E0F2F1").pack(pady=5)
    field_entry = tk.Entry(update_window)
    field_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Label(update_window, text="New Value:", bg="#E0F2F1").pack(pady=5)
    new_value_entry = tk.Entry(update_window)
    new_value_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Button(update_window, text="Update", bg="#87CEFA", command=lambda: update_customer(acc_num_entry.get(), field_entry.get(), new_value_entry.get())).pack(pady=20)

#4.Window for Transaction
def perform_transaction_window():
    transaction_window = tk.Toplevel()
    transaction_window.title("Perform Transaction")
    transaction_window.geometry("500x400")  
    transaction_window.configure(bg="#E0F2F1")

    tk.Label(transaction_window, text="Perform Transaction", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=10)

    tk.Label(transaction_window, text="Account Number:", bg="#E0F2F1").pack(pady=5)
    acc_num_entry = tk.Entry(transaction_window)
    acc_num_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Label(transaction_window, text="Amount:", bg="#E0F2F1").pack(pady=5)
    amount_entry = tk.Entry(transaction_window)
    amount_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Label(transaction_window, text="Transaction Type:", bg="#E0F2F1").pack(pady=5)
    transaction_type_var = tk.StringVar(value='Deposit')
    tk.Radiobutton(transaction_window, text="Deposit", variable=transaction_type_var, value='Deposit', bg="#E0F2F1").pack(pady=5)
    tk.Radiobutton(transaction_window, text="Withdrawal", variable=transaction_type_var, value='Withdrawal', bg="#E0F2F1").pack(pady=5)

    tk.Button(transaction_window, text="Submit", bg="#87CEFA", command=lambda: perform_transaction(acc_num_entry.get(), amount_entry.get(), transaction_type_var.get())).pack(pady=20)

#5.Window for Viewing Balance of Customer
def check_balance_window():
    balance_window = tk.Toplevel()
    balance_window.title("Check Balance")
    balance_window.geometry("500x300")
    balance_window.configure(bg="#E0F2F1")

    tk.Label(balance_window, text="Check Balance", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=10)

    tk.Label(balance_window, text="Account Number:", bg="#E0F2F1").pack(pady=5)
    acc_num_entry = tk.Entry(balance_window)
    acc_num_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Button(balance_window, text="Check Balance", bg="#87CEFA", command=lambda: check_balance(acc_num_entry.get())).pack(pady=20)

#6.Window for Deleting Account
def delete_customer_account():
    delete_window = tk.Toplevel()
    delete_window.title("Delete Customer Account")
    delete_window.geometry("500x300")
    delete_window.configure(bg="#E0F2F1")

    tk.Label(delete_window, text="Delete Customer Account", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=10)

    tk.Label(delete_window, text="Account Number:", bg="#E0F2F1").pack(pady=5)
    acc_num_entry = tk.Entry(delete_window)
    acc_num_entry.pack(pady=5, padx=20, fill=tk.X)

    tk.Button(delete_window, text="Delete Account", bg="#87CEFA", command=lambda: delete_customer(acc_num_entry.get())).pack(pady=20)

#Showing Menu
def show_menu():
    menu_window = tk.Tk()
    menu_window.title("Menu - Bank Management System")
    menu_window.geometry("850x650")
    menu_window.configure(bg="#FFFFFF")

    logo_path = r"D:\Pratham\python programs\12 proj\logo.png"

    try:
        logo = Image.open(logo_path)
        logo = logo.resize((200, 100), Image.Resampling.LANCZOS)  
        logo = ImageTk.PhotoImage(logo)

        header_frame = tk.Frame(menu_window, bg="#00796B", padx=10, pady=10)
        header_frame.pack(fill=tk.X)

        logo_label = tk.Label(header_frame, image=logo, bg="#00796B")
        logo_label.pack(pady=20)

    except Exception as e:
        print(f"Error loading logo: {e}")
        logo = None

    menu_frame = tk.Frame(menu_window, bg="#E0F2F1", padx=10, pady=10)
    menu_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(menu_frame, text="Select an option to proceed:", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=10)

    functions = {
        "Create New Account": create_customer_account,
        "View Account Details": view_customer_details,
        "Update Account Details": update_customer_details,
        "Perform Transaction": perform_transaction_window,
        "Check Account Balance": check_balance_window,
        "Delete Account": delete_customer_account,
        "Exit": menu_window.destroy
    }

    for func_name, func_command in functions.items():
        btn_color = "#B2DFDB" if func_name == "Create New Account" else (
                    "#C8E6C9" if func_name == "View Account Details" else (
                    "#FFE082" if func_name == "Update Account Details" else (
                    "#80DEEA" if func_name == "Perform Transaction" else (
                    "#FFCCBC" if func_name == "Check Account Balance" else (
                    "#F44336" if func_name == "Delete Account" else "#FFAB91")))))
        btn = tk.Button(menu_frame, text=func_name, font=("Arial", 14), bg=btn_color, fg="black", command=func_command)
        btn.pack(pady=5, padx=20, fill=tk.X)

    menu_window.mainloop()

#For Login Button
def handle_login(username_entry, password_entry, login_window):
    """Handle the login process."""
    username = username_entry.get()
    password = password_entry.get()

    if employee_login(username, password):  
        login_window.destroy()  
        show_menu()  


# Define the login window function
def create_login_window():
    """Display the login screen for the bank management system."""
    login_window = tk.Tk()
    login_window.title("Employee Login - DT Bank")

    window_width = 800
    window_height = 600
    login_window.geometry(f"{window_width}x{window_height}")
    login_window.configure(bg="#FFFFFF")

    logo_path = r"D:\Pratham\python programs\12 proj\logo.png"

    try:
        logo = Image.open(logo_path)
        logo = logo.resize((200, 100), Image.Resampling.LANCZOS)  # Resize the logo as needed
        logo = ImageTk.PhotoImage(logo)

        header_frame = tk.Frame(login_window, bg="#00796B", padx=10, pady=10)
        header_frame.pack(fill=tk.X)

        logo_label = tk.Label(header_frame, image=logo, bg="#00796B")
        logo_label.pack(pady=10)

    except Exception as e:
        print(f"Error loading logo: {e}")
        logo = None

    login_frame = tk.Frame(login_window, bg="#E0F2F1", padx=10, pady=10)
    login_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(login_frame, text="Employee Login", font=("Arial", 18, "bold"), bg="#E0F2F1").pack(pady=20)

    tk.Label(login_frame, text="Username:", font=("Arial", 12), bg="#E0F2F1").pack(pady=5)
    username_entry = tk.Entry(login_frame, font=("Arial", 12))
    username_entry.pack(pady=5)
   
    tk.Label(login_frame, text="Password:", font=("Arial", 12), bg="#E0F2F1").pack(pady=5)
    password_entry = tk.Entry(login_frame, font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    login_button = tk.Button(login_frame, text="Login", font=("Arial", 12, "bold"), bg="#00796B", fg="white", width=20, command=lambda: handle_login(username_entry, password_entry, login_window))
    login_button.pack(pady=20)

    login_window.mainloop()


if __name__ == "__main__":
    create_login_window()  
