import socket
import tkinter as tk
import tkinter.scrolledtext as st
import json

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

print(f"Starting gameserver on port {UDP_PORT}")

root = tk.Tk()
root.title("Server")
root.geometry('400x200')
addr = None
addresses = []
# Function to display input


def show_input():
    global addr
    text = txt.get('1.0', 'end-1c')
    sock.sendto(text.encode("utf-8"), addr)
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

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)


def update():
    global addr
    try:
        raw_data, addr = sock.recvfrom(1024)
        print("received message: %s" % raw_data)
        data : dict = json.loads(raw_data.decode("utf-8"))
        print(type(data))
        text_area.configure(state=tk.NORMAL)
        text_area.insert(tk.END, f"<- {json.loads(raw_data.decode())}\n")
        text_area.configure(state=tk.DISABLED)
        
        if data.get("init"):
            init_dict = {
                "init_success": True
            }
            sock.sendto(json.dumps(init_dict).encode("utf-8"), addr)
        
        if addr not in addresses:
            addresses.append(addr)
            
        addresses.append(addr)
    except BlockingIOError:
        pass                      # žádná data, nic se neděje
    root.after(10, update)


update()
root.mainloop()
