# 🚀🔒 Pipeline DevSecOps Completo com Docker e Gitea

[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![Gitea](https://img.shields.io/badge/Gitea-1.17+-green.svg)](https://gitea.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Produção-green.svg)](#)

> **Ambiente completo de DevSecOps local** com CI/CD integrado, análise de segurança e monitoramento. Ideal para desenvolver habilidades em segurança de aplicações e automação em ambiente controlado.**

## 🚀 Funcionalidades

### 📋 Aplicação Flask
- **Gerenciador de Tarefas** com CRUD completo
- **API REST** para integração com CI/CD
- **Health Check** para monitoramento
- **Interface web** moderna e responsiva

### 🐙 Gitea (Git Self-hosted)
- **Repositório Git** local
- **Gitea Actions** (CI/CD nativo)
- **Interface web** similar ao GitHub
- **SSH** para acesso remoto

### 🔒 Segurança Integrada
- **Bandit** (SAST) - Análise estática de código Python
- **Trivy** (SCA/DAST) - Análise de vulnerabilidades em containers
- **Docker Security** - Boas práticas de containerização

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │     Gitea       │    │   PostgreSQL    │
│   (Port 5000)   │    │   (Port 3000)   │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Docker Network │
                    │  devsecops-net  │
                    └─────────────────┘
```

## 🛠️ Tecnologias

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **Containerização**: Docker, Docker Compose
- **Git**: Gitea (self-hosted)
- **Database**: SQLite (app), PostgreSQL (Gitea)
- **Segurança**: Bandit, Trivy
- **Testes**: pytest

## 📦 Instalação e Uso

### Pré-requisitos
- Docker Desktop
- Git
- Navegador web

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/pipeline-devsecops-docker-gitea.git
cd pipeline-devsecops-docker-gitea
```

### 2. Execute o ambiente
```bash
docker-compose up --build -d
```

### 3. Acesse as aplicações
- **Flask App**: http://localhost:5001
- **Health Check**: http://localhost:5001/health
- **Gitea**: http://localhost:3000

## 🔧 Configuração do Gitea

### Primeira execução:
1. Acesse http://localhost:3000
2. Configure o banco de dados:
   - **Database Type**: PostgreSQL
   - **Host**: gitea-db:5432
   - **Username**: gitea
   - **Password**: gitea
   - **Database Name**: gitea
3. Configure o administrador
4. Crie seu primeiro repositório

## 🧪 Testes

Execute os testes automatizados:
```bash
docker-compose exec app python -m pytest tests/
```

## 🔒 Análise de Segurança

### Bandit (SAST)
```bash
docker-compose exec app bandit -r .
```

### Trivy (SCA/DAST)
```bash
docker-compose exec app trivy fs .
```

## 📁 Estrutura do Projeto

```
pipeline-devsecops-docker-gitea/
├── app/                      # Pacote principal da aplicação Flask
│   ├── __init__.py           # App factory (create_app)
│   ├── wsgi.py               # Ponto de entrada WSGI
│   ├── api/                  # Blueprints da API
│   ├── auth/                 # Autenticação
│   ├── health/               # Healthcheck
│   ├── static/               # Arquivos estáticos
│   └── templates/            # Templates Jinja
├── wsgi.py                   # Wrapper/entry (desenvolvimento)
├── app.py                    # Script utilitário (se aplicável)
├── docker-compose.yml        # Orquestração dos containers
├── Dockerfile                # Containerização da aplicação
├── requirements.txt          # Dependências Python
├── templates/
│   └── index.html            # Interface web
├── tests/
│   └── test_app.py           # Testes automatizados
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # Pipeline CI/CD
├── .gitignore                # Arquivos ignorados pelo Git
└── README.md                 # Documentação
```

## 🔄 CI/CD Pipeline

O projeto inclui um pipeline CI/CD configurado com:

1. **Build**: Construção da imagem Docker
2. **Test**: Execução de testes automatizados
3. **Security Scan**: Análise de vulnerabilidades
4. **Deploy**: Deploy automático (configurável)

## 🛡️ Segurança

### Boas Práticas Implementadas:
- ✅ Usuário não-root no container
- ✅ Health checks configurados
- ✅ Dependências atualizadas
- ✅ Análise estática de código
- ✅ Scan de vulnerabilidades
- ✅ Network isolation

### Vulnerabilidades Comuns Mitigadas:
- ✅ SQL Injection (SQLAlchemy ORM)
- ✅ XSS (Template escaping)
- ✅ CSRF (Flask-WTF)
- ✅ Container escape (usuário não-root)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique os logs: `docker-compose logs app`
2. Reinicie os containers: `docker-compose restart app`
3. Cheque se a aplicação está escutando: acesse `http://localhost:5001/health`
4. Verifique variáveis no `docker-compose.yml` para o serviço `app`:
   - `FLASK_APP=wsgi:app`
   - `PYTHONPATH=.`
   - `command: flask run --host=0.0.0.0 --port=5000`
5. Confirme o volume está montado: `.:/app`
6. Se aparecer erro "Could not import 'wsgi'" ou "No module named wsgi", garanta que o arquivo `wsgi.py` existe em `app/wsgi.py` e que o diretório de trabalho é `/app` no container.
7. Abra uma issue no GitHub

## 🎯 Próximos Passos

- [ ] Integração com SonarQube
- [ ] Análise de dependências com Safety
- [ ] Implementação de secrets management
- [ ] Configuração de backup automático
- [ ] Monitoramento com Prometheus/Grafana

---

<div align="center">
  
**Desenvolvido com ❤️ para a comunidade DevSecOps**  
[![Docker](https://img.shields.io/badge/Docker-Containerizado-blue?logo=docker)](https://www.docker.com/)
[![Gitea](https://img.shields.io/badge/Gitea-Self--hosted-green?logo=gitea)](https://gitea.io/)
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-yellow?logo=python)](https://flask.palletsprojects.com/)

</div>
