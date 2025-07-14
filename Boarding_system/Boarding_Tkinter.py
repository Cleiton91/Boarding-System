# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 15:11:46 2025

@author: cleit
"""

# INTERFACE FILE (TKINTER)   

import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests

#-------ENDPOINT DA API -----
API_URL = "http://127.0.0.1:8000/passengers"

# ----- FUNÇÃO PARA REGISTRAR  -----
def register_passenger():
    nome = entry_nome.get().strip()
    voo = entry_voo.get().strip()
    origem = entry_origem.get().strip()
    destino = entry_destino.get().strip()
    assento = entry_assento.get().strip()

    if not all([nome, voo, origem, destino, assento]):
        messagebox.showerror("Error", "fill in all fields.")
        return

    response = requests.post(API_URL, json={
        "NAME": nome,
        "FLIGHT": voo,
        "ORIGIN": origem,
        "DESTINATION": destino,
        "SEAT": assento
    })

    if response.status_code == 200:
        messagebox.showinfo("Success", "Passenger registered successfully!")
        for e in entries:
            e.delete(0, tk.END)
        list_passengers()
    else:
        messagebox.showerror("Error", response.json().get("detail", "Error registering passenger."))

def do_checkin():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Aviso", "Select a passenger.")
        return
    
    passenger_id = tree.item(selected)['values'][0]
    response = requests.post(f"{API_URL}/{passenger_id}/checkin")
    
    if response.status_code == 200:
        messagebox.showinfo("Success", "Check-in completed!")
        list_passengers()
    else:
        messagebox.showerror("Error", response.json().get("detail", "Check-in error."))

# ----- FUNÇÃO PARA LISTAR
def list_passengers():
    for item in tree.get_children():
        tree.delete(item)

    response = requests.get(API_URL)
    if response.status_code == 200:
        passengers = response.json()
        for p in passengers:
            tree.insert("", tk.END, values=(
                p.get("id"),
                p.get("NAME"),
                p.get("FLIGHT"),
                p.get("ORIGIN"),
                p.get("DESTINATION"),
                p.get("SEAT"),
                "YES✅" if p.get("CHECKIN_STATUS") == 1 else "NO❎"
            ))

# JANELA PRINCIPAL
root = tk.Tk()
root.title("BOARDING SYSTEM")
root.state('zoomed')    

# IMAGEM DE FUNDO
current_dir = os.path.dirname(__file__)
image_path = os.path.join(current_dir, "image", "aeroporto.jpg")

# ----- IMAGEM DE FUNDO -----
bg_image = Image.open(image_path)
bg_image = bg_image.resize((1000, 600), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

try:
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((1500, 900), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
except:
    canvas = tk.Canvas(root, width=800, height=600, bg='#0078D7')
    canvas.pack(fill="both", expand=True)

# CAMPOS DE ENTRADA
labels = ["NAME:", "FLIGHT:", "ORIGIN:", "DESTINATION:", "SEAT:"]
entries = []

for i, label in enumerate(labels):
    canvas.create_text(200, 35 + i*40, text=label, anchor="w", font=("Arial", 13, "bold"), fill="white")
    entry = tk.Entry(root, width=108,bd=5)  
    entry.pack(padx=10, pady=10)
    canvas.create_window(380, 20 + i*40, anchor="nw", window=entry)
    entries.append(entry)

entry_nome, entry_voo, entry_origem, entry_destino, entry_assento = entries

# BOTÃO REGISTRAR
register_btn = tk.Button(root, text="REGISTER", command=register_passenger)
canvas.create_window(380, 220, anchor="nw", window=register_btn)

#BOTÃO CHECKIN
checkin_btn = tk.Button(root, text="CHECK-IN", command=do_checkin)
canvas.create_window(480,220, anchor="nw", window=checkin_btn)

# TABELA
columns = ("ID", "NAME", "FLIGHT", "ORIGIN", "DESTINATION", "SEAT", "CHECK-IN")
tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)

canvas.create_window(200, 260, anchor="nw", window=tree)

# CARREGAR DADOS
list_passengers()

# ----- EVITA ERRO DE IMAGEM AO VIVO -----
root.bg_photo = bg_photo

# ----- EXECUTAR A INTERFACE -----
root.mainloop()