import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox


# Funções para manipulação do banco de dados
def conectar_bd():
    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cidades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS alunos (
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
    cursor.execute('SELECT nome FROM cidades')
    cidades = cursor.fetchall()
    combobox_cidades['values'] = [cidade[0] for cidade in cidades]
    conn.close()


def inserir_aluno(nome, idade, cidade):
    if not nome or not idade or not cidade:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM cidades WHERE nome = ?', (cidade,))
    cidade_id = cursor.fetchone()

    if cidade_id:
        cidade_id = cidade_id[0]
        cursor.execute('INSERT INTO alunos (nome, idade, cidade_id) VALUES (?, ?, ?)', (nome, idade, cidade_id))
        conn.commit()
        conn.close()
        atualizar_treeview()
        limpar_formulario()
    else:
        messagebox.showerror("Erro", "Cidade não encontrada.")


def atualizar_treeview():
    for row in tree.get_children():
        tree.delete(row)
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''SELECT alunos.id, alunos.nome, alunos.idade, cidades.nome 
                      FROM alunos 
                      JOIN cidades ON alunos.cidade_id = cidades.id''')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()


def preencher_formulario(event):
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, valores[1])
        entry_idade.delete(0, tk.END)
        entry_idade.insert(0, valores[2])
        combobox_cidades.set(valores[3])
    except IndexError:
        pass


def alterar_aluno():
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        aluno_id = valores[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM cidades WHERE nome = ?', (combobox_cidades.get(),))
        cidade_id = cursor.fetchone()

        if cidade_id:
            cidade_id = cidade_id[0]
            cursor.execute('UPDATE alunos SET nome = ?, idade = ?, cidade_id = ? WHERE id = ?',
                           (entry_nome.get(), entry_idade.get(), cidade_id, aluno_id))
            conn.commit()
            conn.close()
            atualizar_treeview()
            limpar_formulario()
        else:
            messagebox.showerror("Erro", "Cidade não encontrada.")
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione um aluno para alterar.")


def excluir_aluno():
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        aluno_id = valores[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
        conn.commit()
        conn.close()
        atualizar_treeview()
        limpar_formulario()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione um aluno para excluir.")


def limpar_formulario():
    entry_nome.delete(0, tk.END)
    entry_idade.delete(0, tk.END)
    combobox_cidades.set('')


# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Cadastro de Alunos")

# Campos de formulário
tk.Label(root, text="Nome do Aluno").grid(row=0, column=0)
entry_nome = tk.Entry(root)
entry_nome.grid(row=0, column=1)

tk.Label(root, text="Idade").grid(row=1, column=0)
entry_idade = tk.Entry(root)
entry_idade.grid(row=1, column=1)

tk.Label(root, text="Cidade").grid(row=2, column=0)
combobox_cidades = ttk.Combobox(root)
combobox_cidades.grid(row=2, column=1)

# TreeView para exibir os alunos
tree = ttk.Treeview(root, columns=('ID', 'Nome', 'Idade', 'Cidade'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Nome', text='Nome')
tree.heading('Idade', text='Idade')
tree.heading('Cidade', text='Cidade')
tree.grid(row=3, column=0, columnspan=3)

tree.bind("<ButtonRelease-1>", preencher_formulario)

# Botões
tk.Button(root, text="Incluir",
          command=lambda: inserir_aluno(entry_nome.get(), entry_idade.get(), combobox_cidades.get())).grid(row=4,
                                                                                                           column=0)
tk.Button(root, text="Alterar", command=alterar_aluno).grid(row=4, column=1)
tk.Button(root, text="Excluir", command=excluir_aluno).grid(row=4, column=2)

# Carregar cidades e atualizar a lista de alunos
carregar_cidades()
atualizar_treeview()

root.mainloop()
