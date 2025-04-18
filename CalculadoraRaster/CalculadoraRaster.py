import rasterio
import numpy as np
import tkinter as tk
import os
from tkinter import filedialog, messagebox

# Função para ler um raster

def ler_raster(caminho):
    with rasterio.open(caminho) as src:
        dados = src.read(1)  # Lê a primeira banda
        perfil = src.profile
    return dados, perfil

# Função para normalizar os dados entre 0-255

def normalizar(matriz):
    minimo = np.min(matriz)
    maximo = np.max(matriz)
    if maximo - minimo == 0:
        return np.zeros_like(matriz)
    return ((matriz - minimo) / (maximo - minimo)) * 255

# Função para salvar um raster

def salvar_raster(dados, perfil, saida):
    perfil.update(
        dtype=rasterio.uint8,
        count=1,
        compress='lzw'
    )
    with rasterio.open(saida, 'w', **perfil) as dst:
        dst.write(dados.astype(rasterio.uint8), 1)

# Função principal para calcular a operação escolhida

def calcular(arquivos, operacao, saida):
    arrays = []
    perfil_ref = None

    for caminho in arquivos:
        dados, perfil = ler_raster(caminho)
        arrays.append(dados)
        if not perfil_ref:
            perfil_ref = perfil

    if operacao == 'soma':
        resultado = np.sum(arrays, axis=0)
    elif operacao == 'subtracao':
        resultado = arrays[0]
        for arr in arrays[1:]:
            resultado -= arr
    elif operacao == 'media':
        resultado = np.mean(arrays, axis=0)
    elif operacao == 'divisao':
        resultado = arrays[0]
        for arr in arrays[1:]:
            with np.errstate(divide='ignore', invalid='ignore'):
                resultado = np.true_divide(resultado, arr)
                resultado[arr == 0] = 0
    else:
        raise ValueError("Operação inválida.")

    resultado_normalizado = normalizar(resultado)
    salvar_raster(resultado_normalizado, perfil_ref, saida)
    messagebox.showinfo("Operação concluida com sucesso", f"Arquivo salvo em:\n{saida}")

# Interface gráfica com opção de reordenar arquivos

def abrir_interface():
    def escolher_arquivos():
        arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos TIF", "*.tif *.tiff")])
        for arquivo in arquivos:
            lista_arquivos.insert(tk.END, arquivo)

    def escolher_saida():
        caminho = filedialog.asksaveasfilename(defaultextension=".tif", filetypes=[("GeoTIFF", "*.tif")])
        entrada_saida.delete(0, tk.END)
        entrada_saida.insert(0, caminho)

    def mover_para_cima():
        selecionado = lista_arquivos.curselection()
        if selecionado and selecionado[0] > 0:
            idx = selecionado[0]
            texto = lista_arquivos.get(idx)
            lista_arquivos.delete(idx)
            lista_arquivos.insert(idx - 1, texto)
            lista_arquivos.select_set(idx - 1)

    def mover_para_baixo():
        selecionado = lista_arquivos.curselection()
        if selecionado and selecionado[0] < lista_arquivos.size() - 1:
            idx = selecionado[0]
            texto = lista_arquivos.get(idx)
            lista_arquivos.delete(idx)
            lista_arquivos.insert(idx + 1, texto)
            lista_arquivos.select_set(idx + 1)

    def executar():
        arquivos = lista_arquivos.get(0, tk.END)
        operacao = var_operacao.get()
        saida = entrada_saida.get()

        if not arquivos or not saida:
            messagebox.showwarning("Atenção", "Selecione os arquivos e defina o caminho de saída.")
            return

        try:
            calcular(arquivos, operacao, saida)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    root = tk.Tk()
    root.title("Calculadora Raster")

    try:
        caminho_icone = os.path.join(os.path.dirname(__file__), "Icon.ico")
        root.iconbitmap(caminho_icone)
    except:
        pass

    tk.Button(root, text="Selecionar arquivos .tif", command=escolher_arquivos).pack(anchor='w', pady=10, padx=10)

    frame_lista = tk.Frame(root)
    frame_lista.pack(pady=5)

    lista_arquivos = tk.Listbox(frame_lista, width=80, height=6)
    lista_arquivos.grid(row=0, column=0, rowspan=2)

    tk.Button(frame_lista, text="↑", command=mover_para_cima, width=3).grid(row=0, column=1, padx=5)
    tk.Button(frame_lista, text="↓", command=mover_para_baixo, width=3).grid(row=1, column=1, padx=5)

    tk.Label(root, text="Escolha a operação (ordem dos arquivos será respeitada):").pack(anchor='w', padx=10)
    var_operacao = tk.StringVar(value="soma")
    for op in ["soma", "subtracao", "media", "divisao"]:
        tk.Radiobutton(root, text=op.capitalize(), variable=var_operacao, value=op).pack(anchor='w', padx=10)

    tk.Label(root, text="Salvar como:").pack(anchor='w', padx=10, pady=10)
    entrada_saida = tk.Entry(root, width=60)
    entrada_saida.pack(pady=5)
    tk.Button(root, text="Escolher local", command=escolher_saida).pack()

    tk.Button(root, text="Executar operação", command=executar).pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    abrir_interface()
