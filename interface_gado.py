"""
Sistema de Controle de Gado de Corte
Interface de Entrada de Dados
"""

from database_manager import (
    DatabaseManager, AnimalManager, PesagemManager, SanidadeManager
)
from datetime import datetime
import os

class InterfaceGado:
    def __init__(self):
        self.db = DatabaseManager("controle_gado.db")
        self.animal_mgr = AnimalManager(self.db)
        self.pesagem_mgr = PesagemManager(self.db)
        self.sanidade_mgr = SanidadeManager(self.db)
        
        # Inicializa o banco se não existir
        if not os.path.exists("controle_gado.db"):
            self.db.initialize_database()
    
    def limpar_tela(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def aguardar_enter(self):
        """Aguarda o usuário pressionar Enter"""
        input("\nPressione Enter para continuar...")
    
    def mostrar_menu_principal(self):
        """Exibe o menu principal"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 15 + "CONTROLE DE GADO DE CORTE")
        print("=" * 60)
        print("\n[1] Cadastrar Novo Animal")
        print("[2] Registrar Pesagem")
        print("[3] Registrar Sanidade (Vacinas/Medicamentos)")
        print("[4] Buscar Animal")
        print("[5] Listar Animais Ativos")
        print("[6] Relatórios")
        print("[7] Backup do Banco de Dados")
        print("[0] Sair")
        print("\n" + "=" * 60)
    
    def cadastrar_animal(self):
        """Interface para cadastro de novo animal"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 18 + "CADASTRAR NOVO ANIMAL")
        print("=" * 60 + "\n")
        
        try:
            dados = {}
            
            dados['brinco'] = input("Número do Brinco (*): ").strip()
            if not dados['brinco']:
                print("❌ Número do brinco é obrigatório!")
                self.aguardar_enter()
                return
            
            # Verifica se o brinco já existe
            if self.animal_mgr.buscar_animal_por_brinco(dados['brinco']):
                print(f"❌ Já existe um animal com o brinco {dados['brinco']}!")
                self.aguardar_enter()
                return
            
            dados['nome'] = input("Nome do Animal: ").strip() or None
            
            sexo = input("Sexo (M/F) (*): ").strip().upper()
            if sexo not in ['M', 'F']:
                print("❌ Sexo inválido! Use M ou F.")
                self.aguardar_enter()
                return
            dados['sexo'] = sexo
            
            dados['raca'] = input("Raça: ").strip() or None
            
            data_nasc = input("Data de Nascimento (AAAA-MM-DD): ").strip()
            dados['data_nascimento'] = data_nasc if data_nasc else None
            
            peso_nasc = input("Peso ao Nascimento (kg): ").strip()
            dados['peso_nascimento'] = float(peso_nasc) if peso_nasc else None
            
            peso_atual = input("Peso Atual (kg) (*): ").strip()
            if not peso_atual:
                print("❌ Peso atual é obrigatório!")
                self.aguardar_enter()
                return
            dados['peso_atual'] = float(peso_atual)
            
            dados['lote'] = input("Lote: ").strip() or None
            dados['pasto'] = input("Pasto: ").strip() or None
            dados['origem'] = input("Origem/Procedência: ").strip() or None
            
            valor_compra = input("Valor de Compra (R$): ").strip()
            dados['valor_compra'] = float(valor_compra) if valor_compra else None
            
            dados['observacoes'] = input("Observações: ").strip() or None
            
            # Cadastra o animal
            animal_id = self.animal_mgr.cadastrar_animal(dados)
            
            # Registra a pesagem inicial
            pesagem_dados = {
                'animal_id': animal_id,
                'peso': dados['peso_atual'],
                'data_pesagem': datetime.now().strftime('%Y-%m-%d'),
                'observacoes': 'Pesagem inicial - cadastro'
            }
            self.pesagem_mgr.registrar_pesagem(pesagem_dados)
            
            print("\n" + "=" * 60)
            print("✓ Animal cadastrado com sucesso!")
            print(f"  ID: {animal_id}")
            print(f"  Brinco: {dados['brinco']}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Erro ao cadastrar animal: {e}")
        
        self.aguardar_enter()
    
    def registrar_pesagem(self):
        """Interface para registro de pesagem"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 20 + "REGISTRAR PESAGEM")
        print("=" * 60 + "\n")
        
        try:
            brinco = input("Número do Brinco (*): ").strip()
            if not brinco:
                print("❌ Número do brinco é obrigatório!")
                self.aguardar_enter()
                return
            
            animal = self.animal_mgr.buscar_animal_por_brinco(brinco)
            if not animal:
                print(f"❌ Animal com brinco {brinco} não encontrado!")
                self.aguardar_enter()
                return
            
            print(f"\nAnimal: {animal['nome'] or 'S/N'} - Brinco: {animal['brinco']}")
            print(f"Peso Atual: {animal['peso_atual']}kg")
            print("-" * 60)
            
            dados = {}
            dados['animal_id'] = animal['id']
            
            data = input("\nData da Pesagem (AAAA-MM-DD) [hoje]: ").strip()
            dados['data_pesagem'] = data if data else datetime.now().strftime('%Y-%m-%d')
            
            peso = input("Peso (kg) (*): ").strip()
            if not peso:
                print("❌ Peso é obrigatório!")
                self.aguardar_enter()
                return
            dados['peso'] = float(peso)
            
            cc = input("Condição Corporal (1-5): ").strip()
            dados['condicao_corporal'] = int(cc) if cc else None
            
            dados['observacoes'] = input("Observações: ").strip() or None
            
            pesagem_id = self.pesagem_mgr.registrar_pesagem(dados)
            
            # Calcula GMD
            gmd = self.pesagem_mgr.calcular_gmd(animal['id'])
            
            print("\n" + "=" * 60)
            print("✓ Pesagem registrada com sucesso!")
            print(f"  ID: {pesagem_id}")
            print(f"  Peso: {dados['peso']}kg")
            if gmd:
                print(f"  GMD (Ganho Médio Diário): {gmd}kg/dia")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Erro ao registrar pesagem: {e}")
        
        self.aguardar_enter()
    
    def registrar_sanidade(self):
        """Interface para registro de sanidade"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 18 + "REGISTRAR SANIDADE")
        print("=" * 60 + "\n")
        
        try:
            brinco = input("Número do Brinco (*): ").strip()
            if not brinco:
                print("❌ Número do brinco é obrigatório!")
                self.aguardar_enter()
                return
            
            animal = self.animal_mgr.buscar_animal_por_brinco(brinco)
            if not animal:
                print(f"❌ Animal com brinco {brinco} não encontrado!")
                self.aguardar_enter()
                return
            
            print(f"\nAnimal: {animal['nome'] or 'S/N'} - Brinco: {animal['brinco']}")
            print("-" * 60)
            
            dados = {}
            dados['animal_id'] = animal['id']
            
            print("\nTipo de Aplicação:")
            print("[1] Vacina")
            print("[2] Vermífugo")
            print("[3] Antibiótico")
            print("[4] Carrapaticida")
            print("[5] Outro")
            
            tipo_opcao = input("\nSelecione o tipo (*): ").strip()
            tipos = {
                '1': 'vacina',
                '2': 'vermifugo',
                '3': 'antibiotico',
                '4': 'carrapaticida',
                '5': 'outro'
            }
            
            if tipo_opcao not in tipos:
                print("❌ Tipo inválido!")
                self.aguardar_enter()
                return
            dados['tipo'] = tipos[tipo_opcao]
            
            dados['produto'] = input("Nome do Produto (*): ").strip()
            if not dados['produto']:
                print("❌ Nome do produto é obrigatório!")
                self.aguardar_enter()
                return
            
            dados['dose'] = input("Dose/Quantidade: ").strip() or None
            dados['aplicador'] = input("Responsável pela Aplicação: ").strip() or None
            
            data_aplic = input("Data da Aplicação (AAAA-MM-DD) [hoje]: ").strip()
            dados['data_aplicacao'] = data_aplic if data_aplic else datetime.now().strftime('%Y-%m-%d')
            
            proxima = input("Próxima Aplicação (AAAA-MM-DD): ").strip()
            dados['proxima_aplicacao'] = proxima if proxima else None
            
            custo = input("Custo (R$): ").strip()
            dados['custo'] = float(custo) if custo else None
            
            dados['observacoes'] = input("Observações: ").strip() or None
            
            sanidade_id = self.sanidade_mgr.registrar_sanidade(dados)
            
            print("\n" + "=" * 60)
            print("✓ Registro de sanidade criado com sucesso!")
            print(f"  ID: {sanidade_id}")
            print(f"  Tipo: {dados['tipo']}")
            print(f"  Produto: {dados['produto']}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Erro ao registrar sanidade: {e}")
        
        self.aguardar_enter()
    
    def buscar_animal(self):
        """Interface para buscar animal"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 22 + "BUSCAR ANIMAL")
        print("=" * 60 + "\n")
        
        brinco = input("Número do Brinco: ").strip()
        if not brinco:
            print("❌ Digite um número de brinco!")
            self.aguardar_enter()
            return
        
        animal = self.animal_mgr.buscar_animal_por_brinco(brinco)
        
        if not animal:
            print(f"\n❌ Animal com brinco {brinco} não encontrado!")
        else:
            print("\n" + "=" * 60)
            print("DADOS DO ANIMAL")
            print("=" * 60)
            print(f"ID: {animal['id']}")
            print(f"Brinco: {animal['brinco']}")
            print(f"Nome: {animal['nome'] or 'N/A'}")
            print(f"Sexo: {animal['sexo']}")
            print(f"Raça: {animal['raca'] or 'N/A'}")
            print(f"Data Nascimento: {animal['data_nascimento'] or 'N/A'}")
            print(f"Peso Atual: {animal['peso_atual']}kg")
            print(f"Status: {animal['status']}")
            print(f"Lote: {animal['lote'] or 'N/A'}")
            print(f"Pasto: {animal['pasto'] or 'N/A'}")
            
            # Busca histórico de pesagens
            pesagens = self.pesagem_mgr.obter_historico_pesagens(animal['id'])
            if pesagens:
                print(f"\nÚltimas Pesagens: {len(pesagens)}")
                for i, p in enumerate(pesagens[:3], 1):
                    print(f"  {i}. {p['data_pesagem']}: {p['peso']}kg")
            
            # Calcula GMD
            gmd = self.pesagem_mgr.calcular_gmd(animal['id'])
            if gmd:
                print(f"\nGMD (Ganho Médio Diário): {gmd}kg/dia")
            
            print("=" * 60)
        
        self.aguardar_enter()
    
    def listar_animais_ativos(self):
        """Interface para listar animais ativos"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 19 + "ANIMAIS ATIVOS")
        print("=" * 60 + "\n")
        
        lote = input("Filtrar por Lote (deixe em branco para todos): ").strip() or None
        
        animais = self.animal_mgr.listar_animais_ativos(lote)
        
        if not animais:
            print("\n❌ Nenhum animal ativo encontrado!")
        else:
            print(f"\nTotal de animais: {len(animais)}\n")
            print(f"{'Brinco':<15} {'Nome':<20} {'Sexo':<6} {'Raça':<15} {'Peso':<10} {'Lote':<10}")
            print("-" * 86)
            
            for animal in animais:
                print(f"{animal['brinco']:<15} "
                      f"{(animal['nome'] or 'N/A'):<20} "
                      f"{animal['sexo']:<6} "
                      f"{(animal['raca'] or 'N/A'):<15} "
                      f"{animal['peso_atual']:<10.2f} "
                      f"{(animal['lote'] or 'N/A'):<10}")
        
        self.aguardar_enter()
    
    def menu_relatorios(self):
        """Menu de relatórios"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 23 + "RELATÓRIOS")
        print("=" * 60 + "\n")
        print("[1] Próximas Aplicações de Sanidade")
        print("[2] Performance dos Animais (GMD)")
        print("[3] Resumo do Rebanho")
        print("[0] Voltar")
        print("\n" + "=" * 60)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            self.relatorio_proximas_aplicacoes()
        elif opcao == '2':
            self.relatorio_performance()
        elif opcao == '3':
            self.relatorio_resumo_rebanho()
    
    def relatorio_proximas_aplicacoes(self):
        """Relatório de próximas aplicações"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 15 + "PRÓXIMAS APLICAÇÕES")
        print("=" * 60 + "\n")
        
        dias = input("Próximos quantos dias? [30]: ").strip()
        dias = int(dias) if dias else 30
        
        aplicacoes = self.sanidade_mgr.obter_proximas_aplicacoes(dias)
        
        if not aplicacoes:
            print(f"\n✓ Nenhuma aplicação programada para os próximos {dias} dias!")
        else:
            print(f"\nTotal de aplicações: {len(aplicacoes)}\n")
            print(f"{'Data':<12} {'Brinco':<15} {'Nome':<20} {'Tipo':<15} {'Produto':<25}")
            print("-" * 87)
            
            for aplic in aplicacoes:
                print(f"{aplic['proxima_aplicacao']:<12} "
                      f"{aplic['brinco']:<15} "
                      f"{(aplic['nome'] or 'N/A'):<20} "
                      f"{aplic['tipo']:<15} "
                      f"{aplic['produto']:<25}")
        
        self.aguardar_enter()
    
    def relatorio_performance(self):
        """Relatório de performance dos animais"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 18 + "PERFORMANCE - GMD")
        print("=" * 60 + "\n")
        
        query = "SELECT * FROM vw_performance_animais ORDER BY gmd DESC"
        resultados = self.db.execute_query(query)
        
        if not resultados:
            print("\n❌ Nenhum dado de performance disponível!")
        else:
            print(f"Total de animais: {len(resultados)}\n")
            print(f"{'Brinco':<15} {'Nome':<20} {'Peso Inicial':<13} {'Peso Atual':<12} {'Ganho':<10} {'GMD':<10}")
            print("-" * 80)
            
            for animal in resultados:
                print(f"{animal['brinco']:<15} "
                      f"{(animal['nome'] or 'N/A'):<20} "
                      f"{animal['peso_inicial']:<13.2f} "
                      f"{animal['peso_final']:<12.2f} "
                      f"{animal['ganho_total']:<10.2f} "
                      f"{animal['gmd']:<10.3f}")
        
        self.aguardar_enter()
    
    def relatorio_resumo_rebanho(self):
        """Relatório resumo do rebanho"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 20 + "RESUMO DO REBANHO")
        print("=" * 60 + "\n")
        
        # Total de animais ativos
        query_total = "SELECT COUNT(*) as total FROM animais WHERE status = 'ativo'"
        total = self.db.execute_query(query_total)[0]['total']
        
        # Por sexo
        query_sexo = """
        SELECT sexo, COUNT(*) as qtd
        FROM animais
        WHERE status = 'ativo'
        GROUP BY sexo
        """
        por_sexo = self.db.execute_query(query_sexo)
        
        # Peso médio
        query_peso = """
        SELECT AVG(peso_atual) as peso_medio
        FROM animais
        WHERE status = 'ativo'
        """
        peso_medio = self.db.execute_query(query_peso)[0]['peso_medio']
        
        print(f"Total de Animais Ativos: {total}")
        print("\nPor Sexo:")
        for item in por_sexo:
            sexo_descr = "Machos" if item['sexo'] == 'M' else "Fêmeas"
            print(f"  {sexo_descr}: {item['qtd']}")
        
        if peso_medio:
            print(f"\nPeso Médio do Rebanho: {peso_medio:.2f}kg")
        
        print("\n" + "=" * 60)
        
        self.aguardar_enter()
    
    def fazer_backup(self):
        """Faz backup do banco de dados"""
        self.limpar_tela()
        print("=" * 60)
        print(" " * 22 + "BACKUP")
        print("=" * 60 + "\n")
        
        try:
            backup_path = self.db.backup_database()
            print(f"\n✓ Backup realizado com sucesso!")
            print(f"  Arquivo: {backup_path}")
        except Exception as e:
            print(f"\n❌ Erro ao fazer backup: {e}")
        
        self.aguardar_enter()
    
    def executar(self):
        """Loop principal da aplicação"""
        while True:
            self.mostrar_menu_principal()
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == '1':
                self.cadastrar_animal()
            elif opcao == '2':
                self.registrar_pesagem()
            elif opcao == '3':
                self.registrar_sanidade()
            elif opcao == '4':
                self.buscar_animal()
            elif opcao == '5':
                self.listar_animais_ativos()
            elif opcao == '6':
                self.menu_relatorios()
            elif opcao == '7':
                self.fazer_backup()
            elif opcao == '0':
                print("\nSaindo do sistema... Até logo!")
                break
            else:
                print("\n❌ Opção inválida!")
                self.aguardar_enter()


if __name__ == "__main__":
    app = InterfaceGado()
    app.executar()
