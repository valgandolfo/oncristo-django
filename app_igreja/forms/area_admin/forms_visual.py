from django import forms
from ...models.area_admin.models_visual import TBVISUAL
from .forms_commons import BaseAdminForm

_attrs = lambda **kw: {**{'class': 'form-control', 'accept': 'image/*'}, **kw}
_MAX_MB = lambda mb: mb * 1024 * 1024


class VisualForm(BaseAdminForm):
    """Formulário para Configurações Visuais (TBVISUAL)."""

    class Meta:
        model = TBVISUAL
        fields = [
            'VIS_FOTO_CAPA',
            'VIS_FOTO_BRASAO',
            'VIS_FOTO_PADROEIRO',
            'VIS_FOTO_PRINCIPAL'
        ]
        widgets = {
            'VIS_FOTO_CAPA': forms.FileInput(attrs=_attrs(onchange='previewImage(this, "preview-capa")')),
            'VIS_FOTO_BRASAO': forms.FileInput(attrs=_attrs(onchange='previewImage(this, "preview-brasao")')),
            'VIS_FOTO_PADROEIRO': forms.FileInput(attrs=_attrs(onchange='previewImage(this, "preview-padroeiro")')),
            'VIS_FOTO_PRINCIPAL': forms.FileInput(attrs=_attrs(onchange='previewImage(this, "preview-principal")')),
        }
        labels = {
            'VIS_FOTO_CAPA': 'Foto da Paróquia',
            'VIS_FOTO_BRASAO': 'Foto do Brasão (Logo)',
            'VIS_FOTO_PADROEIRO': 'Foto do(a) Santo(a) Padroeiro(a)',
            'VIS_FOTO_PRINCIPAL': 'Imagem Principal (Homepage)',
        }
        help_texts = {
            'VIS_FOTO_CAPA': 'Foto da paróquia',
            'VIS_FOTO_BRASAO': 'Logo ou brasão da paróquia',
            'VIS_FOTO_PADROEIRO': 'Imagem do santo padroeiro da paróquia',
            'VIS_FOTO_PRINCIPAL': 'Imagem principal no topo da página inicial (recomendado: 286x253px)',
        }

    def _clean_foto_tamanho(self, foto, max_mb, msg):
        if foto and foto.size > _MAX_MB(max_mb):
            raise forms.ValidationError(msg)
        return foto

    def clean_VIS_FOTO_CAPA(self):
        return self._clean_foto_tamanho(
            self.cleaned_data.get('VIS_FOTO_CAPA'), 5, 'A foto de capa deve ter no máximo 5MB.'
        )

    def clean_VIS_FOTO_BRASAO(self):
        return self._clean_foto_tamanho(
            self.cleaned_data.get('VIS_FOTO_BRASAO'), 2, 'O brasão deve ter no máximo 2MB.'
        )

    def clean_VIS_FOTO_PADROEIRO(self):
        return self._clean_foto_tamanho(
            self.cleaned_data.get('VIS_FOTO_PADROEIRO'), 3, 'A foto do padroeiro deve ter no máximo 3MB.'
        )

    def clean_VIS_FOTO_PRINCIPAL(self):
        return self._clean_foto_tamanho(
            self.cleaned_data.get('VIS_FOTO_PRINCIPAL'), 5, 'A imagem principal deve ter no máximo 5MB.'
        )
