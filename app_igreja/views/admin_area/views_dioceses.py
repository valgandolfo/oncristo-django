"""Views de Dioceses - CRUD registro único (single-record)."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ...forms.area_admin.forms_dioceses import dioceseform
from ...models.area_admin.models_dioceses import TBDIOCESE

URL_DIOCESE_CRUD_UNICO = 'app_igreja:diocese_crud_unico'


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def diocese_crud_unico(request):
    """Single-record CRUD: GET sem ?edit=1 = visualização; GET ?edit=1 = edição; POST = salvar."""
    diocese = TBDIOCESE.objects.first()
    if not diocese:
        diocese = TBDIOCESE.objects.create(
            DIO_nome_diocese="Nova Diocese",
            DIO_nome_bispo="", DIO_foto_bispo=None,
            DIO_cep="", DIO_endereco="", DIO_numero="", DIO_complemento="",
            DIO_bairro="", DIO_cidade="", DIO_uf="",
            DIO_telefone="", DIO_email="", DIO_site=""
        )
        messages.info(request, 'Diocese criada automaticamente. Preencha os dados.')

    modo_edicao = request.GET.get('edit') == '1'

    if request.method == 'POST':
        form = dioceseform(request.POST, request.FILES, instance=diocese)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados da Diocese atualizados com sucesso!')
            return redirect(URL_DIOCESE_CRUD_UNICO)
        messages.error(request, 'Erro ao salvar dados. Verifique os campos.')

    form = dioceseform(instance=diocese) if modo_edicao else None
    context = {
        'diocese': diocese,
        'form': form,
        'modo_edicao': modo_edicao,
        'modo_visualizacao': not modo_edicao,
    }
    return render(request, 'admin_area/tpl_dioceses.html', context)
