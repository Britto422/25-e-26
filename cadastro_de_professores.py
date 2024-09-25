import tkinter as tk
from tkinter import ttk
import sqlite3

# Funções para manipulação do banco de dados
def conectar_bd():
    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cidades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS professores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        idade INTEGER NOT NULL,
                        cidade_id INTEGER,
                        FOREIGN KEY(cidade_id) REFERENCES cidades(id))''')
    conn.commit()
    return conn

def carregar_cidades():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM cidades')
    cidades = cursor.fetchall()
    for cidade in cidades:
        combobox_cidades['values'] = (*combobox_cidades['values'], cidade[1])
    conn.close()

def inserir_professor(nome, idade, cidade):
    conn = conectar_bd()
    cursor = conn.cursor()
    # Buscar ID da cidade selecionada
    cursor.execute('SELECT id FROM cidades WHERE nome = ?', (cidade,))
    cidade_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO professores (nome, idade, cidade_id) VALUES (?, ?, ?)', (nome, idade, cidade_id))
    conn.commit()
    conn.close()
    atualizar_treeview()

def atualizar_treeview():
    for row in tree.get_children():
        tree.delete(row)
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''SELECT professores.id, professores.nome, professores.idade, cidades.nome 
                      FROM professores 
                      JOIN cidades ON professores.cidade_id = cidades.id''')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()

def preencher_formulario(event):
    item_selecionado = tree.selection()[0]
    valores = tree.item(item_selecionado, 'values')
    entry_nome.delete(0, tk.END)
    entry_nome.insert(0, valores[1])
    entry_idade.delete(0, tk.END)
    entry_idade.insert(0, valores[2])
    combobox_cidades.set(valores[3])

# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Cadastro de Professores")

# Campos de formulário
tk.Label(root, text="Nome do Professor").grid(row=0, column=0)
entry_nome = tk.Entry(root)
entry_nome.grid(row=0, column=1)

tk.Label(root, text="Idade").grid(row=1, column=0)
entry_idade = tk.Entry(root)
entry_idade.grid(row=1, column=1)

tk.Label(root, text="Cidade").grid(row=2, column=0)
combobox_cidades = ttk.Combobox(root)
combobox_cidades.grid(row=2, column=1)

# TreeView para exibir os professores
tree = ttk.Treeview(root, columns=('ID', 'Nome', 'Idade', 'Cidade'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Nome', text='Nome')
tree.heading('Idade', text='Idade')
tree.heading('Cidade', text='Cidade')
tree.grid(row=3, column=0, columnspan=2)

tree.bind("<ButtonRelease-1>", preencher_formulario)

# Botões
tk.Button(root, text="Incluir", command=lambda: inserir_professor(entry_nome.get(), entry_idade.get(), combobox_cidades.get())).grid(row=4, column=0)
tk.Button(root, text="Alterar").grid(row=4, column=1)
tk.Button(root, text="Excluir").grid(row=4, column=2)

# Carregar cidades e atualizar a lista de professores
carregar_cidades()
atualizar_treeview()

root.mainloop()
