import sys
import sqlite3
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QDialog
from datetime import datetime

# Classe principal da aplicação
class LibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()  # Inicializa a interface do usuário
        self.initDB()  # Inicializa o banco de dados SQLite
        self.loadBooks()  # Carrega os livros do banco de dados

    def initUI(self):
        # Configurações da janela principal
        self.setWindowTitle("Sistema de Gerenciamento de Biblioteca")
        self.setGeometry(100, 100, 400, 300)

        # Cria um widget central e define-o como centralWidget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal da janela
        self.layout = QVBoxLayout()

        # Lista de livros exibida na interface
        self.book_list = QListWidget()
        self.layout.addWidget(self.book_list)

        # Botão para adicionar um livro
        self.add_button = QPushButton("Adicionar Livro")
        self.add_button.clicked.connect(self.addBook)
        self.layout.addWidget(self.add_button)

        # Botão para emprestar um livro
        self.borrow_button = QPushButton("Emprestar Livro")
        self.borrow_button.clicked.connect(self.borrowBook)
        self.layout.addWidget(self.borrow_button)

        # Botão para devolver um livro
        self.return_button = QPushButton("Devolver Livro")
        self.return_button.clicked.connect(self.returnBook)
        self.layout.addWidget(self.return_button)

        # Define o layout como layout principal
        self.central_widget.setLayout(self.layout)

        self.book_id = None  # Variável para armazenar o ID do livro selecionado

    def initDB(self):
        # Conecta-se ao banco de dados SQLite e cria uma tabela de livros se não existir
        self.conn = sqlite3.connect("library.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, author TEXT, status TEXT, borrow_date TEXT, return_date TEXT)")
        self.conn.commit()

    def loadBooks(self):
        # Carrega os livros do banco de dados e exibe na lista
        self.book_list.clear()
        self.cursor.execute("SELECT id, title, author, status, borrow_date, return_date FROM books")
        books = self.cursor.fetchall()
        for book in books:
            status = book[3]
            borrow_date = self.formatDate(book[4])
            return_date = self.formatDate(book[5])
            if status == "Emprestado":
                status += f" (Emprestado em {borrow_date}"
            self.book_list.addItem(f"{book[1]} by {book[2]} ({status})")
        self.conn.commit()

    def formatDate(self, date_str):
        if date_str is not None:
            try:
                datetime_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                return datetime_obj.strftime("%d/%m/%Y")
            except ValueError:
                return date_str
        return ""

    def addBook(self):
        # Abre uma caixa de diálogo para adicionar um livro ao banco de dados
        title, ok = InputDialog.getText("Adicionar Livro", "Digite o título do livro:")
        if ok:
            author, ok = InputDialog.getText("Adicionar Livro", "Digite o autor do livro:")
            if ok:
                self.cursor.execute("INSERT INTO books (title, author, status) VALUES (?, ?, ?)", (title, author, "Disponível"))
                self.conn.commit()
                self.loadBooks()

    def borrowBook(self):
        # Marca um livro como emprestado no banco de dados
        selected_item = self.book_list.currentItem()
        if selected_item:
            title = selected_item.text().split("by")[0].strip()
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("UPDATE books SET status = 'Emprestado', borrow_date = ? WHERE title = ?", (current_datetime, title))
            self.conn.commit()
            self.loadBooks()

    def returnBook(self):
        # Marca um livro como devolvido no banco de dados
        selected_item = self.book_list.currentItem()
        if selected_item:
            title = selected_item.text().split("by")[0].strip()
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("UPDATE books SET status = 'Disponível', return_date = ? WHERE title = ?", (current_datetime, title))
            self.conn.commit()
            self.loadBooks()

    def closeEvent(self, event):
        # Fecha a conexão com o banco de dados ao fechar a janela
        self.conn.close()

# Classe para criar uma caixa de diálogo de entrada
class InputDialog(QDialog):
    @staticmethod
    def getText(title, label):
        dialog = InputDialog()
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))
        dialog.text_input = QLineEdit()
        layout.addWidget(dialog.text_input)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        result = dialog.exec()
        text = dialog.text_input.text()
        return (text, result == QDialog.Accepted)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LibraryApp()
    window.show()
    sys.exit(app.exec())
