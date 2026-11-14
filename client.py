import socket
import tkinter as tk
import socket
import tkinter as tk
import tkinter.scrolledtext as st

UDP_IP = "192.168.3.84"
UDP_PORT = 5005

print(f"Game client starting on port {UDP_PORT}. Connecting to IP {UDP_IP}")

root = tk.Tk()
root.title("Client")
root.geometry('400x200')

# Function to display input
def show_input():
    text = txt.get('1.0', 'end-1c')
    sock.sendto(text.encode("utf-8"), (UDP_IP, UDP_PORT))
    text_area.configure(state=tk.NORMAL)
    text_area.insert(tk.END, f"-> {text}\n")
    text_area.configure(state=tk.DISABLED)

# TextBox for input
txt = tk.Text(root, height=5, width=40)
txt.pack()

# Button to print input
btn = tk.Button(root, text="send", command=show_input)
btn.pack()

text_area = st.ScrolledText(root,
                            width=30,
                            height=8)
text_area.pack()
# Label to display input
lbl = tk.Label(root, text="")
lbl.pack()


sock = socket.socket(socket.AF_INET, # IPv4
                     socket.SOCK_DGRAM) # UDP
sock.bind(("0.0.0.0", 0))   # navaž na libovolný volný port
sock.setblocking(False)

def update():
    try:
        data, addr = sock.recvfrom(1024)
        print("received message: %s" % data)
        text_area.configure(state=tk.NORMAL)
        text_area.insert(tk.END, f"<- {data.decode()}\n")
        text_area.configure(state=tk.DISABLED)
    except BlockingIOError:
        pass                      # žádná data, nic se neděje
    root.after(10, update)


update()

root.mainloop()

