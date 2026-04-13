import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB = "jogo.db"




def conectar():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enigmas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT,
        resposta TEXT,
        dificuldade TEXT,
        pontos INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dicas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        enigma_id INTEGER,
        dica TEXT,
        FOREIGN KEY(enigma_id) REFERENCES enigmas(id)
    )
    """)
    conn.commit()
    return conn, cursor

def adicionar_enigma_db(pergunta, resposta, dificuldade, pontos):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT INTO enigmas (pergunta, resposta, dificuldade, pontos) VALUES (?, ?, ?, ?)",
        (pergunta, resposta, dificuldade, pontos)
    )
    conn.commit()
    conn.close()

def listar_enigmas_db():
    conn, cursor = conectar()
    cursor.execute("SELECT id, pergunta FROM enigmas")
    enigmas = cursor.fetchall()
    conn.close()
    return enigmas

def adicionar_dica_db(enigma_id, dica):
    conn, cursor = conectar()
    cursor.execute(
        "INSERT INTO dicas (enigma_id, dica) VALUES (?, ?)",
        (enigma_id, dica)
    )
    conn.commit()
    conn.close()



def adicionar_enigma():
    pergunta = entry_pergunta.get().strip()
    resposta = entry_resposta.get().strip()
    dificuldade = combo_dificuldade.get()
    pontos = entry_pontos.get().strip()

    if not pergunta or not resposta or not dificuldade or not pontos:
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return

    try:
        pontos_int = int(pontos)
    except ValueError:
        messagebox.showerror("Erro", "Pontos deve ser um número inteiro!")
        return

    adicionar_enigma_db(pergunta, resposta, dificuldade, pontos_int)
    messagebox.showinfo("Sucesso", "Enigma adicionado com sucesso!")
    entry_pergunta.delete(0, tk.END)
    entry_resposta.delete(0, tk.END)
    combo_dificuldade.set('')
    entry_pontos.delete(0, tk.END)
    atualizar_enigmas()

def adicionar_dica():
    escolha = combo_enigmas.get()
    if not escolha:
        messagebox.showwarning("Aviso", "Selecione um enigma!")
        return
    dica = entry_dica.get().strip()
    if not dica:
        messagebox.showwarning("Aviso", "Digite a dica!")
        return

    enigma_id = enigmas_dict[escolha]
    adicionar_dica_db(enigma_id, dica)
    messagebox.showinfo("Sucesso", "Dica adicionada com sucesso!")
    entry_dica.delete(0, tk.END)

def atualizar_enigmas():
    global enigmas_dict
    enigmas = listar_enigmas_db()
    enigmas_dict = {f"{e[0]} - {e[1][:40]}...": e[0] for e in enigmas}
    combo_enigmas['values'] = list(enigmas_dict.keys())



root = tk.Tk()
root.title("Painel Admin - Enigmas")
root.geometry("500x500")



frame_enigma = tk.LabelFrame(root, text="Adicionar Enigma", padx=10, pady=10)
frame_enigma.pack(padx=10, pady=10, fill="both")

tk.Label(frame_enigma, text="Pergunta:").pack(anchor="w")
entry_pergunta = tk.Entry(frame_enigma, width=50)
entry_pergunta.pack()

tk.Label(frame_enigma, text="Resposta:").pack(anchor="w")
entry_resposta = tk.Entry(frame_enigma, width=50)
entry_resposta.pack()

tk.Label(frame_enigma, text="Dificuldade:").pack(anchor="w")
combo_dificuldade = ttk.Combobox(frame_enigma, values=["Fácil", "Médio", "Difícil"], state="readonly")
combo_dificuldade.pack()

tk.Label(frame_enigma, text="Pontos:").pack(anchor="w")
entry_pontos = tk.Entry(frame_enigma, width=10)
entry_pontos.pack()

tk.Button(frame_enigma, text="Adicionar Enigma", command=adicionar_enigma).pack(pady=10)

#Adicionar Dica
frame_dica = tk.LabelFrame(root, text="Adicionar Dica", padx=10, pady=10)
frame_dica.pack(padx=10, pady=10, fill="both")

tk.Label(frame_dica, text="Selecione Enigma:").pack(anchor="w")
combo_enigmas = ttk.Combobox(frame_dica, state="readonly")
combo_enigmas.pack()

tk.Label(frame_dica, text="Dica:").pack(anchor="w")
entry_dica = tk.Entry(frame_dica, width=50)
entry_dica.pack()

tk.Button(frame_dica, text="Adicionar Dica", command=adicionar_dica).pack(pady=10)

# Atualizar enigmas ao iniciar
enigmas_dict = {}
atualizar_enigmas()

root.mainloop()