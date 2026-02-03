"""Views de Paróquias - CRUD registro único (single-record) + horários em JSON."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ...forms.area_admin.forms_paroquias import ParoquiaForm, ParoquiaHorariosForm
from ...models.area_admin.models_paroquias import TBPAROQUIA

URL_PAROQUIA_CRUD_UNICO = 'app_igreja:paroquia_crud_unico'
DIAS_SEMANA = ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def _salvar_horarios_paroquia(paroquia, form_horarios):
    """Extrai horários do form e persiste no JSON da paróquia."""
    if not form_horarios.is_valid():
        return False
    horarios_data = {}
    for dia in DIAS_SEMANA:
        raw = form_horarios.cleaned_data.get(f'{dia}_horarios', '') or ''
        horarios_data[dia] = [h.strip() for h in raw.split(',') if h.strip()]
    paroquia.set_horarios_fixos(horarios_data)
    paroquia.save()
    return True


@login_required
@admin_required
def paroquia_crud_unico(request):
    """Single-record CRUD: GET sem ?edit=1 = visualização; GET ?edit=1 = edição; POST = salvar."""
    paroquia = TBPAROQUIA.objects.first()
    if not paroquia:
        paroquia = TBPAROQUIA.objects.create(
            PAR_nome_paroquia="Nova Paróquia",
            PAR_diocese=None,
            PAR_paroco="", PAR_secretario="",
            PAR_cep="", PAR_endereco="", PAR_numero="", PAR_cidade="", PAR_uf="", PAR_bairro="",
            PAR_telefone="", PAR_email="", PAR_cnpj="",
            PAR_banco="", PAR_agencia="", PAR_conta="",
            PAR_pix_chave="", PAR_pix_tipo="", PAR_pix_beneficiario="", PAR_pix_cidade="", PAR_pix_uf=""
        )
        messages.info(request, 'Paróquia criada automaticamente. Preencha os dados.')

    modo_edicao = request.GET.get('edit') == '1'

    if request.method == 'POST':
        form = ParoquiaForm(request.POST, request.FILES, instance=paroquia)
        if form.is_valid():
            try:
                form.save()
                _salvar_horarios_paroquia(paroquia, ParoquiaHorariosForm(request.POST, instance=paroquia))
                messages.success(request, 'Dados da paróquia atualizados com sucesso!')
                return redirect(URL_PAROQUIA_CRUD_UNICO)
            except Exception as e:
                messages.error(request, f'Erro ao salvar dados: {e}')
        else:
            messages.error(request, f'Erro ao salvar. Verifique os campos: {form.errors}')

    form = ParoquiaForm(instance=paroquia) if modo_edicao else None
    try:
        form_horarios = ParoquiaHorariosForm(instance=paroquia)
    except Exception:
        form_horarios = ParoquiaHorariosForm()

    context = {
        'paroquia': paroquia,
        'form': form,
        'form_horarios': form_horarios,
        'modo_edicao': modo_edicao,
        'modo_visualizacao': not modo_edicao,
    }
    return render(request, 'admin_area/tpl_paroquia.html', context)
