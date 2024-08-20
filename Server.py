import socket
import hashlib
import threading

# Função para calcular o checksum
def calculate_checksum(data):
    return hashlib.md5(data.encode()).hexdigest()

# Função para criptografar a mensagem (substituição simples)
def encrypt_message(message):
    encrypted = ""
    for char in message:
        encrypted += chr((ord(char) + 3) % 256)  # Shift simples de 3
    return encrypted

# Função para descriptografar a mensagem (substituição simples)
def decrypt_message(encrypted_message):
    decrypted = ""
    for char in encrypted_message:
        decrypted += chr((ord(char) - 3) % 256)
    return decrypted

# Função para envio de ACK
def send_ack(server_socket, client_address, seq_num):
    ack_packet = f"ACK{seq_num}"
    server_socket.sendto(ack_packet.encode(), client_address)

# Função do servidor
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 12000))

    expected_seq_num = 0

    print("Servidor aguardando mensagens...")

    while True:
        packet, client_address = server_socket.recvfrom(1024)
        packet = packet.decode()

        seq_num = int(packet[0])
        checksum = packet[1:33]
        encrypted_message = packet[33:]

        # Verificação do checksum
        calculated_checksum = calculate_checksum(encrypted_message)

        if checksum == calculated_checksum and seq_num == expected_seq_num:
            # Descriptografar a mensagem
            message = decrypt_message(encrypted_message)
            print(f"Mensagem recebida: {message}")

            # Criptografar de volta
            encrypted_message = encrypt_message(message)
            print(f"Mensagem criptografada: {encrypted_message}")

            # Enviar ACK
            send_ack(server_socket, client_address, seq_num)
            expected_seq_num = 1 - expected_seq_num
        else:
            # Ignorar ou reenviar o último ACK se for duplicado
            print("Erro detectado. ACK anterior reenviado.")
            send_ack(server_socket, client_address, 1 - seq_num)

if __name__ == "__main__":
    threading.Thread(target=server).start()