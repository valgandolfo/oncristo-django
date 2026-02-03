import os
import sys
import boto3
import django
from dotenv import load_dotenv

# 1. Ajuste de Terreno: Garante que o Python encontre a pasta pro_igreja
sys.path.append(os.getcwd())

# 2. Carregar variáveis de ambiente
load_dotenv('.env_local')

# 3. O ALVO: pro_igreja.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings')

# 4. Inicializa o Django
try:
    django.setup()
    print("✅ Django inicializado com sucesso para limpeza.")
except Exception as e:
    print(f"❌ Erro ao inicializar Django: {e}")
    sys.exit(1)

# Importações de models APÓS o django.setup()
from app_igreja.models.area_admin.models_dioceses import TBDIOCESE
from app_igreja.models.area_admin.models_paroquias import TBPAROQUIA
from app_igreja.models.area_admin.models_celebrantes import TBCELEBRANTES
from app_igreja.models.area_admin.models_banners import TBBANNERS
from app_igreja.models.area_admin.models_colaboradores import TBCOLABORADORES
from app_igreja.models.area_admin.models_dizimistas import TBDIZIMISTAS
from app_igreja.models.area_admin.models_mural import TBMURAL
from app_igreja.models.area_admin.models_visual import TBVISUAL

def limpar_wasabi():
    print("🚀 Iniciando varredura no Wasabi...")
    
    # Configurar cliente S3 (Wasabi)
    # Buscamos a URL do endpoint. Se não estiver no .env, usamos a padrão us-east-1
    endpoint = os.getenv('AWS_S3_ENDPOINT_URL', 'https://s3.us-east-1.wasabisys.com')
    
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        region_name='sa-east-1', # Tente colocar a string direta aqui        
    
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    if not bucket_name:
        print("❌ Erro: AWS_STORAGE_BUCKET_NAME não encontrado no .env_local")
        return

    # 5. Coletar todos os arquivos que o Banco de Dados conhece (O Pente Fino)
    arquivos_no_banco = set()
    
    print("🔍 Coletando nomes de arquivos do banco de dados...")

    # Diocese e Paróquia
    for d in TBDIOCESE.objects.all():
        if d.DIO_foto_bispo: arquivos_no_banco.add(d.DIO_foto_bispo.name)
    for p in TBPAROQUIA.objects.all():
        if p.PAR_foto_paroco: arquivos_no_banco.add(p.PAR_foto_paroco.name)
    
    # Celebrantes e Colaboradores
    for c in TBCELEBRANTES.objects.all():
        if c.CEL_foto: arquivos_no_banco.add(c.CEL_foto.name)
    for col in TBCOLABORADORES.objects.all():
        if col.COL_foto: arquivos_no_banco.add(col.COL_foto.name)
        
    # Banners e Dizimistas
    for b in TBBANNERS.objects.all():
        if b.BAN_IMAGE: arquivos_no_banco.add(b.BAN_IMAGE.name)
    for diz in TBDIZIMISTAS.objects.all():
        if diz.DIS_foto: arquivos_no_banco.add(diz.DIS_foto.name)

    # Mural (5 fotos)
    for m in TBMURAL.objects.all():
        for i in range(1, 6):
            foto = getattr(m, f'MUR_foto{i}_mural')
            if foto: arquivos_no_banco.add(foto.name)

    # Visual (4 fotos)
    for v in TBVISUAL.objects.all():
        if v.VIS_FOTO_CAPA: arquivos_no_banco.add(v.VIS_FOTO_CAPA.name)
        if v.VIS_FOTO_BRASAO: arquivos_no_banco.add(v.VIS_FOTO_BRASAO.name)
        if v.VIS_FOTO_PADROEIRO: arquivos_no_banco.add(v.VIS_FOTO_PADROEIRO.name)
        if v.VIS_FOTO_PRINCIPAL: arquivos_no_banco.add(v.VIS_FOTO_PRINCIPAL.name)

    print(f"📊 Total de arquivos válidos no banco: {len(arquivos_no_banco)}")

    # 6. Listar arquivos no Wasabi e comparar
    count_deleted = 0
    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    
                    # Ignorar pastas ou arquivos de sistema (se houver)
                    if key.endswith('/'): continue
                    
                    if key not in arquivos_no_banco:
                        print(f"🗑️ Órfão encontrado: {key}")
                        # s3.delete_object(Bucket=bucket_name, Key=key) # DESCOMENTE APÓS TESTAR
                        count_deleted += 1

        if count_deleted == 0:
            print("✨ Wasabi está limpo! Nenhum arquivo órfão encontrado.")
        else:
            print(f"⚠️  Total de arquivos órfãos listados: {count_deleted}")
            print("💡 Para apagar de verdade, desconte a linha 's3.delete_object' no script.")

    except Exception as e:
        print(f"❌ Erro ao acessar o Wasabi: {e}")

if __name__ == "__main__":
    limpar_wasabi()
