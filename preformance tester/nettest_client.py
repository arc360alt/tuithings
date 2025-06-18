import socket
import time
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 12345        # The port used by the server
TEST_DURATION = 8   # seconds for the client to run its test (slightly less than orchestrator's timeout)
DATA_CHUNK_SIZE = 4096 # Bytes to send/receive per operation

def run_client():
    total_bytes_sent = 0
    total_bytes_received = 0
    test_data = b'X' * DATA_CHUNK_SIZE # Prepare a chunk of data to send

    print("-------------------------")
    print(" Network Performance Test")
    print(" (Loopback Echo Throughput) ")
    print("-------------------------")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.settimeout(1) # Set a timeout for socket operations

            start_time = time.time()
            while time.time() - start_time < TEST_DURATION:
                try:
                    s.sendall(test_data)
                    total_bytes_sent += len(test_data)

                    received_data = s.recv(DATA_CHUNK_SIZE)
                    if not received_data:
                        print("Server closed connection prematurely.")
                        break
                    total_bytes_received += len(received_data)

                except socket.timeout:
                    print("Network client timed out (server might be slow or test finished).")
                    break
                except ConnectionResetError:
                    print("Connection reset by peer (server likely closed).")
                    break
                except BrokenPipeError:
                    print("Broken pipe (server likely closed).")
                    break

            end_time = time.time()
            time_taken = end_time - start_time

            # Calculate speeds
            send_speed_mbps = (total_bytes_sent / (1024 * 1024)) / time_taken if time_taken > 0 else 0
            recv_speed_mbps = (total_bytes_received / (1024 * 1024)) / time_taken if time_taken > 0 else 0

            print(f"Total Data Sent: {total_bytes_sent / (1024 * 1024):.2f} MB")
            print(f"Total Data Received: {total_bytes_received / (1024 * 1024):.2f} MB")
            print(f"Send Speed: {send_speed_mbps:.2f} MB/s")
            print(f"Receive Speed: {recv_speed_mbps:.2f} MB/s")

    except ConnectionRefusedError:
        print(f"Error: Connection refused. Is the server running on {HOST}:{PORT}?")
    except Exception as e:
        print(f"An error occurred during network client test: {e}")
    finally:
        sys.exit()

if __name__ == "__main__":
    run_client()
