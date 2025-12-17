# 🚀 Como Configurar Wasabi no Projeto

## Passo 1: Criar Conta no Wasabi

1. Acesse: https://wasabi.com/
2. Clique em "Sign Up" (criar conta)
3. Preencha os dados e confirme o email
4. **30 dias grátis** para testar!

## Passo 2: Criar um Bucket

1. Faça login no painel do Wasabi
2. Vá em **"Buckets"** → **"Create Bucket"**
3. Escolha:
   - **Nome do bucket**: `projeto-oncristo-media` (ou outro nome)
   - **Região**: `us-east-1` (ou outra região próxima)
4. Clique em **"Create"**

## Passo 3: Obter Credenciais de Acesso

1. No painel do Wasabi, vá em **"Access Keys"**
2. Clique em **"Create New Access Key"**
3. Anote:
   - **Access Key ID** (exemplo: `ABC123...`)
   - **Secret Access Key** (exemplo: `xyz789...`) - **Só aparece uma vez!**

## Passo 4: Configurar o .env_local

Edite o arquivo `.env_local` e adicione/altere:

```bash
# ============================================================================
# CONFIGURAÇÕES WASABI (Storage de Imagens)
# ============================================================================
STORAGE_PROVIDER=wasabi
AWS_ACCESS_KEY_ID=sua-access-key-do-wasabi
AWS_SECRET_ACCESS_KEY=sua-secret-key-do-wasabi
AWS_STORAGE_BUCKET_NAME=projeto-oncristo-media
AWS_S3_REGION_NAME=us-east-1
```

**Importante:**
- Substitua `sua-access-key-do-wasabi` pela Access Key ID do Wasabi
- Substitua `sua-secret-key-do-wasabi` pela Secret Access Key do Wasabi
- Substitua `projeto-oncristo-media` pelo nome do bucket que você criou
- A região deve ser a mesma onde você criou o bucket

## Passo 5: Reiniciar o Servidor Django

```bash
# Pare o servidor (Ctrl+C) e inicie novamente
python manage.py runserver
```

## ✅ Pronto!

Agora todas as imagens serão salvas no Wasabi automaticamente!

---

## 💰 Preços do Wasabi (2024)

- **Armazenamento**: $0.0059 por GB/mês (muito mais barato que AWS!)
- **Transferência de dados**: **GRÁTIS** (sem taxa de saída!)
- **30 dias grátis** para testar

## 🔄 Migrar Imagens do AWS para Wasabi

Se você já tem imagens no AWS S3 e quer migrar:

1. Use o painel do Wasabi para importar do S3
2. Ou use ferramentas como `rclone` ou `s3cmd`
3. Ou simplesmente faça upload novamente das imagens pelo admin do Django

---

## ❓ Problemas Comuns

**Erro: "Access Denied"**
- Verifique se as credenciais estão corretas
- Verifique se o bucket existe na região correta

**Erro: "Bucket not found"**
- Verifique o nome do bucket no `.env_local`
- Verifique se a região está correta

**Imagens não aparecem**
- Verifique se `STORAGE_PROVIDER=wasabi` está configurado
- Reinicie o servidor Django após alterar o `.env_local`

