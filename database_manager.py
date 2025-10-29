"""
Sistema de Controle de Gado de Corte
Módulo de gerenciamento de banco de dados
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "controle_gado.db"):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return self.connection
    
    def disconnect(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self, schema_file: str = "database_schema.sql"):
        """
        Inicializa o banco de dados com o schema
        
        Args:
            schema_file: Caminho para o arquivo SQL com o schema
        """
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # Executa o schema
        cursor.executescript(schema_sql)
        conn.commit()
        
        print(f"✓ Banco de dados inicializado com sucesso: {self.db_path}")
        
        self.disconnect()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Executa uma query SELECT e retorna os resultados
        
        Args:
            query: Query SQL
            params: Parâmetros da query
            
        Returns:
            Lista de dicionários com os resultados
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        self.disconnect()
        return results
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """
        Executa um INSERT e retorna o ID do registro criado
        
        Args:
            query: Query SQL INSERT
            params: Parâmetros da query
            
        Returns:
            ID do registro inserido
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        last_id = cursor.lastrowid
        
        self.disconnect()
        return last_id
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Executa um UPDATE e retorna o número de linhas afetadas
        
        Args:
            query: Query SQL UPDATE
            params: Parâmetros da query
            
        Returns:
            Número de linhas afetadas
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        rows_affected = cursor.rowcount
        
        self.disconnect()
        return rows_affected
    
    def backup_database(self, backup_path: Optional[str] = None):
        """
        Cria um backup do banco de dados
        
        Args:
            backup_path: Caminho para o arquivo de backup
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_controle_gado_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"✓ Backup criado: {backup_path}")
        return backup_path


class AnimalManager:
    """Gerenciador de operações relacionadas aos animais"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def cadastrar_animal(self, dados: Dict[str, Any]) -> int:
        """
        Cadastra um novo animal no sistema
        
        Args:
            dados: Dicionário com os dados do animal
            
        Returns:
            ID do animal cadastrado
        """
        query = """
        INSERT INTO animais (
            brinco, nome, sexo, raca, data_nascimento, peso_nascimento,
            peso_atual, status, lote, pasto, pai_id, mae_id, observacoes,
            data_entrada, valor_compra, origem
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            dados.get('brinco'),
            dados.get('nome'),
            dados.get('sexo'),
            dados.get('raca'),
            dados.get('data_nascimento'),
            dados.get('peso_nascimento'),
            dados.get('peso_atual'),
            dados.get('status', 'ativo'),
            dados.get('lote'),
            dados.get('pasto'),
            dados.get('pai_id'),
            dados.get('mae_id'),
            dados.get('observacoes'),
            dados.get('data_entrada', datetime.now().strftime('%Y-%m-%d')),
            dados.get('valor_compra'),
            dados.get('origem')
        )
        
        animal_id = self.db.execute_insert(query, params)
        print(f"✓ Animal cadastrado com sucesso! ID: {animal_id}")
        return animal_id
    
    def buscar_animal_por_brinco(self, brinco: str) -> Optional[Dict]:
        """Busca um animal pelo número do brinco"""
        query = "SELECT * FROM animais WHERE brinco = ?"
        results = self.db.execute_query(query, (brinco,))
        return results[0] if results else None
    
    def listar_animais_ativos(self, lote: Optional[str] = None) -> List[Dict]:
        """Lista todos os animais ativos, opcionalmente filtrados por lote"""
        if lote:
            query = "SELECT * FROM vw_rebanho_ativo WHERE lote = ? ORDER BY brinco"
            return self.db.execute_query(query, (lote,))
        else:
            query = "SELECT * FROM vw_rebanho_ativo ORDER BY brinco"
            return self.db.execute_query(query)
    
    def atualizar_peso(self, animal_id: int, peso: float, data: Optional[str] = None) -> int:
        """Atualiza o peso atual do animal"""
        if not data:
            data = datetime.now().strftime('%Y-%m-%d')
        
        # Atualiza o peso na tabela de animais
        query_animal = "UPDATE animais SET peso_atual = ? WHERE id = ?"
        self.db.execute_update(query_animal, (peso, animal_id))
        
        # Registra a pesagem
        query_pesagem = """
        INSERT INTO pesagens (animal_id, data_pesagem, peso)
        VALUES (?, ?, ?)
        """
        pesagem_id = self.db.execute_insert(query_pesagem, (animal_id, data, peso))
        
        print(f"✓ Peso atualizado para {peso}kg")
        return pesagem_id


class PesagemManager:
    """Gerenciador de operações relacionadas às pesagens"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def registrar_pesagem(self, dados: Dict[str, Any]) -> int:
        """Registra uma nova pesagem"""
        query = """
        INSERT INTO pesagens (
            animal_id, data_pesagem, peso, condicao_corporal, observacoes
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            dados.get('animal_id'),
            dados.get('data_pesagem', datetime.now().strftime('%Y-%m-%d')),
            dados.get('peso'),
            dados.get('condicao_corporal'),
            dados.get('observacoes')
        )
        
        pesagem_id = self.db.execute_insert(query, params)
        
        # Atualiza peso atual do animal
        update_query = "UPDATE animais SET peso_atual = ? WHERE id = ?"
        self.db.execute_update(update_query, (dados.get('peso'), dados.get('animal_id')))
        
        print(f"✓ Pesagem registrada com sucesso! ID: {pesagem_id}")
        return pesagem_id
    
    def obter_historico_pesagens(self, animal_id: int) -> List[Dict]:
        """Obtém o histórico de pesagens de um animal"""
        query = """
        SELECT * FROM pesagens 
        WHERE animal_id = ? 
        ORDER BY data_pesagem DESC
        """
        return self.db.execute_query(query, (animal_id,))
    
    def calcular_gmd(self, animal_id: int) -> Optional[float]:
        """Calcula o Ganho Médio Diário entre a primeira e última pesagem"""
        query = """
        SELECT 
            MIN(data_pesagem) as primeira_data,
            MAX(data_pesagem) as ultima_data,
            (SELECT peso FROM pesagens WHERE animal_id = ? ORDER BY data_pesagem ASC LIMIT 1) as peso_inicial,
            (SELECT peso FROM pesagens WHERE animal_id = ? ORDER BY data_pesagem DESC LIMIT 1) as peso_final
        FROM pesagens
        WHERE animal_id = ?
        """
        
        result = self.db.execute_query(query, (animal_id, animal_id, animal_id))
        
        if result and result[0]['primeira_data'] != result[0]['ultima_data']:
            dados = result[0]
            ganho_total = dados['peso_final'] - dados['peso_inicial']
            
            # Calcula dias entre pesagens
            from datetime import datetime
            data_inicial = datetime.strptime(dados['primeira_data'], '%Y-%m-%d')
            data_final = datetime.strptime(dados['ultima_data'], '%Y-%m-%d')
            dias = (data_final - data_inicial).days
            
            if dias > 0:
                gmd = ganho_total / dias
                return round(gmd, 3)
        
        return None


class SanidadeManager:
    """Gerenciador de operações relacionadas à sanidade"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def registrar_sanidade(self, dados: Dict[str, Any]) -> int:
        """Registra um evento de sanidade (vacina, vermífugo, etc)"""
        query = """
        INSERT INTO sanidade (
            animal_id, data_aplicacao, tipo, produto, dose,
            aplicador, proxima_aplicacao, observacoes, custo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            dados.get('animal_id'),
            dados.get('data_aplicacao', datetime.now().strftime('%Y-%m-%d')),
            dados.get('tipo'),
            dados.get('produto'),
            dados.get('dose'),
            dados.get('aplicador'),
            dados.get('proxima_aplicacao'),
            dados.get('observacoes'),
            dados.get('custo')
        )
        
        sanidade_id = self.db.execute_insert(query, params)
        print(f"✓ Registro de sanidade criado! ID: {sanidade_id}")
        return sanidade_id
    
    def obter_proximas_aplicacoes(self, dias: int = 30) -> List[Dict]:
        """Lista as próximas aplicações programadas"""
        query = """
        SELECT 
            s.*,
            a.brinco,
            a.nome
        FROM sanidade s
        INNER JOIN animais a ON s.animal_id = a.id
        WHERE s.proxima_aplicacao IS NOT NULL
        AND s.proxima_aplicacao <= date('now', '+' || ? || ' days')
        AND a.status = 'ativo'
        ORDER BY s.proxima_aplicacao
        """
        return self.db.execute_query(query, (dias,))


if __name__ == "__main__":
    # Exemplo de uso
    db = DatabaseManager("controle_gado.db")
    
    # Inicializa o banco de dados
    if not os.path.exists("controle_gado.db"):
        db.initialize_database()
    
    # Exemplo de cadastro de animal
    animal_mgr = AnimalManager(db)
    
    print("\n" + "="*50)
    print("Sistema de Controle de Gado - Banco de Dados")
    print("="*50)
    print("\n✓ Sistema inicializado com sucesso!")
    print(f"✓ Banco de dados: {db.db_path}")
