import json

from django.db import models
from django.utils import timezone


class TBGRUPOS(models.Model):
    """Grupos litúrgicos / atividades da igreja."""
    GRU_id = models.AutoField(primary_key=True, verbose_name="ID do Grupo")
    GRU_nome_grupo = models.CharField(max_length=255, verbose_name="Nome do Grupo")
    GRU_eventos_json = models.TextField(
        verbose_name="Eventos do Grupo",
        blank=True, null=True, default='[]',
        help_text="Lista de eventos/atividades do grupo em formato JSON"
    )
    GRU_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    GRU_data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")
    GRU_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        db_table = 'TBGRUPOS'
        verbose_name = 'Grupo Litúrgico'
        verbose_name_plural = 'Grupos Litúrgicos'
        ordering = ['GRU_nome_grupo']

    def __str__(self):
        return str(self.GRU_nome_grupo)

    def get_eventos_list(self):
        try:
            eventos = json.loads(self.GRU_eventos_json or '[]')
            return [e.strip() for e in eventos if isinstance(e, str) and e.strip()]
        except (json.JSONDecodeError, TypeError):
            return []

    def set_eventos_list(self, eventos_list):
        self.GRU_eventos_json = json.dumps([e.strip() for e in eventos_list if e and str(e).strip()])

    def get_eventos_display(self):
        eventos = self.get_eventos_list()
        return ', '.join(eventos) if eventos else 'Nenhum evento definido'

    def add_evento(self, evento):
        evento = evento.strip() if evento else ''
        if not evento:
            return
        eventos = self.get_eventos_list()
        if evento not in eventos:
            eventos.append(evento)
            self.set_eventos_list(eventos)

    def remove_evento(self, evento):
        evento = evento.strip() if evento else ''
        eventos = self.get_eventos_list()
        if evento in eventos:
            eventos.remove(evento)
            self.set_eventos_list(eventos)
