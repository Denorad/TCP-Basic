import sys
import time
import socket
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QInputDialog,
    QPushButton,
    QMainWindow,
    QApplication,
    QWidget,
    QTextEdit,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
)

clients = []

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("Luna")
        self.resize(700, 1000)

        self.username, ok = QInputDialog.getText(None, "Username", "Enter your username: ")
        if ok:
            print(f"Username: {self.username}")
        else:
            sys.exit()
        
        self.role, ok  = QInputDialog.getItem(None, "Role", "Select your role: ", ["Host", "Client"], 0, False)
        if ok:
            print(f"Role: {self.role}")
        else:
            sys.exit()

        self.ip, ok = QInputDialog.getText(None, "Ip", "Enter an Ip adresse: ", text=socket.gethostbyname(socket.gethostname()))
        if ok:
            print(f"Ip: {self.ip}")
        else:
            sys.exit()
        
        self.port, ok = QInputDialog.getText(None, "Port", "Port: ", text="7777")
        if ok:
            print(f"Port: {self.port}")
        else:
            sys.exit()
        
        self.messages = QTextEdit()

        self.messages.setReadOnly(True)
        self.msg = QLineEdit()
        self.msg.setMaximumHeight(50)

        userLayout = QHBoxLayout()

        self.sendMsgBtn = QPushButton()
        self.sendMsgBtn.setText("Send")
        self.sendMsgBtn.setMaximumHeight(50)
        self.sendMsgBtn.clicked.connect(self.sendMsg)

        userLayout.addWidget(self.msg)
        userLayout.addWidget(self.sendMsgBtn)


        layout = QVBoxLayout()
        layout.addWidget(self.messages)
        layout.addLayout(userLayout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        if self.role == "Host":
            print("Host lauching server!")
            self.messages.append("[SERVER: Connected as host]")
            threading.Thread(target=self.startServer).start()
        
        if self.role == "Client":
            print("Client joining!")
            self.messages.append("[SERVER: Connected as client]")
            threading.Thread(target=self.connectClient).start()

    def sendMsg(self):
        if self.role == "Host" and self.msg.text() != "":
            self.messages.append(f"[{time.strftime("%H:%M:%S")}] {self.username}: {self.msg.text()}")
            self.broadcastMsg()
        elif self.role == "Client" and self.msg.text() != "":
            self.handleMessages()

        self.msg.setText(None)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and self.msg.text() != "":
            self.sendMsg()
            
    def startServer(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_ecoute:
            socket_ecoute.bind(('', int(self.port)))
            socket_ecoute.listen()
            while True:
                connexion_client, adresse_client = socket_ecoute.accept()
                clients.append(connexion_client)
                self.messages.append(f"Client connected: {adresse_client}")
                threading.Thread(target=self.handleClient, args=(connexion_client,), daemon=True).start()


    def broadcastMsg(self):
        for client in clients:
            combined_msg = f"{self.username}:{self.msg.text()}"
            client.send(combined_msg.encode("utf-8"))
    
    def broadcastMsgUser(self, data):
        for client in clients:
            client.send(data.encode("utf-8"))
    
    def handleClient(self, client_socket):
        while True: 
            try:
                data = client_socket.recv(1024).decode("utf-8")
                if data:
                    self.broadcastMsgUser(data)
                    name, message = data.split(":", 1)
                    current_time = time.strftime("%H:%M:%S")
                    self.messages.append(f"[{current_time}] {name}: {message}")
            except:
                clients.remove(client_socket)
                client_socket.close()
                break

    def connectClient(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.connexion_serveur:
            self.connexion_serveur.connect((self.ip, int(self.port)))
            while True:
                data = self.connexion_serveur.recv(1024).decode("utf-8").strip()
                if ":" in data:
                    name, message = data.split(":", 1)
                    self.messages.append(f"[{time.strftime('%H:%M:%S')}] {name}: {message}")

    def handleMessages(self):
        try:
            combined_msg = f"{self.username}:{self.msg.text()}"
            self.connexion_serveur.send(combined_msg.encode("utf-8"))
        except:
            self.connexion_serveur.close()

app = QApplication(sys.argv)
window = MainWindow() 
window.show()

app.exec()