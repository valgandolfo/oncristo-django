import os
import django
from django.db import IntegrityError  # type: ignore

# Configura o Django para usar o settings do projeto
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_igreja.settings")
django.setup()

from app_igreja.models.area_admin.models_dizimistas import TBDIZIMISTAS  # noqa: E402
from app_igreja.models.area_admin.models_colaboradores import TBCOLABORADORES  # noqa: E402


def criar_dizimistas_fake(qtd: int = 100) -> None:
    """
    Cria registros fake na tabela TBDIZIMISTAS.

    OBS:
    - Este script usa o banco configurado nas variáveis de ambiente.
      Se você exportar o `.env_remote_local`, ele vai gravar direto no
      banco do DigitalOcean.
    - Campos obrigatórios: DIS_telefone (único) e DIS_nome.
    - Os demais campos são opcionais e ficam em branco.
    """
    criados = 0

    for i in range(1, qtd + 1):
        # Gera telefone único com pelo menos 10 dígitos
        telefone = f"1199{i:07d}"  # ex: 11990000001, 11990000002, ...

        try:
            obj, created = TBDIZIMISTAS.objects.get_or_create(
                DIS_telefone=telefone,
                defaults={
                    "DIS_nome": f"Dizimista Teste {i}",
                    "DIS_email": f"dizimista_teste_{i}@exemplo.com",
                    # demais campos ficam em branco / nulos
                },
            )

            if created:
                criados += 1
                print(f"[OK] Dizimista criado: {obj.DIS_nome} - {obj.DIS_telefone}")
            else:
                print(f"[SKIP] Dizimista já existia telefone {telefone}, pulando...")
        except IntegrityError:
            # Pode acontecer por causa da formatação de telefone no save()
            print(f"[ERRO] Telefone já usado após formatação ({telefone}), pulando...")
            continue

    print(f"\nTotal de dizimistas criados agora: {criados} registro(s).")


def criar_colaboradores_fake(qtd: int = 100) -> None:
    """
    Cria registros fake na tabela TBCOLABORADORES.

    OBS:
    - Usa o banco configurado nas variáveis de ambiente
      (local ou DO, conforme o .env exportado).
    - Campos obrigatórios: COL_telefone (único), COL_nome_completo, COL_status, COL_membro_ativo.
    """
    criados = 0

    for i in range(1, qtd + 1):
        telefone = f"1198{i:07d}"  # separa dos telefones de dizimistas

        try:
            obj, created = TBCOLABORADORES.objects.get_or_create(
                COL_telefone=telefone,
                defaults={
                    "COL_nome_completo": f"Colaborador Teste {i}",
                    "COL_apelido": f"Colab {i}",
                    "COL_status": "ATIVO",
                    "COL_membro_ativo": True,
                    "COL_cidade": "São Paulo",
                    "COL_estado": "SP",
                },
            )

            if created:
                criados += 1
                print(f"[OK] Colaborador criado: {obj.COL_nome_completo} - {obj.COL_telefone}")
            else:
                print(f"[SKIP] Colaborador já existia telefone {telefone}, pulando...")
        except IntegrityError:
            print(f"[ERRO] Telefone de colaborador já usado após formatação ({telefone}), pulando...")
            continue

    print(f"\nTotal de colaboradores criados agora: {criados} registro(s).")


if __name__ == "__main__":
    criar_dizimistas_fake(100)
    criar_colaboradores_fake(100)


