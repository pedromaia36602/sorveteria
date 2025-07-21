import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta
from sorveteria_backend import SorveteriaBackend

# Configuração da interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SorveteriaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Sorveteria do Marcos")
        self.geometry("1000x700")
        self.resizable(False, False)
        
        # Inicializa o backend SQLite
        self.backend = SorveteriaBackend()

        # Menu lateral
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="🍦 Sorveteria do Marcos", font=("Arial", 18, "bold"))
        self.logo_label.pack(pady=30)

        self.btn_painel = ctk.CTkButton(self.sidebar, text="Painel", command=self.abrir_painel)
        self.btn_painel.pack(pady=10, fill="x", padx=10)

        self.btn_vendas = ctk.CTkButton(self.sidebar, text="Vendas", command=self.abrir_vendas)
        self.btn_vendas.pack(pady=10, fill="x", padx=10)

        self.btn_produtos = ctk.CTkButton(self.sidebar, text="Produtos", command=self.abrir_produtos)
        self.btn_produtos.pack(pady=10, fill="x", padx=10)

        self.btn_promocoes = ctk.CTkButton(self.sidebar, text="Promoções", command=self.abrir_promocoes)
        self.btn_promocoes.pack(pady=10, fill="x", padx=10)

        self.btn_despesas = ctk.CTkButton(self.sidebar, text="Despesas", command=self.abrir_despesas)
        self.btn_despesas.pack(pady=10, fill="x", padx=10)

        self.btn_estoque = ctk.CTkButton(self.sidebar, text="Estoque", command=self.abrir_estoque)
        self.btn_estoque.pack(pady=10, fill="x", padx=10)

        # Área principal
        self.frame_principal = ctk.CTkFrame(self)
        self.frame_principal.pack(expand=True, fill="both")

        self.abrir_painel()

    def limpar_frame(self):
        for w in self.frame_principal.winfo_children():
            w.destroy()

    ### PAINEL - Resumo ###
    def abrir_painel(self):
        self.limpar_frame()

        titulo = ctk.CTkLabel(self.frame_principal, text="Painel Resumo", font=("Arial", 22, "bold"))
        titulo.pack(pady=20)

        resumo = self.backend.calcular_resumo()

        # Frame para os resumos
        frame_resumos = ctk.CTkFrame(self.frame_principal)
        frame_resumos.pack(pady=10, padx=10, fill="x")

        # Resumo Diário
        frame_diario = ctk.CTkFrame(frame_resumos)
        frame_diario.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(frame_diario, text="HOJE", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(frame_diario, text=f"R$ {resumo['vendas_hoje']:.2f}", font=("Arial", 18)).pack(pady=5)

        # Resumo Semanal
        frame_semanal = ctk.CTkFrame(frame_resumos)
        frame_semanal.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(frame_semanal, text="ESTA SEMANA", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(frame_semanal, text=f"R$ {resumo['vendas_semana']:.2f}", font=("Arial", 18)).pack(pady=5)

        # Resumo Mensal
        frame_mensal = ctk.CTkFrame(frame_resumos)
        frame_mensal.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(frame_mensal, text="ESTE MÊS", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(frame_mensal, text=f"R$ {resumo['vendas_mes']:.2f}", font=("Arial", 18)).pack(pady=5)

        frame_resumos.grid_columnconfigure(0, weight=1)
        frame_resumos.grid_columnconfigure(1, weight=1)
        frame_resumos.grid_columnconfigure(2, weight=1)

        # Resumo Geral
        frame_geral = ctk.CTkFrame(self.frame_principal)
        frame_geral.pack(pady=20, padx=10, fill="x")

        ctk.CTkLabel(frame_geral, text="Resumo Geral", font=("Arial", 16, "bold")).pack(pady=10)

        lbl_vendas = ctk.CTkLabel(frame_geral, text=f"Total Vendas (todas): R$ {resumo['total_vendas']:.2f}", font=("Arial", 14))
        lbl_vendas.pack(pady=5)

        lbl_despesas = ctk.CTkLabel(frame_geral, text=f"Total Despesas: R$ {resumo['total_despesas']:.2f}", font=("Arial", 14))
        lbl_despesas.pack(pady=5)

        lbl_lucro = ctk.CTkLabel(frame_geral, text=f"Lucro Total: R$ {resumo['lucro']:.2f}", font=("Arial", 14))
        lbl_lucro.pack(pady=5)

    ### VENDAS ###
    def abrir_vendas(self):
        self.limpar_frame()
        titulo = ctk.CTkLabel(self.frame_principal, text="Vendas", font=("Arial", 22, "bold"))
        titulo.pack(pady=10)

        # Frame para criar nova venda
        frame_nova_venda = ctk.CTkFrame(self.frame_principal)
        frame_nova_venda.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_nova_venda, text="Criar nova venda", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=6, pady=5)

        # Combobox para selecionar produto por nome
        ctk.CTkLabel(frame_nova_venda, text="Selecione o Produto:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        
        produtos = self.backend.listar_produtos()
        nomes_produtos = [f"{p['codigo']} - {p['nome']}" for p in produtos]
        
        self.combo_produtos = ctk.CTkComboBox(frame_nova_venda, values=nomes_produtos)
        self.combo_produtos.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(frame_nova_venda, text="Quantidade:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entrada_quantidade_venda = ctk.CTkEntry(frame_nova_venda)
        self.entrada_quantidade_venda.grid(row=1, column=3, padx=5, pady=5)

        btn_adicionar = ctk.CTkButton(frame_nova_venda, text="Adicionar Venda", command=self.adicionar_venda)
        btn_adicionar.grid(row=2, column=0, columnspan=6, pady=10)

        # Ajustar colunas
        frame_nova_venda.grid_columnconfigure(1, weight=1)
        frame_nova_venda.grid_columnconfigure(3, weight=1)

        # Frame listando vendas abertas
        ctk.CTkLabel(self.frame_principal, text="Vendas em andamento", font=("Arial", 18, "bold")).pack(pady=10)

        self.frame_vendas_abertas = ctk.CTkScrollableFrame(self.frame_principal, height=180)
        self.frame_vendas_abertas.pack(padx=10, fill="x")

        self.atualizar_lista_vendas_abertas()

        # Frame histórico vendas finalizadas
        ctk.CTkLabel(self.frame_principal, text="Histórico de vendas finalizadas", font=("Arial", 18, "bold")).pack(pady=10)

        self.frame_vendas_finalizadas = ctk.CTkScrollableFrame(self.frame_principal, height=150)
        self.frame_vendas_finalizadas.pack(padx=10, fill="x")

        self.atualizar_lista_vendas_finalizadas()

    def adicionar_venda(self):
        produto_selecionado = self.combo_produtos.get()
        quantidade = self.entrada_quantidade_venda.get().strip()

        if not produto_selecionado or not quantidade:
            messagebox.showerror("Erro", "Selecione um produto e informe a quantidade!")
            return

        try:
            quantidade = float(quantidade)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida!")
            return

        # Extrair ID do produto da seleção (formato "ID - Nome")
        produto_id = produto_selecionado.split(" - ")[0]
        
        produtos = self.backend.listar_produtos()
        produto = next((p for p in produtos if str(p['codigo']) == produto_id), None)
        
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado!")
            return

        if quantidade > produto['quantidade']:
            messagebox.showerror("Erro", f"Estoque insuficiente! Atual: {produto['quantidade']}")
            return

        venda_id, erro = self.backend.criar_venda(
            produto_id=produto['codigo'],
            produto_nome=produto['nome'],
            quantidade=quantidade,
            preco_unitario=produto['preco']
        )

        if erro:
            messagebox.showerror("Erro", erro)
        else:
            messagebox.showinfo("Sucesso", f"Venda {venda_id} registrada!")
            self.abrir_vendas()

    def atualizar_lista_vendas_abertas(self):
        for w in self.frame_vendas_abertas.winfo_children():
            w.destroy()

        vendas_abertas = self.backend.listar_vendas(status='aberta')

        for venda in vendas_abertas:
            frame = ctk.CTkFrame(self.frame_vendas_abertas)
            frame.pack(fill="x", pady=2, padx=2)

            info = f"ID: {venda['codigo']} | Produto: {venda['produto_nome']} | Qtde: {venda['quantidade']} | Total: R$ {venda['valor_total']:.2f} | Data: {venda['data']} {venda['hora']}"
            lbl = ctk.CTkLabel(frame, text=info)
            lbl.pack(side="left", padx=5)

            btn_finalizar = ctk.CTkButton(frame, text="Finalizar", width=100, command=lambda vid=venda['codigo']: self.finalizar_venda(vid))
            btn_finalizar.pack(side="right", padx=5)

    def finalizar_venda(self, id_venda):
        if self.backend.finalizar_venda(id_venda):
            self.atualizar_lista_vendas_abertas()
            self.atualizar_lista_vendas_finalizadas()
            messagebox.showinfo("Sucesso", f"Venda {id_venda} finalizada!")
        else:
            messagebox.showerror("Erro", "Não foi possível finalizar a venda")

    def atualizar_lista_vendas_finalizadas(self):
        for w in self.frame_vendas_finalizadas.winfo_children():
            w.destroy()

        vendas_finalizadas = self.backend.listar_vendas(status='finalizada')

        for venda in vendas_finalizadas:
            info = f"ID: {venda['codigo']} | Produto: {venda['produto_nome']} | Qtde: {venda['quantidade']} | Total: R$ {venda['valor_total']:.2f} | Data: {venda['data']} {venda['hora']}"
            lbl = ctk.CTkLabel(self.frame_vendas_finalizadas, text=info)
            lbl.pack(anchor="w", padx=10, pady=2)

    ### PRODUTOS ###
    def abrir_produtos(self):
        self.limpar_frame()
        titulo = ctk.CTkLabel(self.frame_principal, text="Produtos", font=("Arial", 22, "bold"))
        titulo.pack(pady=10)

        # Frame para cadastro/edição
        frame_cadastro = ctk.CTkFrame(self.frame_principal)
        frame_cadastro.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_cadastro, text="Cadastrar/Editar Produto", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=5)

        # Campos do formulário
        ctk.CTkLabel(frame_cadastro, text="Código (deixe em branco para novo):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entrada_codigo_produto = ctk.CTkEntry(frame_cadastro)
        self.entrada_codigo_produto.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(frame_cadastro, text="Nome:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entrada_nome_produto = ctk.CTkEntry(frame_cadastro)
        self.entrada_nome_produto.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(frame_cadastro, text="Preço:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entrada_preco_produto = ctk.CTkEntry(frame_cadastro)
        self.entrada_preco_produto.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(frame_cadastro, text="Quantidade em Estoque:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.entrada_quantidade_produto = ctk.CTkEntry(frame_cadastro)
        self.entrada_quantidade_produto.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Botões
        btn_carregar = ctk.CTkButton(frame_cadastro, text="Carregar", command=self.carregar_produto)
        btn_carregar.grid(row=5, column=0, pady=10, padx=5)

        btn_salvar = ctk.CTkButton(frame_cadastro, text="Salvar", command=self.salvar_produto)
        btn_salvar.grid(row=5, column=1, pady=10, padx=5)

        btn_limpar = ctk.CTkButton(frame_cadastro, text="Limpar", command=self.limpar_formulario_produto)
        btn_limpar.grid(row=5, column=2, pady=10, padx=5)

        btn_excluir = ctk.CTkButton(frame_cadastro, text="Excluir", fg_color="#d9534f", hover_color="#c9302c", command=self.excluir_produto)
        btn_excluir.grid(row=5, column=3, pady=10, padx=5)

        # Lista de produtos
        frame_lista = ctk.CTkFrame(self.frame_principal)
        frame_lista.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(frame_lista, text="Lista de Produtos", font=("Arial", 18, "bold")).pack(pady=5)

        self.lista_produtos = ctk.CTkScrollableFrame(frame_lista, height=300)
        self.lista_produtos.pack(fill="both", expand=True)

        self.atualizar_lista_produtos()

    def carregar_produto(self):
        codigo = self.entrada_codigo_produto.get().strip()
        if not codigo:
            messagebox.showerror("Erro", "Informe o código do produto!")
            return

        produto = self.backend.obter_produto_por_id(codigo)
        if produto:
            self.limpar_formulario_produto()
            self.entrada_codigo_produto.insert(0, str(produto['codigo']))
            self.entrada_nome_produto.insert(0, produto['nome'])
            self.entrada_preco_produto.insert(0, str(produto['preco']))
            self.entrada_quantidade_produto.insert(0, str(produto['quantidade']))
        else:
            messagebox.showerror("Erro", "Produto não encontrado!")

    def salvar_produto(self):
        codigo = self.entrada_codigo_produto.get().strip()
        nome = self.entrada_nome_produto.get().strip()
        preco = self.entrada_preco_produto.get().strip()
        quantidade = self.entrada_quantidade_produto.get().strip()

        if not nome or not preco or not quantidade:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        try:
            preco = float(preco)
            quantidade = int(quantidade)
            if preco <= 0 or quantidade < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser número positivo e quantidade inteiro não negativo!")
            return

        if codigo:  # Edição
            if self.backend.atualizar_produto(codigo, nome, preco, quantidade):
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
                self.atualizar_lista_produtos()
            else:
                messagebox.showerror("Erro", "Falha ao atualizar produto!")
        else:  # Cadastro novo
            novo_codigo = self.backend.criar_produto(nome, preco, quantidade)
            if novo_codigo:
                messagebox.showinfo("Sucesso", f"Produto cadastrado com código {novo_codigo}!")
                self.limpar_formulario_produto()
                self.atualizar_lista_produtos()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar produto!")

    def limpar_formulario_produto(self):
        self.entrada_codigo_produto.delete(0, 'end')
        self.entrada_nome_produto.delete(0, 'end')
        self.entrada_preco_produto.delete(0, 'end')
        self.entrada_quantidade_produto.delete(0, 'end')

    def excluir_produto(self):
        codigo = self.entrada_codigo_produto.get().strip()
        if not codigo:
            messagebox.showerror("Erro", "Nenhum produto selecionado para excluir!")
            return

        confirmacao = messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir o produto {codigo}?")
        if confirmacao:
            if self.backend.excluir_produto(codigo):
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
                self.limpar_formulario_produto()
                self.atualizar_lista_produtos()
            else:
                messagebox.showerror("Erro", "Falha ao excluir produto!")

    def atualizar_lista_produtos(self):
        for widget in self.lista_produtos.winfo_children():
            widget.destroy()

        produtos = self.backend.listar_produtos()
        for produto in produtos:
            frame = ctk.CTkFrame(self.lista_produtos)
            frame.pack(fill="x", pady=2, padx=2)

            info = f"{produto['codigo']} - {produto['nome']} | Preço: R$ {produto['preco']:.2f} | Estoque: {produto['quantidade']}"
            lbl = ctk.CTkLabel(frame, text=info)
            lbl.pack(side="left", padx=5)

            btn_editar = ctk.CTkButton(frame, text="Editar", width=80, command=lambda p=produto: self.editar_produto(p))
            btn_editar.pack(side="right", padx=5)

    def editar_produto(self, produto):
        self.limpar_formulario_produto()
        self.entrada_codigo_produto.insert(0, str(produto['codigo']))
        self.entrada_nome_produto.insert(0, produto['nome'])
        self.entrada_preco_produto.insert(0, str(produto['preco']))
        self.entrada_quantidade_produto.insert(0, str(produto['quantidade']))

    ### PROMOÇÕES ###
    def abrir_promocoes(self):
        self.limpar_frame()
        titulo = ctk.CTkLabel(self.frame_principal, text="Promoções", font=("Arial", 22, "bold"))
        titulo.pack(pady=10)

        frame_cadastro = ctk.CTkFrame(self.frame_principal)
        frame_cadastro.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_cadastro, text="Cadastrar nova promoção", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        ctk.CTkLabel(frame_cadastro, text="Descrição:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        entrada_desc = ctk.CTkEntry(frame_cadastro)
        entrada_desc.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(frame_cadastro, text="Desconto (%):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        entrada_desc_pct = ctk.CTkEntry(frame_cadastro)
        entrada_desc_pct.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(frame_cadastro, text="Data Início (AAAA-MM-DD):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        entrada_data_inicio = ctk.CTkEntry(frame_cadastro)
        entrada_data_inicio.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(frame_cadastro, text="Data Fim (AAAA-MM-DD):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        entrada_data_fim = ctk.CTkEntry(frame_cadastro)
        entrada_data_fim.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        def cadastrar_promocao():
            desc = entrada_desc.get().strip()
            pct = entrada_desc_pct.get().strip()
            dt_inicio = entrada_data_inicio.get().strip()
            dt_fim = entrada_data_fim.get().strip()
            if not desc or not pct or not dt_inicio or not dt_fim:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            try:
                pct = float(pct)
                datetime.strptime(dt_inicio, "%Y-%m-%d")
                datetime.strptime(dt_fim, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Erro", "Dados inválidos! Confira o formato das datas e do desconto.")
                return
            
            promocao_id = self.backend.criar_promocao(desc, pct, dt_inicio, dt_fim)
            if promocao_id:
                messagebox.showinfo("Sucesso", f"Promoção cadastrada com código {promocao_id}!")
                self.abrir_promocoes()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar promoção!")

        btn_cadastrar = ctk.CTkButton(frame_cadastro, text="Cadastrar Promoção", command=cadastrar_promocao)
        btn_cadastrar.grid(row=5, column=0, columnspan=2, pady=10)

        frame_lista = ctk.CTkFrame(self.frame_principal)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(frame_lista, text="Promoções Atuais", font=("Arial", 18, "bold")).pack(pady=5)

        lista_scroll = ctk.CTkScrollableFrame(frame_lista)
        lista_scroll.pack(fill="both", expand=True, pady=5)

        promocoes = self.backend.listar_promocoes()
        for p in promocoes:
            info = f"Código: {p['codigo']} | {p['descricao']} | Desconto: {p['desconto_percentual']}% | De {p['data_inicio']} até {p['data_fim']}"
            lbl = ctk.CTkLabel(lista_scroll, text=info)
            lbl.pack(anchor="w", padx=10, pady=2)

    ### DESPESAS ###
    def abrir_despesas(self):
        self.limpar_frame()
        titulo = ctk.CTkLabel(self.frame_principal, text="Despesas", font=("Arial", 22, "bold"))
        titulo.pack(pady=10)

        frame_cadastro = ctk.CTkFrame(self.frame_principal)
        frame_cadastro.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(frame_cadastro, text="Cadastrar nova despesa", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        ctk.CTkLabel(frame_cadastro, text="Descrição:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        entrada_desc = ctk.CTkEntry(frame_cadastro)
        entrada_desc.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(frame_cadastro, text="Valor:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        entrada_valor = ctk.CTkEntry(frame_cadastro)
        entrada_valor.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        def cadastrar_despesa():
            desc = entrada_desc.get().strip()
            valor = entrada_valor.get().strip()
            if not desc or not valor:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            try:
                valor = float(valor)
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            if self.backend.criar_despesa(desc, valor):
                messagebox.showinfo("Sucesso", "Despesa cadastrada!")
                self.abrir_despesas()
            else:
                messagebox.showerror("Erro", "Falha ao cadastrar despesa!")

        btn_cadastrar = ctk.CTkButton(frame_cadastro, text="Cadastrar Despesa", command=cadastrar_despesa)
        btn_cadastrar.grid(row=3, column=0, columnspan=2, pady=10)

        frame_lista = ctk.CTkFrame(self.frame_principal)
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(frame_lista, text="Despesas Registradas", font=("Arial", 18, "bold")).pack(pady=5)

        lista_scroll = ctk.CTkScrollableFrame(frame_lista)
        lista_scroll.pack(fill="both", expand=True, pady=5)

        despesas = self.backend.listar_despesas()
        for d in despesas:
            info = f"Descrição: {d['descricao']} | Valor: R$ {d['valor']:.2f} | Data: {d['data']}"
            lbl = ctk.CTkLabel(lista_scroll, text=info)
            lbl.pack(anchor="w", padx=10, pady=2)

    ### ESTOQUE ###
    def abrir_estoque(self):
        self.limpar_frame()
        titulo = ctk.CTkLabel(self.frame_principal, text="Controle de Estoque", font=("Arial", 22, "bold"))
        titulo.pack(pady=10)

        # Frame para ajuste de estoque
        frame_ajuste = ctk.CTkFrame(self.frame_principal)
        frame_ajuste.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_ajuste, text="Ajustar Estoque", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=5)

        ctk.CTkLabel(frame_ajuste, text="Produto ID:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entrada_id_produto_estoque = ctk.CTkEntry(frame_ajuste)
        self.entrada_id_produto_estoque.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_ajuste, text="Quantidade:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entrada_quantidade_estoque = ctk.CTkEntry(frame_ajuste)
        self.entrada_quantidade_estoque.grid(row=1, column=3, padx=5, pady=5)

        btn_adicionar = ctk.CTkButton(frame_ajuste, text="Adicionar", command=lambda: self.ajustar_estoque("adicionar"))
        btn_adicionar.grid(row=2, column=0, columnspan=2, pady=10, padx=5)

        btn_remover = ctk.CTkButton(frame_ajuste, text="Remover", command=lambda: self.ajustar_estoque("remover"))
        btn_remover.grid(row=2, column=2, columnspan=2, pady=10, padx=5)

        # Frame listando produtos com estoque baixo
        frame_baixo_estoque = ctk.CTkFrame(self.frame_principal)
        frame_baixo_estoque.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(frame_baixo_estoque, text="Produtos com Estoque Baixo", font=("Arial", 16, "bold")).pack(pady=5)

        self.lista_baixo_estoque = ctk.CTkScrollableFrame(frame_baixo_estoque, height=150)
        self.lista_baixo_estoque.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame listando todos os produtos
        frame_todos_produtos = ctk.CTkFrame(self.frame_principal)
        frame_todos_produtos.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(frame_todos_produtos, text="Todos os Produtos", font=("Arial", 16, "bold")).pack(pady=5)

        self.lista_todos_produtos = ctk.CTkScrollableFrame(frame_todos_produtos, height=250)
        self.lista_todos_produtos.pack(fill="both", expand=True, padx=5, pady=5)

        self.atualizar_listas_estoque()

    def ajustar_estoque(self, operacao):
        produto_id = self.entrada_id_produto_estoque.get().strip()
        quantidade = self.entrada_quantidade_estoque.get().strip()

        if not produto_id or not quantidade:
            messagebox.showerror("Erro", "Preencha o ID do produto e a quantidade!")
            return

        try:
            quantidade = float(quantidade)
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida! Deve ser um número positivo.")
            return

        if operacao == "remover":
            quantidade = -quantidade

        if self.backend.atualizar_estoque(int(produto_id), quantidade):
            messagebox.showinfo("Sucesso", f"Estoque do produto {produto_id} atualizado!")
            self.entrada_id_produto_estoque.delete(0, 'end')
            self.entrada_quantidade_estoque.delete(0, 'end')
            self.atualizar_listas_estoque()
        else:
            messagebox.showerror("Erro", "Falha ao atualizar estoque!")

    def atualizar_listas_estoque(self):
        # Limpar listas
        for widget in self.lista_baixo_estoque.winfo_children():
            widget.destroy()
        for widget in self.lista_todos_produtos.winfo_children():
            widget.destroy()

        produtos = self.backend.listar_produtos()
        
        # Listar produtos com estoque baixo (menos de 10 unidades)
        baixo_estoque = [p for p in produtos if p['quantidade'] < 10]
        
        if not baixo_estoque:
            ctk.CTkLabel(self.lista_baixo_estoque, text="Nenhum produto com estoque baixo").pack(pady=10)
        else:
            for produto in baixo_estoque:
                frame = ctk.CTkFrame(self.lista_baixo_estoque)
                frame.pack(fill="x", pady=2, padx=2)
                
                texto = f"ID: {produto['codigo']} | Nome: {produto['nome']} | Estoque: {produto['quantidade']} (estoque baixo!)"
                ctk.CTkLabel(frame, text=texto, text_color="red").pack(side="left", padx=5)

                btn_editar = ctk.CTkButton(frame, text="Editar", width=80,
                                         command=lambda p=produto: self.editar_direto_estoque(p))
                btn_editar.pack(side="right", padx=5)

        # Listar todos os produtos
        for produto in produtos:
            frame = ctk.CTkFrame(self.lista_todos_produtos)
            frame.pack(fill="x", pady=2, padx=2)
            
            texto = f"ID: {produto['codigo']} | Nome: {produto['nome']} | Preço: R$ {produto['preco']:.2f} | Estoque: {produto['quantidade']}"
            ctk.CTkLabel(frame, text=texto).pack(side="left", padx=5)

            btn_editar = ctk.CTkButton(frame, text="Editar", width=80,
                                     command=lambda p=produto: self.editar_direto_estoque(p))
            btn_editar.pack(side="right", padx=5)

    def editar_direto_estoque(self, produto):
        """Abre a tela de produtos já com os dados carregados para edição"""
        self.abrir_produtos()
        self.entrada_codigo_produto.delete(0, 'end')
        self.entrada_codigo_produto.insert(0, str(produto['codigo']))
        self.entrada_nome_produto.delete(0, 'end')
        self.entrada_nome_produto.insert(0, produto['nome'])
        self.entrada_preco_produto.delete(0, 'end')
        self.entrada_preco_produto.insert(0, str(produto['preco']))
        self.entrada_quantidade_produto.delete(0, 'end')
        self.entrada_quantidade_produto.insert(0, str(produto['quantidade']))


if __name__ == "__main__":
    app = SorveteriaApp()
    app.mainloop()