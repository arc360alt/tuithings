import socket
import sys
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 12345        # Port to listen on (non-privileged ports are > 1023)

def run_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow address reuse
            s.bind((HOST, PORT))
            s.listen()
            print(f"Server listening on {HOST}:{PORT}")

            # This server will accept one connection, echo data, and then exit gracefully
            # after a short timeout if no more data, or when the client closes.
            # It's designed for the orchestrator to manage its lifetime.
            s.settimeout(5) # Set a timeout for accepting new connections
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                conn.settimeout(1) # Set timeout for receiving data from client
                while True:
                    try:
                        data = conn.recv(4096) # Receive up to 4KB of data
                        if not data:
                            break # Client closed connection
                        conn.sendall(data) # Echo back the received data
                    except socket.timeout:
                        break # No more data from client for 1 second, assume done
                    except ConnectionResetError:
                        print("Client disconnected unexpectedly.")
                        break
    except socket.error as e:
        print(f"Server socket error: {e}")
    except Exception as e:
        print(f"An unexpected server error occurred: {e}")
    finally:
        print("Server shutting down.")
        sys.exit() # Ensure the server process terminates

if __name__ == "__main__":
    run_server()
