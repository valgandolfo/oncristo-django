from django.shortcuts import render
from django.http import Http404
import qrcode
import io
import base64

from ...models.area_admin.models_paroquias import TBPAROQUIA


def doacoes_publico(request):
    """
    Área pública para visualizar informações de doações
    Exibe métodos de pagamento: PIX, Cartão de Crédito, Cartão de Débito e Boleto
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    if not paroquia:
        raise Http404("Paróquia não encontrada")
    
    # Gerar QR Code PIX se houver chave PIX
    qr_code_base64 = None
    if paroquia.PAR_pix_chave:
        try:
            # Criar QR Code com a chave PIX
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(paroquia.PAR_pix_chave)
            qr.make(fit=True)
            
            # Criar imagem do QR Code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            qr_code_base64 = img_str
        except Exception as e:
            # Se houver erro na geração do QR Code, continuar sem ele
            qr_code_base64 = None
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'paroquia': paroquia,
        'qr_code': qr_code_base64,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/tpl_doacoes_publico.html', context)

