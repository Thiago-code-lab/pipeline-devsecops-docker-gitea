# 🎬 Script de Demonstração - Pipeline DevSecOps

## 📸 **Capturas de Tela Recomendadas**

### **1. Estrutura do Projeto**
```bash
# Mostrar a estrutura de arquivos
tree /f
# ou
dir
```

### **2. Status dos Containers**
```bash
# Mostrar containers rodando
docker-compose ps
```

### **3. Logs em Tempo Real**
```bash
# Mostrar logs dos containers
docker-compose logs -f
```

### **4. Aplicação Flask Funcionando**
- Abrir: http://localhost:5000
- Capturar: Interface do gerenciador de tarefas
- Demonstrar: Adicionar, editar, excluir tarefas

### **5. API REST Funcionando**
- Abrir: http://localhost:5000/api/tasks
- Capturar: Resposta JSON da API

### **6. Health Check**
- Abrir: http://localhost:5000/health
- Capturar: Status "healthy" em JSON

### **7. Gitea Funcionando**
- Abrir: http://localhost:3000
- Capturar: Interface do Gitea

### **8. Testes Automatizados**
```bash
# Executar testes
docker-compose exec flask-app python -m pytest tests/ -v
```

### **9. Análise de Segurança**
```bash
# Executar Bandit
docker-compose exec flask-app bandit -r . -f json
```

### **10. GitHub Repository**
- Abrir: https://github.com/Thiago-code-lab/pipeline-devsecops-docker-gitea
- Capturar: Página principal do repositório

### **11. GitHub Actions**
- Abrir: https://github.com/Thiago-code-lab/pipeline-devsecops-docker-gitea/actions
- Capturar: Pipeline CI/CD

## 🎯 **Sequência de Demonstração**

### **Fase 1: Infraestrutura**
1. Mostrar estrutura do projeto
2. Mostrar containers rodando
3. Mostrar logs em tempo real

### **Fase 2: Aplicação**
4. Mostrar aplicação Flask funcionando
5. Demonstrar CRUD de tarefas
6. Mostrar API REST
7. Mostrar health check

### **Fase 3: Git e CI/CD**
8. Mostrar Gitea funcionando
9. Mostrar repositório no GitHub
10. Mostrar GitHub Actions

### **Fase 4: Segurança**
11. Executar testes automatizados
12. Executar análise de segurança
13. Mostrar resultados

## 📱 **Dicas para Capturas**

### **Terminal**
- Use tema escuro para melhor visualização
- Aumente o tamanho da fonte
- Capture comandos sendo executados

### **Navegador**
- Use modo escuro se disponível
- Capture telas completas
- Mostre URLs na barra de endereços

### **Docker Desktop**
- Capture containers rodando
- Mostre logs em tempo real
- Capture uso de recursos

## 🎬 **Script de Execução**

```bash
# 1. Iniciar ambiente
docker-compose up -d

# 2. Verificar status
docker-compose ps

# 3. Mostrar logs
docker-compose logs -f

# 4. Executar testes
docker-compose exec flask-app python -m pytest tests/ -v

# 5. Análise de segurança
docker-compose exec flask-app bandit -r . -f json

# 6. Health check
curl http://localhost:5000/health
```

## 📸 **Momentos Chave para Capturar**

1. **Início**: Containers sendo iniciados
2. **Funcionamento**: Aplicação respondendo
3. **Interação**: Usuário adicionando tarefas
4. **API**: Resposta JSON da API
5. **Testes**: Execução de testes automatizados
6. **Segurança**: Análise de vulnerabilidades
7. **GitHub**: Repositório e Actions funcionando

---

**🎬 Agora você pode seguir este script para criar capturas impressionantes do seu projeto!** 