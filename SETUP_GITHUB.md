# 🚀 Configuração do Repositório GitHub

## Passos para criar o repositório no GitHub:

### 1. Criar o repositório no GitHub
- Acesse: https://github.com/new
- **Repository name**: `pipeline-devsecops-docker-gitea`
- **Description**: Pipeline DevSecOps local com Docker, Gitea Actions e análise de vulnerabilidades
- **Visibility**: Public (ou Private, conforme sua preferência)
- **NÃO** inicialize com README, .gitignore ou license (já temos esses arquivos)

### 2. Conectar o repositório local ao GitHub
Após criar o repositório no GitHub, execute os seguintes comandos:

```bash
# Adicionar o remote origin
git remote add origin https://github.com/SEU_USUARIO/pipeline-devsecops-docker-gitea.git

# Fazer push dos commits
git push -u origin main
```

### 3. Verificar se tudo está funcionando
```bash
# Verificar o remote
git remote -v

# Verificar o status
git status
```

## 📋 Checklist

- [ ] Repositório criado no GitHub
- [ ] Remote origin configurado
- [ ] Push inicial realizado
- [ ] GitHub Actions ativado
- [ ] Issues habilitadas
- [ ] Wiki habilitada (opcional)

## 🔧 Configurações Adicionais

### GitHub Actions
- Vá em Settings > Actions > General
- Habilite "Allow all actions and reusable workflows"

### Branch Protection (Recomendado)
- Vá em Settings > Branches
- Adicione rule para branch `main`
- Habilite "Require a pull request before merging"
- Habilite "Require status checks to pass before merging"

### Security
- Vá em Settings > Security
- Habilite "Dependabot alerts"
- Habilite "Dependabot security updates"

## 🎯 Próximos Passos

1. **Configurar Secrets** (se necessário):
   - Settings > Secrets and variables > Actions
   - Adicione secrets para deploy (se aplicável)

2. **Configurar Environments**:
   - Settings > Environments
   - Crie environments: `staging`, `production`

3. **Configurar Branch Protection**:
   - Proteja a branch `main`
   - Configure status checks obrigatórios

4. **Ativar GitHub Pages** (opcional):
   - Settings > Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages`

## 🆘 Troubleshooting

### Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/pipeline-devsecops-docker-gitea.git
```

### Erro: "Authentication failed"
- Verifique se você está logado no GitHub
- Use token de acesso pessoal se necessário

### Erro: "Permission denied"
- Verifique se você tem permissão para push no repositório
- Verifique se o repositório foi criado corretamente

---

**Após seguir estes passos, seu projeto estará disponível no GitHub com CI/CD configurado! 🎉** 