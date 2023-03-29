from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout, QLineEdit,\
    QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, \
    QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import mysql.connector
import env
import os


class DatabaseConnection:
    def __init__(self, host="localhost", user=os.getenv('DB_USER'), password=os.getenv('DB_PW'), database=os.getenv('DB_ADDRESS')):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Management System')
        self.setMinimumSize(800, 600)

        # creates items on menubar
        file_menu_item = self.menuBar().addMenu('&File')
        help_menu_item = self.menuBar().addMenu('&Help')
        edit_menu_item = self.menuBar().addMenu('&Edit')

        # creates actions for items in menubar
        add_student_action = QAction(
            QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon('icons/search.png'), 'Search', self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # main window
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ('Id', 'Name', 'Course', 'Mobile'))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # creates toolbar and adds elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # create status bar and add status bar element
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # detect cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton('Edit Record')
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton('Delete Record')
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusBar.removeWidget(child)

        self.statusBar.addWidget(edit_button)
        self.statusBar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM students')
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(data)))
        connection.close()

    # class methods
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Insert Student Data')
        self.setFixedHeight(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        # student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # add course widget
        self.course_name = QComboBox()
        courses = ['Biology', 'Astronomy', 'Physics', 'Dishwasher Repair']
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText('Mobile')
        layout.addWidget(self.mobile)

        # add submit button
        button = QPushButton('Register')
        layout.addWidget(button)
        button.clicked.connect(self.add_student)

        self.setLayout(layout)

    def add_student(self):
        # determines variables
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        # creates connection with db
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        # Inserts entry into database
        cursor.execute(
            'INSERT INTO students (name, course, mobile) VALUES (%s,%s,%s)', (name, course, mobile))
        # commit and closes connections
        connection.commit()
        cursor.close()
        connection.close()
        # close window
        self.close()
        # reload data on mainpage
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Search Students')

        layout = QVBoxLayout()

        # defines name to be searched in DB
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # search button
        button = QPushButton('Search')
        button.clicked.connect(self.search)
        layout.addWidget(button)

        # creates layout
        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM students WHERE name = %s', (name,))
        cursor.fetchall()
        items = main_window.table.findItems(
            name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Update Student Data')
        self.setFixedHeight(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        # get student record from DB
        rowIndex = main_window.table.currentRow()

        # get student id

        self.student_id = main_window.table.item(rowIndex, 0).text()

        # get student name from record
        student_name = main_window.table.item(rowIndex, 1).text()

        # student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # course widget
        course_name = main_window.table.item(rowIndex, 2).text()
        self.course_name = QComboBox()
        courses = ['Biology', 'Astronomy', 'Physics', 'Dishwasher Repair']
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # mobile widget
        mobile_number = main_window.table.item(rowIndex, 3).text()
        self.mobile_number = QLineEdit(mobile_number)
        self.mobile_number.setPlaceholderText('Mobile')
        layout.addWidget(self.mobile_number)

        # submit button
        button = QPushButton('Update')
        layout.addWidget(button)
        button.clicked.connect(self.update_student)

        self.setLayout(layout)

    def update_student(self):
        # create connection with database
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        # execute command to update entry
        cursor.execute(
            'UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s', (
                self.student_name.text(),
                self.course_name.itemText(self.course_name.currentIndex()),
                self.mobile_number.text(),
                self.student_id
            )
        )
        # commit changes and close connections
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        # creates window
        self.setWindowTitle('Delete Student Data')

        layout = QGridLayout()
        # creates text and buttons
        confirmation = QLabel('Are you sure?')
        positive_confirmation = QPushButton('Yes')
        negative_confirmation = QPushButton('No')

        # lay components out
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(positive_confirmation, 1, 0)
        layout.addWidget(negative_confirmation, 1, 1)
        self.setLayout(layout)

        # runs logic behind buttons
        positive_confirmation.clicked.connect(self.delete_student)
        negative_confirmation.clicked.connect(self.close)

    def delete_student(self):
        # get student record from DB
        rowIndex = main_window.table.currentRow()

        # get student id
        student_id = main_window.table.item(rowIndex, 0).text()

        # filter student and delete student
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('DELETE from students WHERE id = %s', (student_id,))

        # commit and closes connections
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        # closes window
        self.close()

        # creates window with confirmation
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle('Success')
        confirmation_widget.setText('Deletion was successful')
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    # creates instance with text
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        content = """
        This App was created during the course \"Python mega course\".
        Feel free to modify it."""
        self.setText(content)


# main application
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
