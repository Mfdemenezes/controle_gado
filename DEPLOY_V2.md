# Deploy do Sistema v2.0 - Reprodução Completa

## Arquivos Atualizados

### 1. mobile_app.html (2270 linhas)
**Frontend completo com todos os recursos novos**

### 2. Novos Recursos Implementados

#### ✅ Cadastros Base
- **Raças**: CRUD completo com nome, origem, descrição
- **Lotes**: CRUD completo com nome, descrição
- **Pastos**: CRUD completo com nome, área, tipo, descrição
- **Touros IA**: CRUD completo com brinco, nome, raça, registro, linhagem

#### ✅ Sistema de Reprodução
- **Dashboard com Stats**:
  - Total de prenhas
  - Partos no ano
  - Aguardando diagnóstico
  - Abortos no ano

- **Eventos Reprodutivos**:
  - Inseminação Artificial
  - Diagnóstico Positivo/Negativo
  - Parto (com opção natimorto)
  - Aborto
  - Cio

- **Timeline por Animal**:
  - Histórico completo de eventos reprodutivos
  - Datas previstas calculadas automaticamente
  - Touro usado em cada IA
  - Visualização cronológica

#### ✅ Integração de Ícones
Todos os 22 ícones personalizados foram integrados:
- Categorias: bezerro, garrote, touro, vaca
- Eventos: nascimento, morte, aborto, cio, prenha
- Ações: brinco, cadastro, pesagem, sanidade, vacinação

#### ✅ Hero Image
- Imagem `pagina_home_api_gado.jpg` na home
- Overlay com título "Sistema de Gestão Pecuária"

#### ✅ Formulário de Animal Atualizado
- Dropdown de Raças (busca do banco)
- Dropdown de Lotes (busca do banco)
- Dropdown de Pastos (busca do banco)
- Layout responsivo em grid

## Passos para Deploy

### 1. No servidor Oracle Cloud

```bash
# Conectar ao servidor
ssh ubuntu@167.234.234.124

# Ir para o diretório do projeto
cd /caminho/do/projeto

# Fazer backup do arquivo atual
cp mobile_app.html mobile_app.html.backup

# Atualizar o arquivo
# (usar scp, git pull, ou copiar manualmente)
```

### 2. Copiar arquivo atualizado via SCP (do seu Mac)

```bash
scp /Users/marcelofmenezes/estudo/controle_gado/mobile_app.html ubuntu@167.234.234.124:/caminho/do/projeto/
```

### 3. Reiniciar containers Docker

```bash
# No servidor
cd /caminho/do/projeto
docker-compose restart nginx
docker-compose restart api

# Verificar se estão rodando
docker-compose ps
```

### 4. Testar no navegador

Acessar: **https://agromm.mbam.com.br**

## Checklist de Testes

### ✅ Teste 1: Cadastros Base
1. Criar uma Raça (ex: "Nelore", origem "Zebuína")
2. Criar um Lote (ex: "Lote 2025")
3. Criar um Pasto (ex: "Pasto 1", 10ha, Brachiaria)
4. Criar um Touro IA (ex: "T001", "Imperador", Nelore)
5. Editar cada um (botão ✏️)
6. Testar exclusão (botão 🗑️)

### ✅ Teste 2: Cadastro de Animal
1. Ir em "Cadastrar" (➕)
2. Preencher formulário:
   - Brinco: 001
   - Nome: "Teste"
   - Sexo: Fêmea
   - Data nascimento: 01/01/2022
   - Raça: Nelore (usar dropdown)
   - Peso: 350kg
   - Lote: Lote 2025
   - Pasto: Pasto 1
3. Salvar
4. Verificar se aparece na lista de animais
5. Verificar se categoria foi calculada automaticamente (deve ser "Vaca")

### ✅ Teste 3: Reprodução
1. Ir em "Reprodução" (👶 no menu inferior)
2. **Tab Registrar**:
   - Buscar animal: 001
   - Tipo evento: Inseminação Artificial
   - Data: hoje
   - Touro: T001 - Imperador
   - Salvar
3. **Tab Eventos**:
   - Deve aparecer evento de diagnóstico previsto (45 dias)
4. **Tab Timeline**:
   - Buscar animal: 001
   - Deve mostrar histórico com ícone de inseminação

### ✅ Teste 4: Registrar Diagnóstico Positivo
1. Reprodução > Registrar
2. Animal: 001
3. Tipo: Diagnóstico Positivo
4. Data: 45 dias após IA
5. Salvar
6. Verificar em Eventos:
   - Deve aparecer previsão de parto (283 dias após IA)

### ✅ Teste 5: Registrar Parto
1. Reprodução > Registrar
2. Animal: 001
3. Tipo: Parto
4. Data: data prevista
5. **NÃO** marcar natimorto
6. Salvar
7. Ir em Animais:
   - Deve ter criado automaticamente um novo bezerro/bezerra

### ✅ Teste 6: Ícones
Verificar se todos os ícones estão carregando:
- Home: stats com ícones de brinco, vaca prenha, vaca, touro
- Cadastros Base: ícones nos cards
- Lista de animais: ícones de categoria
- Eventos reprodutivos: ícones de nascimento, cio, prenha, aborto

## Troubleshooting

### Erro: "Not Found" ao acessar API
```bash
# Verificar logs do nginx
docker-compose logs nginx

# Verificar se API está respondendo localmente
curl http://localhost:8000/health
```

### Erro: Ícones não carregam
```bash
# Verificar se pasta img/ está montada
docker-compose exec nginx ls /usr/share/nginx/html/img/

# Se não estiver, atualizar docker-compose.yml:
# - ./img:/usr/share/nginx/html/img:ro
```

### Erro: "Internal Server Error" no cadastro
```bash
# Aplicar fix da função no banco
docker-compose exec postgres psql -U postgres -d seu_banco -f fix_function.sql
```

## Próximos Passos (Opcional)

1. **Sanidade/Vacinação**: Implementar módulo de controle sanitário
2. **Pesagens em Gráfico**: Visualizar evolução de peso
3. **Relatórios PDF**: Gerar relatórios para impressão
4. **Fotos de Animais**: Upload de fotos via câmera do celular
5. **Notificações Push**: Alertas de eventos próximos

## Suporte

Em caso de dúvidas, verificar:
- Logs: `docker-compose logs -f`
- Banco de dados: `docker-compose exec postgres psql -U postgres`
- API docs: https://agromm.mbam.com.br/docs
