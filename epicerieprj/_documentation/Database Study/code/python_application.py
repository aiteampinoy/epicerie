import sys
import os
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QFormLayout, QMessageBox, QDialog, QTextEdit, QGroupBox, QCheckBox,
    QSpinBox, QDoubleSpinBox, QDateEdit, QFrame, QStackedWidget, QScrollArea,
    QSplitter, QHeaderView, QStyle, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont
import pyodbc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection
class DatabaseConnection:
    def __init__(self):
        self.connection = None
        try:
            # Load configuration from environment variables
            self.server = os.getenv("DB_SERVER")
            self.database = os.getenv("DB_NAME")
            self.username = os.getenv("DB_USERNAME")
            self.password = os.getenv("DB_PASSWORD")
            
            # Create connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
            
            # Connect to database
            self.connection = pyodbc.connect(conn_str)
            print("Database connection successful")
            
        except Exception as e:
            print(f"Error connecting to database: {e}")
    
    def get_connection(self):
        return self.connection
    
    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed")

# Authentication System
class AuthenticationSystem:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        
    def authenticate(self, username, password):
        # This is a simplified authentication system
        # In a real application, use proper hashing and security
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT UserID, UserName, UserRole 
                FROM Users 
                WHERE UserName=? AND Password=? AND Status='Active'
            """
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            
            if result:
                # Return user data on successful authentication
                return {"user_id": result[0], "username": result[1], "role": result[2]}
            else:
                return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

# Main Application Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Philippine Supplier and Product Management System")
        self.setMinimumSize(1200, 800)
        
        # Initialize database connection
        self.db = DatabaseConnection()
        self.conn = self.db.get_connection()
        
        # Set up the authentication system
        self.auth_system = AuthenticationSystem(self.conn)
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        # Set central widget
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create login widget
        self.login_widget = LoginWidget(self.auth_system, self.on_login_success)
        
        # Create main dashboard widget
        self.dashboard_widget = DashboardWidget(self.conn)
        
        # Add widgets to stack
        self.central_widget.addWidget(self.login_widget)
        self.central_widget.addWidget(self.dashboard_widget)
        
        # Start with login screen
        self.central_widget.setCurrentIndex(0)
    
    def on_login_success(self, user_data):
        # Set user data in dashboard
        self.dashboard_widget.set_user_data(user_data)
        
        # Switch to dashboard view
        self.central_widget.setCurrentIndex(1)
    
    def closeEvent(self, event):
        # Close database connection when application exits
        self.db.close_connection()
        event.accept()

# Login Widget
class LoginWidget(QWidget):
    def __init__(self, auth_system, login_callback):
        super().__init__()
        self.auth_system = auth_system
        self.login_callback = login_callback
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a frame for the login form
        login_frame = QFrame()
        login_frame.setFrameShape(QFrame.StyledPanel)
        login_frame.setMaximumWidth(400)
        login_frame.setMaximumHeight(300)
        
        # Login form layout
        form_layout = QVBoxLayout(login_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("System Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Username input
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        
        # Password input
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.attempt_login)
        
        # Add widgets to form layout
        form_layout.addWidget(title_label)
        form_layout.addSpacing(20)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.login_button)
        
        # Center the login frame in the widget
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(login_frame)
        container_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(container_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return
        
        # Attempt authentication
        user_data = self.auth_system.authenticate(username, password)
        
        if user_data:
            self.login_callback(user_data)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

# Dashboard Widget
class DashboardWidget(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.user_data = None
        self.setup_ui()
    
    def set_user_data(self, user_data):
        self.user_data = user_data
        self.update_user_info()
        
        # Update access control based on user role
        is_admin = self.user_data["role"] == "Administrator"
        self.supplier_management.set_admin_access(is_admin)
        self.product_management.set_admin_access(is_admin)
        self.catalog_management.set_admin_access(is_admin)
    
    def update_user_info(self):
        if self.user_data:
            self.user_label.setText(f"User: {self.user_data['username']} | Role: {self.user_data['role']}")
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header section
        header_layout = QHBoxLayout()
        
        # System title
        title_label = QLabel("Philippine Supplier and Product Management System")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # User info
        self.user_label = QLabel("User: Not logged in")
        
        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        
        # Add to header layout
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.user_label)
        header_layout.addWidget(logout_button)
        
        # Create tab widget for main sections
        tab_widget = QTabWidget()
        
        # Create each management tab
        self.supplier_management = SupplierManagementTab(self.db_connection)
        self.product_management = ProductManagementTab(self.db_connection)
        self.catalog_management = CatalogManagementTab(self.db_connection)
        self.reports = ReportsTab(self.db_connection)
        
        # Add tabs to tab widget
        tab_widget.addTab(self.supplier_management, "Supplier Management")
        tab_widget.addTab(self.product_management, "Product Management")
        tab_widget.addTab(self.catalog_management, "Catalog Management")
        tab_widget.addTab(self.reports, "Reports")
        
        # Add layouts and widgets to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(tab_widget)
        
        self.setLayout(main_layout)
    
    def logout(self):
        # Switch back to login screen
        self.parent().parent().central_widget.setCurrentIndex(0)

# Supplier Management Tab
class SupplierManagementTab(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.is_admin = False
        self.setup_ui()
        
    def set_admin_access(self, is_admin):
        self.is_admin = is_admin
        self.add_supplier_button.setEnabled(is_admin)
        self.edit_supplier_button.setEnabled(is_admin)
        self.toggle_status_button.setEnabled(is_admin)
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Control panel
        control_panel = QHBoxLayout()
        
        # Search box
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by company name, TIN, etc.")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_suppliers)
        
        # Add supplier button
        self.add_supplier_button = QPushButton("Add New Supplier")
        self.add_supplier_button.clicked.connect(self.add_supplier)
        
        # Edit supplier button
        self.edit_supplier_button = QPushButton("Edit Supplier")
        self.edit_supplier_button.clicked.connect(self.edit_supplier)
        
        # Toggle status button
        self.toggle_status_button = QPushButton("Change Status")
        self.toggle_status_button.clicked.connect(self.toggle_supplier_status)
        
        # Add to control panel
        control_panel.addWidget(search_label)
        control_panel.addWidget(self.search_input)
        control_panel.addWidget(search_button)
        control_panel.addStretch()
        control_panel.addWidget(self.add_supplier_button)
        control_panel.addWidget(self.edit_supplier_button)
        control_panel.addWidget(self.toggle_status_button)
        
        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(6)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Supplier ID", "TIN", "Company Name", "Date Created", "Date Updated", "Status"
        ])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Add to main layout
        main_layout.addLayout(control_panel)
        main_layout.addWidget(self.suppliers_table)
        
        self.setLayout(main_layout)
        
        # Load suppliers on initialization
        self.load_suppliers()
    
    def load_suppliers(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT SupplierID, TIN, CompanyName, DateCreated, DateUpdated, Status 
                FROM Suppliers 
                ORDER BY CompanyName
            """)
            
            # Clear table
            self.suppliers_table.setRowCount(0)
            
            # Populate table with suppliers
            for row_num, row_data in enumerate(cursor.fetchall()):
                self.suppliers_table.insertRow(row_num)
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                    self.suppliers_table.setItem(row_num, col_num, item)
        
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading suppliers: {e}")
    
    def search_suppliers(self):
        search_text = self.search_input.text().strip()
        
        if not search_text:
            self.load_suppliers()
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT SupplierID, TIN, CompanyName, DateCreated, DateUpdated, Status 
                FROM Suppliers 
                WHERE CompanyName LIKE ? OR TIN LIKE ?
                ORDER BY CompanyName
            """, (f'%{search_text}%', f'%{search_text}%'))
            
            # Clear table
            self.suppliers_table.setRowCount(0)
            
            # Populate table with search results
            for row_num, row_data in enumerate(cursor.fetchall()):
                self.suppliers_table.insertRow(row_num)
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                    self.suppliers_table.setItem(row_num, col_num, item)
        
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error searching suppliers: {e}")
    
    def add_supplier(self):
        if not self.is_admin:
            QMessageBox.warning(self, "Access Denied", "Only administrators can add new suppliers.")
            return
            
        dialog = SupplierDialog(self.db_connection)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_suppliers()
    
    def edit_supplier(self):
        if not self.is_admin:
            QMessageBox.warning(self, "Access Denied", "Only administrators can edit suppliers.")
            return
            
        # Get selected supplier
        selected_items = self.suppliers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to edit.")
            return
            
        # Get supplier ID from the first column
        supplier_id = int(self.suppliers_table.item(selected_items[0].row(), 0).text())
        
        dialog = SupplierDialog(self.db_connection, supplier_id)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_suppliers()
    
    def toggle_supplier_status(self):
        if not self.is_admin:
            QMessageBox.warning(self, "Access Denied", "Only administrators can change supplier status.")
            return
            
        # Get selected supplier
        selected_items = self.suppliers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to change status.")
            return
            
        # Get supplier ID and current status
        row = selected_items[0].row()
        supplier_id = int(self.suppliers_table.item(row, 0).text())
        current_status = self.suppliers_table.item(row, 5).text()
        
        # Determine new status
        new_status = "Inactive" if current_status == "Active" else "Active"
        
        # Confirm status change
        reply = QMessageBox.question(
            self, 
            "Confirm Status Change",
            f"Are you sure you want to change the status from '{current_status}' to '{new_status}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Update status
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "UPDATE Suppliers SET Status = ?, DateUpdated = GETDATE() WHERE SupplierID = ?",
                    (new_status, supplier_id)
                )
                self.db_connection.commit()
                
                # Refresh the table
                self.load_suppliers()
                
                QMessageBox.information(self, "Status Updated", f"Supplier status changed to {new_status}.")
                
            except Exception as e:
                self.db_connection.rollback()
                QMessageBox.critical(self, "Database Error", f"Error updating supplier status: {e}")

# Supplier Dialog for Add/Edit
class SupplierDialog(QDialog):
    def __init__(self, db_connection, supplier_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.supplier_id = supplier_id
        self.is_edit_mode = supplier_id is not None
        
        self.setWindowTitle("Add New Supplier" if not self.is_edit_mode else "Edit Supplier")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.setup_ui()
        
        # Load supplier data if in edit mode
        if self.is_edit_mode:
            self.load_supplier_data()
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Create tab widget for different supplier aspects
        tab_widget = QTabWidget()
        
        # Basic Information tab
        basic_info_widget = QWidget()
        basic_info_layout = QFormLayout()
        
        # TIN
        self.tin_input = QLineEdit()
        self.tin_input.setPlaceholderText("Tax Identification Number")
        basic_info_layout.addRow("TIN:", self.tin_input)
        
        # Company Name
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Company Name")
        basic_info_layout.addRow("Company Name:", self.company_name_input)
        
        # Status (only for edit mode)
        if self.is_edit_mode:
            self.status_combo = QComboBox()
            self.status_combo.addItems(["Active", "Inactive"])
            basic_info_layout.addRow("Status:", self.status_combo)
        
        basic_info_widget.setLayout(basic_info_layout)
        
        # Addresses tab
        addresses_widget = QWidget()
        addresses_layout = QVBoxLayout()
        
        # Add Address button
        add_address_button = QPushButton("Add Address")
        add_address_button.clicked.connect(self.add_address)
        
        # Addresses table
        self.addresses_table = QTableWidget()
        self.addresses_table.setColumnCount(8)
        self.addresses_table.setHorizontalHeaderLabels([
            "ID", "Address Line 1", "Address Line 2", "City/Municipality", 
            "Province", "Postal Code", "Type", "Primary"
        ])
        self.addresses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Address control buttons
        address_buttons_layout = QHBoxLayout()
        edit_address_button = QPushButton("Edit Address")
        edit_address_button.clicked.connect(self.edit_address)
        delete_address_button = QPushButton("Delete Address")
        delete_address_button.clicked.connect(self.delete_address)
        set_primary_address_button = QPushButton("Set as Primary")
        set_primary_address_button.clicked.connect(self.set_primary_address)
        
        address_buttons_layout.addWidget(edit_address_button)
        address_buttons_layout.addWidget(delete_address_button)
        address_buttons_layout.addWidget(set_primary_address_button)
        
        addresses_layout.addWidget(add_address_button)
        addresses_layout.addWidget(self.addresses_table)
        addresses_layout.addLayout(address_buttons_layout)
        addresses_widget.setLayout(addresses_layout)
        
        # Contact Numbers tab
        contact_numbers_widget = QWidget()
        contact_numbers_layout = QVBoxLayout()
        
        # Add Contact Number button
        add_contact_button = QPushButton("Add Contact Number")
        add_contact_button.clicked.connect(self.add_contact_number)
        
        # Contact Numbers table
        self.contact_numbers_table = QTableWidget()
        self.contact_numbers_table.setColumnCount(4)
        self.contact_numbers_table.setHorizontalHeaderLabels([
            "ID", "Contact Number", "Type", "Primary"
        ])
        self.contact_numbers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Contact Number control buttons
        contact_buttons_layout = QHBoxLayout()
        edit_contact_button = QPushButton("Edit Contact Number")
        edit_contact_button.clicked.connect(self.edit_contact_number)
        delete_contact_button = QPushButton("Delete Contact Number")
        delete_contact_button.clicked.connect(self.delete_contact_number)
        set_primary_contact_button = QPushButton("Set as Primary")
        set_primary_contact_button.clicked.connect(self.set_primary_contact_number)
        
        contact_buttons_layout.addWidget(edit_contact_button)
        contact_buttons_layout.addWidget(delete_contact_button)
        contact_buttons_layout.addWidget(set_primary_contact_button)
        
        contact_numbers_layout.addWidget(add_contact_button)
        contact_numbers_layout.addWidget(self.contact_numbers_table)
        contact_numbers_layout.addLayout(contact_buttons_layout)
        contact_numbers_widget.setLayout(contact_numbers_layout)
        
        # Email Addresses tab
        emails_widget = QWidget()
        emails_layout = QVBoxLayout()
        
        # Add Email button
        add_email_button = QPushButton("Add Email Address")
        add_email_button.clicked.connect(self.add_email)
        
        # Emails table
        self.emails_table = QTableWidget()
        self.emails_table.setColumnCount(4)
        self.emails_table.setHorizontalHeaderLabels([
            "ID", "Email Address", "Type", "Primary"
        ])
        self.emails_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Email control buttons
        email_buttons_layout = QHBoxLayout()
        edit_email_button = QPushButton("Edit Email Address")
        edit_email_button.clicked.connect(self.edit_email)
        delete_email_button = QPushButton("Delete Email Address")
        delete_email_button.clicked.connect(self.delete_email)
        set_primary_email_button = QPushButton("Set as Primary")
        set_primary_email_button.clicked.connect(self.set_primary_email)
        
        email_buttons_layout.addWidget(edit_email_button)
        email_buttons_layout.addWidget(delete_email_button)
        email_buttons_layout.addWidget(set_primary_email_button)
        
        emails_layout.addWidget(add_email_button)
        emails_layout.addWidget(self.emails_table)
        emails_layout.addLayout(email_buttons_layout)
        emails_widget.setLayout(emails_layout)
        
        # Contact Persons tab
        contact_persons_widget = QWidget()
        contact_persons_layout = QVBoxLayout()
        
        # Add Contact Person button
        add_person_button = QPushButton("Add Contact Person")
        add_person_button.clicked.connect(self.add_contact_person)
        
        # Contact Persons table
        self.contact_persons_table = QTableWidget()
        self.contact_persons_table.setColumnCount(7)
        self.contact_persons_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "Position", 
            "Email", "Contact Number", "Status"
        ])
        self.contact_persons_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Contact Person control buttons
        person_buttons_layout = QHBoxLayout()
        edit_person_button = QPushButton("Edit Contact Person")
        edit_person_button.clicked.connect(self.edit_contact_person)
        toggle_person_status_button = QPushButton("Change Status")
        toggle_person_status_button.clicked.connect(self.toggle_contact_person_status)
        
        person_buttons_layout.addWidget(edit_person_button)
        person_buttons_layout.addWidget(toggle_person_status_button)
        
        contact_persons_layout.addWidget(add_person_button)
        contact_persons_layout.addWidget(self.contact_persons_table)
        contact_persons_layout.addLayout(person_buttons_layout)
        contact_persons_widget.setLayout(contact_persons_layout)
        
        # Add tabs to tab widget
        tab_widget.addTab(basic_info_widget, "Basic Information")
        tab_widget.addTab(addresses_widget, "Addresses")
        tab_widget.addTab(contact_numbers_widget, "Contact Numbers")
        tab_widget.addTab(emails_widget, "Email Addresses")
        tab_widget.addTab(contact_persons_widget, "Contact Persons")
        
        # Buttons at the bottom
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_supplier)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        
        # Add layouts and widgets to main layout
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def load_supplier_data(self):
        try:
            # Load basic information
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT TIN, CompanyName, Status FROM Suppliers WHERE SupplierID = ?",
                (self.supplier_id,)
            )
            result = cursor.fetchone()
            
            if result:
                self.tin_input.setText(result[0])
                self.company_name_input.setText(result[1])
                if self.is_edit_mode:
                    self.status_combo.setCurrentText(result[2])
            
            # Load addresses
            self.load_addresses()
            
            # Load contact numbers
            self.load_contact_numbers()
            
            # Load email addresses
            self.load_emails()
            
            # Load contact persons
            self.load_contact_persons()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading supplier data: {e}")
    
    def load_addresses(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT AddressID, AddressLine1, AddressLine2, CityMunicipality, 
                       Province, PostalCode, AddressType, IsPrimary
                FROM SupplierAddresses
                WHERE SupplierID = ?
                ORDER BY IsPrimary DESC, AddressID
            """, (self.supplier_id,))
            
            # Clear table
            self.addresses_table.setRowCount(0)
            
            # Populate table with addresses
            for row_num, row_data in enumerate(cursor.fetchall()):
                self.addresses_table.insertRow(row_num)
                for col_num, data in enumerate(row_data):
                    if col_num == 7:  # IsPrimary column
                        item = QTableWidgetItem("Yes" if data else "No")
                    else:
                        item = QTableWidgetItem(str(data) if data is not None else "")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                    self.addresses_table.setItem(row_num, col_num, item)
        
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading addresses: {e}")
    
    def load_contact_numbers(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT ContactNumberID, ContactNumber, NumberType, IsPrimary
                FROM SupplierContactNumbers
                WHERE SupplierID = ?
                ORDER BY IsPrimary DESC, ContactNumberID
            """, (self.supplier_id,))
            
            # Clear table
            self.contact_numbers_table.setRowCount(0)
            
            # Populate table with contact numbers
            for row_num, row_data in enumerate(cursor.fetchall