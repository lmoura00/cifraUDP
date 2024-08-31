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
def send_ack(server_socket, client_address, seq_num, message=None, simulate_error=None):
    ack_packet = f"ACK{seq_num}"
    
    if message:
        ack_packet += message
    
    # Calcular checksum para o ACK
    ack_checksum = calculate_checksum(ack_packet)
    ack_packet = f"{ack_checksum}{ack_packet}"
    
    if simulate_error == "corrupção":
        ack_packet = "00000000000000000000000000000000" + ack_packet[32:]  # Corromper o checksum do ACK
    
    if simulate_error != "perda":
        server_socket.sendto(ack_packet.encode(), client_address)
    else:
        print("Simulação de perda do ACK. Não enviando o ACK.")

# Função do servidor
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 12000))
    
    # Definir um timeout opcional para o socket do servidor (por exemplo, 10 segundos)
    server_socket.settimeout(10)

    expected_seq_num = 0

    print("Servidor aguardando mensagens...")
    while True:
        try:
            packet, client_address = server_socket.recvfrom(1024)
            packet = packet.decode()

            seq_num = int(packet[0])
            checksum = packet[1:33]
            encrypted_message = packet[33:]

            # Verificação do checksum
            calculated_checksum = calculate_checksum(encrypted_message)

            if checksum == calculated_checksum and seq_num == expected_seq_num:
                print(f"----------------PACKAGE {seq_num}-----------------------\n")
                print(f"NUM SEQUENCIA: {seq_num}")
                print(f"CHECKSUM RECEBIDO: {checksum}")
                print(f"CHECKSUM EXPERADO: {checksum}")
                
                # Descriptografar a mensagem
                message = decrypt_message(encrypted_message)
                print(f"Mensagem recebida: {message}")

                # Criptografar de volta
                encrypted_message = encrypt_message(message)
                print(f"Mensagem criptografada: {encrypted_message}")

                # Enviar ACK com a mensagem criptografada de volta
                print(f"------------------FIM DO PACKAGE {seq_num}---------------------\n\n")

                send_ack(server_socket, client_address, seq_num, encrypted_message)
                expected_seq_num = 1 - expected_seq_num
            else:
                # Ignorar ou reenviar o último ACK se for duplicado
                print("Erro detectado. ACK anterior reenviado.")
                send_ack(server_socket, client_address, 1 - seq_num)

        except socket.timeout:
            # Timeout ocorreu, o servidor continua aguardando o próximo pacote
            print("Timeout ocorreu, aguardando próximo pacote...")
            continue

if __name__ == "__main__":
    threading.Thread(target=server).start()
