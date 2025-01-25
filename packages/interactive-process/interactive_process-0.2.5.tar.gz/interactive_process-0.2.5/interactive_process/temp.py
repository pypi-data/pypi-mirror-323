import threading

def read_fd(pipe, output_queue):
    print("HELLO starting", flush=True)

stdout_thread = threading.Thread(target=read_fd, args=("",""))
stderr_thread = threading.Thread(target=read_fd, args=("",""))

stdout_thread.daemon = True
stderr_thread.daemon = True

stdout_thread.start()
stderr_thread.start()