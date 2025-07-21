import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional

class SorveteriaBackend:
    def __init__(self, db_name='sorveteria.db'):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row  # Para retornar dicionários
        self.criar_tabelas()
    
    def criar_tabelas(self):
        cursor = self.conn.cursor()
        
        # Tabela Produto
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Produto (
            codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL
        )
        """)
        
        # Tabela Estoque
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Estoque (
            codigo_produto INTEGER PRIMARY KEY,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY (codigo_produto) REFERENCES Produto(codigo)
        )
        """)
        
        # Tabela Promocao
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Promocao (
            codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            desconto_percentual REAL NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL
        )
        """)
        
        # Tabela Venda
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Venda (
            codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_produto INTEGER NOT NULL,
            produto_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            valor_total REAL NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('aberta', 'finalizada')),
            codigo_promocao INTEGER,
            FOREIGN KEY (codigo_produto) REFERENCES Produto(codigo),
            FOREIGN KEY (codigo_promocao) REFERENCES Promocao(codigo)
        )
        """)
        
        # Tabela Despesa
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Despesa (
            codigo INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL
        )
        """)
        
        self.conn.commit()
    
    def __del__(self):
        self.conn.close()
    
    # Métodos para Produtos
    def criar_produto(self, nome: str, preco: float, quantidade: int) -> Optional[int]:
        """Cria um novo produto e seu registro de estoque"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Produto (nome, preco) VALUES (?, ?)", (nome, preco))
            produto_id = cursor.lastrowid
            cursor.execute("INSERT INTO Estoque (codigo_produto, quantidade) VALUES (?, ?)", 
                         (produto_id, quantidade))
            self.conn.commit()
            return produto_id
        except sqlite3.Error as e:
            print(f"Erro ao criar produto: {e}")
            self.conn.rollback()
            return None
    
    def obter_produto_por_id(self, produto_id: int) -> Optional[Dict]:
        """Obtém um produto específico pelo seu código"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT p.codigo, p.nome, p.preco, e.quantidade 
                FROM Produto p
                JOIN Estoque e ON p.codigo = e.codigo_produto
                WHERE p.codigo = ?
            """, (produto_id,))
            produto = cursor.fetchone()
            return dict(produto) if produto else None
        except sqlite3.Error as e:
            print(f"Erro ao obter produto: {e}")
            return None
    
    def listar_produtos(self) -> List[Dict]:
        """Lista todos os produtos com suas quantidades em estoque"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT p.codigo, p.nome, p.preco, e.quantidade 
                FROM Produto p
                JOIN Estoque e ON p.codigo = e.codigo_produto
                ORDER BY p.nome
            """)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao listar produtos: {e}")
            return []
    
    def atualizar_produto(self, codigo: int, nome: str, preco: float, quantidade: int) -> bool:
        """Atualiza os dados de um produto e seu estoque"""
        try:
            cursor = self.conn.cursor()
            
            # Atualiza produto
            cursor.execute("""
                UPDATE Produto 
                SET nome = ?, preco = ? 
                WHERE codigo = ?
            """, (nome, preco, codigo))
            
            # Atualiza estoque
            cursor.execute("""
                UPDATE Estoque 
                SET quantidade = ? 
                WHERE codigo_produto = ?
            """, (quantidade, codigo))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto: {e}")
            self.conn.rollback()
            return False
    
    def excluir_produto(self, codigo: int) -> bool:
        """Remove um produto e seu registro de estoque"""
        try:
            cursor = self.conn.cursor()
            
            # Verifica se há vendas associadas ao produto
            cursor.execute("SELECT COUNT(*) FROM Venda WHERE codigo_produto = ?", (codigo,))
            if cursor.fetchone()[0] > 0:
                return False  # Não permite excluir produtos com vendas registradas
            
            # Remove o estoque primeiro por causa da constraint de chave estrangeira
            cursor.execute("DELETE FROM Estoque WHERE codigo_produto = ?", (codigo,))
            
            # Remove o produto
            cursor.execute("DELETE FROM Produto WHERE codigo = ?", (codigo,))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao excluir produto: {e}")
            self.conn.rollback()
            return False
    
    def atualizar_estoque(self, produto_id: int, quantidade_alterar: int) -> bool:
        """Atualiza a quantidade em estoque de um produto"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE Estoque 
                SET quantidade = quantidade + ? 
                WHERE codigo_produto = ?
            """, (quantidade_alterar, produto_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar estoque: {e}")
            self.conn.rollback()
            return False
    
    # Métodos para Vendas
    def criar_venda(self, produto_id: int, produto_nome: str, quantidade: int, 
                   preco_unitario: float, codigo_promocao: Optional[int] = None) -> tuple:
        """Cria uma nova venda e atualiza o estoque"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar estoque
            cursor.execute("SELECT quantidade FROM Estoque WHERE codigo_produto = ?", (produto_id,))
            estoque = cursor.fetchone()
            
            if not estoque or estoque['quantidade'] < quantidade:
                return None, "Estoque insuficiente"
            
            # Calcular total
            total = quantidade * preco_unitario
            
            # Inserir venda
            cursor.execute("""
                INSERT INTO Venda (
                    codigo_produto, produto_nome, quantidade, preco_unitario, 
                    valor_total, data, hora, status, codigo_promocao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                produto_id, produto_nome, quantidade, preco_unitario,
                total, datetime.now().strftime("%Y-%m-%d"), 
                datetime.now().strftime("%H:%M:%S"), 'aberta', codigo_promocao
            ))
            
            # Atualizar estoque
            cursor.execute("""
                UPDATE Estoque 
                SET quantidade = quantidade - ? 
                WHERE codigo_produto = ?
            """, (quantidade, produto_id))
            
            venda_id = cursor.lastrowid
            self.conn.commit()
            return venda_id, None
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Erro ao criar venda: {e}")
            return None, str(e)
    
    def finalizar_venda(self, venda_id: int) -> bool:
        """Marca uma venda como finalizada"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE Venda 
                SET status = 'finalizada' 
                WHERE codigo = ?
            """, (venda_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Erro ao finalizar venda: {e}")
            return False
    
    def listar_vendas(self, status: Optional[str] = None) -> List[Dict]:
        """Lista vendas, opcionalmente filtrando por status"""
        try:
            cursor = self.conn.cursor()
            
            if status:
                cursor.execute("""
                    SELECT * FROM Venda 
                    WHERE status = ? 
                    ORDER BY data DESC, hora DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT * FROM Venda 
                    ORDER BY data DESC, hora DESC
                """)
                
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao listar vendas: {e}")
            return []
    
    # Métodos para Promoções
    def criar_promocao(self, descricao: str, desconto_percentual: float, 
                      data_inicio: str, data_fim: str) -> Optional[int]:
        """Cria uma nova promoção"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Promocao 
                (descricao, desconto_percentual, data_inicio, data_fim)
                VALUES (?, ?, ?, ?)
            """, (descricao, desconto_percentual, data_inicio, data_fim))
            
            promocao_id = cursor.lastrowid
            self.conn.commit()
            return promocao_id
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Erro ao criar promoção: {e}")
            return None
    
    def listar_promocoes(self) -> List[Dict]:
        """Lista todas as promoções"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM Promocao 
                ORDER BY data_inicio DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao listar promoções: {e}")
            return []
    
    # Métodos para Relatórios
    def calcular_resumo(self) -> Dict[str, float]:
        """Calcula métricas resumidas para o painel"""
        try:
            cursor = self.conn.cursor()
            
            hoje = datetime.now().strftime("%Y-%m-%d")
            inicio_semana = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
            inicio_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            
            # Total de vendas
            cursor.execute("""
                SELECT SUM(valor_total) FROM Venda 
                WHERE status = 'finalizada'
            """)
            total_vendas = cursor.fetchone()[0] or 0
            
            # Vendas hoje
            cursor.execute("""
                SELECT SUM(valor_total) FROM Venda 
                WHERE status = 'finalizada' AND data = ?
            """, (hoje,))
            vendas_hoje = cursor.fetchone()[0] or 0
            
            # Vendas semana
            cursor.execute("""
                SELECT SUM(valor_total) FROM Venda 
                WHERE status = 'finalizada' AND data >= ?
            """, (inicio_semana,))
            vendas_semana = cursor.fetchone()[0] or 0
            
            # Vendas mês
            cursor.execute("""
                SELECT SUM(valor_total) FROM Venda 
                WHERE status = 'finalizada' AND data >= ?
            """, (inicio_mes,))
            vendas_mes = cursor.fetchone()[0] or 0
            
            # Despesas
            cursor.execute("SELECT SUM(valor) FROM Despesa")
            total_despesas = cursor.fetchone()[0] or 0
            
            # Lucro
            lucro = total_vendas - total_despesas
            
            return {
                "total_vendas": float(total_vendas),
                "total_despesas": float(total_despesas),
                "lucro": float(lucro),
                "vendas_hoje": float(vendas_hoje),
                "vendas_semana": float(vendas_semana),
                "vendas_mes": float(vendas_mes)
            }
        except sqlite3.Error as e:
            print(f"Erro ao calcular resumo: {e}")
            return {
                "total_vendas": 0.0,
                "total_despesas": 0.0,
                "lucro": 0.0,
                "vendas_hoje": 0.0,
                "vendas_semana": 0.0,
                "vendas_mes": 0.0
            }
    
    # Métodos para Despesas
    def criar_despesa(self, descricao: str, valor: float) -> bool:
        """Registra uma nova despesa"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Despesa 
                (descricao, valor, data) 
                VALUES (?, ?, ?)
            """, (descricao, valor, datetime.now().strftime("%Y-%m-%d")))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Erro ao criar despesa: {e}")
            return False
    
    def listar_despesas(self) -> List[Dict]:
        """Lista todas as despesas"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM Despesa 
                ORDER BY data DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao listar despesas: {e}")
            return []