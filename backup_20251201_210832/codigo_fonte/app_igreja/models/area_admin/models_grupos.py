from django.db import models
from django.utils import timezone

class TBGRUPOS(models.Model):
    """
    Tabela de Grupos Litúrgicos - Define os grupos de atividades da igreja
    """
    GRU_id = models.AutoField(primary_key=True, verbose_name="ID do Grupo")
    GRU_nome_grupo = models.CharField(max_length=255, verbose_name="Nome do Grupo")
    GRU_eventos_json = models.TextField(
        verbose_name="Eventos do Grupo", 
        blank=True, 
        null=True,
        default='[]',
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
        return f"{self.GRU_nome_grupo}"
    
    def get_eventos_list(self):
        """Retorna lista de eventos do grupo"""
        import json
        try:
            eventos = json.loads(self.GRU_eventos_json or '[]')
            return [evento.strip() for evento in eventos if evento.strip()]
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_eventos_list(self, eventos_list):
        """Define a lista de eventos do grupo"""
        import json
        eventos_limpos = [evento.strip() for evento in eventos_list if evento.strip()]
        self.GRU_eventos_json = json.dumps(eventos_limpos)
    
    def get_eventos_display(self):
        """Retorna eventos formatados para exibição"""
        eventos = self.get_eventos_list()
        return ', '.join(eventos) if eventos else 'Nenhum evento definido'
    
    def add_evento(self, evento):
        """Adiciona um evento à lista"""
        eventos = self.get_eventos_list()
        if evento.strip() and evento.strip() not in eventos:
            eventos.append(evento.strip())
            self.set_eventos_list(eventos)
    
    def remove_evento(self, evento):
        """Remove um evento da lista"""
        eventos = self.get_eventos_list()
        if evento.strip() in eventos:
            eventos.remove(evento.strip())
            self.set_eventos_list(eventos)

    def save(self, *args, **kwargs):
        """Override save para atualizar GRU_data_atualizacao"""
        self.GRU_data_atualizacao = timezone.now()
        super().save(*args, **kwargs)
