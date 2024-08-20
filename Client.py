import socket
import hashlib
import threading
import time
import tkinter as tk
from tkinter import messagebox

# Função para calcular o checksum
def calculate_checksum(data):
    return hashlib.md5(data.encode()).hexdigest()

# Função para enviar pacotes (com opção de simulação de erro)
def send_packet(client_socket, server_address, seq_num, message, simulate_error=None):
    checksum = calculate_checksum(message)
    
    if simulate_error == "corrupção":
        checksum = "00000000000000000000000000000000"  # Corromper o checksum
    
    packet = f"{seq_num}{checksum}{message}"
    
    if simulate_error != "perda":
        client_socket.sendto(packet.encode(), server_address)

    start_timer(client_socket, server_address, seq_num, message)

# Função para iniciar o temporizador
def start_timer(client_socket, server_address, seq_num, message):
    timeout = 5
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            client_socket.settimeout(timeout - (time.time() - start_time))
            ack, _ = client_socket.recvfrom(1024)
            ack = ack.decode()
            
            if ack == f"ACK{seq_num}":
                messagebox.showinfo("Status", "Pacote enviado com sucesso!")
                return
        except socket.timeout:
            pass
    
    # Reenvio do pacote em caso de timeout
    alarm_message("Timeout: Nenhum ACK recebido. Reenviando o pacote.")
    send_packet(client_socket, server_address, seq_num, message)

# Função para lidar com alarmes no cliente
def alarm_message(msg):
    print(f"ALERTA: {msg}")

# Função do cliente
def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 12000)
    
    seq_num = 0
    
    def on_send():
        nonlocal seq_num
        message = entry_message.get()
        error_type = error_var.get()
        send_packet(client_socket, server_address, seq_num, message, simulate_error=error_type)
        seq_num = 1 - seq_num
    
    # Interface Tkinter
    root = tk.Tk()
    root.title("Cliente RDT 3.0")

    # Entrada de mensagem
    tk.Label(root, text="Mensagem:").grid(row=0, column=0)
    entry_message = tk.Entry(root, width=40)
    entry_message.grid(row=0, column=1)

    # Botão de envio
    tk.Button(root, text="Enviar", command=on_send).grid(row=1, column=1)

    # Simulação de erros
    error_var = tk.StringVar(value="normal")
    tk.Radiobutton(root, text="Envio Normal", variable=error_var, value="normal").grid(row=2, column=0)
    tk.Radiobutton(root, text="Simular Perda", variable=error_var, value="perda").grid(row=2, column=1)
    tk.Radiobutton(root, text="Simular Corrupção", variable=error_var, value="corrupção").grid(row=2, column=2)
    
    root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=client).start()