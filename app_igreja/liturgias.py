#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App separado para funcionalidades de liturgia
Acesse via: https://gandolfovaldir.pythonanywhere.com/liturgias/
Abre em janela modal com botão "Sair" para fechar
"""

from flask import Blueprint, request, jsonify, render_template_string
import os
import logging
import mysql.connector
from datetime import datetime, date
from config import DB_CONFIG
# import pymysql.cursors # Added for pymysql.cursors.DictCursor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria o blueprint
app_liturgias = Blueprint('liturgias', __name__)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_db_connection():
    """Cria conexão com o banco de dados"""
    return mysql.connector.connect(**DB_CONFIG)

def get_liturgia_por_data(data_lit):
    """Busca liturgia por data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = """
        SELECT TIPOLIT, TEXTO 
        FROM TBLITURGIA 
        WHERE DATALIT = %s AND STATUSLIT = 1
        ORDER BY 
            CASE TIPOLIT 
                WHEN 'Primeira Leitura' THEN 1
                WHEN 'Salmo' THEN 2
                WHEN 'Segunda Leitura' THEN 3
                WHEN 'Evangelho' THEN 4
                ELSE 5
            END
        """
        
        cursor.execute(sql, (data_lit,))
        resultados = cursor.fetchall()
        
        liturgia = {
            'data': data_lit.strftime('%d/%m/%Y'),
            'leituras': {}
        }
        
        for row in resultados:
            # Aplica formatação de versículos em negrito
            texto_formatado = formatar_versiculos(row['TEXTO'])
            liturgia['leituras'][row['TIPOLIT']] = texto_formatado
        
        return liturgia
        
    except Exception as e:
        logger.error(f"Erro ao buscar liturgia: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def get_liturgia_hoje():
    """Busca liturgia do dia atual"""
    return get_liturgia_por_data(date.today())

def formatar_versiculos(texto):
    """Formata os versículos em negrito"""
    import re
    
    # Padrão simples: número seguido de espaço e texto até o próximo número
    partes = re.split(r'(\d+\s+)', texto)
    
    resultado = []
    for i, parte in enumerate(partes):
        if re.match(r'\d+\s+', parte):
            # É um número seguido de espaço - formata em negrito
            numero = parte.strip()
            resultado.append(f'<strong>{numero}</strong> ')
        else:
            resultado.append(parte)
    
    return ''.join(resultado)

# ============================================================================
# ROTAS
# ============================================================================

@app_liturgias.route('/')
def home():
    """Página principal de liturgias - Modal"""
    try:
        # Busca liturgia de hoje por padrão
        liturgia_hoje = get_liturgia_hoje()
        data_hoje = date.today().strftime('%Y-%m-%d')

        return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liturgias - Paróquia</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
            position: relative;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .sair-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background: rgba(231, 76, 60, 0.9);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }

        .sair-btn:hover {
            background: #e74c3c;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .date-selector {
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }

        .date-form {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }

        .date-input {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            flex: 1;
            min-width: 200px;
        }

        .btn {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .liturgia-content {
            padding: 30px;
            max-height: 60vh;
            overflow-y: auto;
        }

        .liturgia-item {
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 10px;
            background: #f8f9fa;
            border-left: 5px solid #667eea;
        }

        .liturgia-title {
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .liturgia-text {
            line-height: 1.8;
            color: #34495e;
            text-align: justify;
        }

        .no-data {
            text-align: center;
            padding: 50px;
            color: #7f8c8d;
        }

        .loading {
            text-align: center;
            padding: 50px;
            color: #7f8c8d;
        }

        .error {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }

        /* Estilo para scrollbar personalizada */
        .liturgia-content::-webkit-scrollbar {
            width: 8px;
        }

        .liturgia-content::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }

        .liturgia-content::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }

        .liturgia-content::-webkit-scrollbar-thumb:hover {
            background: #5a6fd8;
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .header h1 {
                font-size: 2em;
            }

            .header {
                padding: 20px;
            }

            .sair-btn {
                position: static;
                margin: 10px auto;
                display: block;
                width: fit-content;
            }

            .date-form {
                flex-direction: column;
            }

            .date-input {
                min-width: 100%;
            }

            .liturgia-content {
                padding: 20px;
                max-height: 50vh;
            }
        }

        /* Animação de entrada */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .container {
            animation: fadeInUp 0.6s ease-out;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <button class="sair-btn" onclick="fecharJanela()">❌ Sair</button>
            <h1>📖 Liturgias</h1>
            <p>Palavra de Deus para cada dia</p>
        </div>

        <div class="date-selector">
            <form class="date-form" id="dateForm">
                <input type="date" class="date-input" id="dataLiturgia" name="data" value="{{ data_hoje }}" required>
                <button type="submit" class="btn">Buscar Liturgia</button>
            </form>
        </div>

        <div class="liturgia-content" id="liturgiaContent">
            {% if liturgia_hoje %}
                {% for tipo, texto in liturgia_hoje.leituras.items() %}
                    <div class="liturgia-item">
                        <div class="liturgia-title">
                            {% if tipo == 'Primeira Leitura' %}
                                📖 Primeira Leitura
                            {% elif tipo == 'Segunda Leitura' %}
                                📖 Segunda Leitura
                            {% elif tipo == 'Salmo' %}
                                🎵 Salmo Responsorial
                            {% elif tipo == 'Evangelho' %}
                                ✝️ Evangelho
                            {% else %}
                                📖 {{ tipo }}
                            {% endif %}
                        </div>
                        <div class="liturgia-text">{{ texto | safe }}</div>
                    </div>
                {% endfor %}
            {% else %}
                <div class="no-data">
                    <h3>📅 {{ data_hoje }}</h3>
                    <p>Nenhuma liturgia encontrada para esta data.</p>
                    <p>Tente selecionar outra data ou verifique se há liturgia disponível.</p>
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        // Função para fechar a janela
        function fecharJanela() {
            // Tenta fechar como popup primeiro
            if (window.opener) {
                window.close();
            } else {
                // Se não for popup, redireciona para o site principal
                window.location.href = 'https://zap.oncristo.com.br/';
            }
        }

        // Adiciona listener para tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                fecharJanela();
            }
        });

        // Previne que o usuário saia acidentalmente
        window.addEventListener('beforeunload', function(e) {
            // Remove o aviso padrão para não incomodar o usuário
            // e.preventDefault();
            // e.returnValue = '';
        });

        document.getElementById('dateForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const data = document.getElementById('dataLiturgia').value;
            const content = document.getElementById('liturgiaContent');

            // Mostra loading
            content.innerHTML = '<div class="loading">Carregando liturgia...</div>';

            // Faz requisição AJAX
            fetch(`/api/liturgia/${data}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        content.innerHTML = `<div class="error">${data.error}</div>`;
                        return;
                    }

                    if (!data.leituras || Object.keys(data.leituras).length === 0) {
                        content.innerHTML = `
                            <div class="no-data">
                                <h3>📅 ${data.data}</h3>
                                <p>Nenhuma liturgia encontrada para esta data.</p>
                                <p>Tente selecionar outra data ou verifique se há liturgia disponível.</p>
                            </div>
                        `;
                        return;
                    }

                    // Renderiza as liturgias
                    let html = '';
                    for (const [tipo, texto] of Object.entries(data.leituras)) {
                        let icon = '📖';
                        let title = tipo;

                        if (tipo === 'Primeira Leitura') {
                            icon = '📖';
                            title = 'Primeira Leitura';
                        } else if (tipo === 'Segunda Leitura') {
                            icon = '📖';
                            title = 'Segunda Leitura';
                        } else if (tipo === 'Salmo') {
                            icon = '🎵';
                            title = 'Salmo Responsorial';
                        } else if (tipo === 'Evangelho') {
                            icon = '✝️';
                            title = 'Evangelho';
                        }

                        html += `
                            <div class="liturgia-item">
                                <div class="liturgia-title">
                                    ${icon} ${title}
                                </div>
                                <div class="liturgia-text">${texto}</div>
                            </div>
                        `;
                    }

                    content.innerHTML = html;
                })
                .catch(error => {
                    content.innerHTML = `<div class="error">Erro ao carregar liturgia: ${error.message}</div>`;
                });
        });

        // Auto-focus no campo de data
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('dataLiturgia').focus();
        });
    </script>
</body>
</html>
        ''', liturgia_hoje=liturgia_hoje, data_hoje=data_hoje)

    except Exception as e:
        logger.error(f"Erro na página de liturgias: {str(e)}")
        return f"Erro ao carregar página: {str(e)}", 500

@app_liturgias.route('/api/liturgia/<data>')
def api_liturgia(data):
    """API para buscar liturgia por data"""
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        liturgia = get_liturgia_por_data(data_obj)

        if not liturgia:
            return jsonify({"error": "Liturgia não encontrada"}), 404

        return jsonify(liturgia)

    except ValueError:
        return jsonify({"error": "Formato de data inválido"}), 400

@app_liturgias.route('/visualizar/<data>')
def visualizar_liturgia(data):
    """Página para visualizar liturgia específica"""
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        liturgia = get_liturgia_por_data(data_obj)

        if not liturgia:
            return "Liturgia não encontrada", 404

        return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liturgia {{ data }} - Paróquia</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .liturgia-content {
            padding: 30px;
        }

        .liturgia-item {
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 10px;
            background: #f8f9fa;
            border-left: 5px solid #667eea;
        }

        .liturgia-title {
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .liturgia-text {
            line-height: 1.8;
            color: #34495e;
            text-align: justify;
        }

        .voltar-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.9);
            color: #2c3e50;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }

        .voltar-btn:hover {
            background: white;
            transform: translateY(-2px);
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }

            .liturgia-content {
                padding: 20px;
            }

            .voltar-btn {
                position: static;
                margin: 20px;
                display: inline-block;
            }
        }
    </style>
</head>
<body>
    <a href="https://zap.oncristo.com.br/" class="voltar-btn">← Voltar ao Site</a>
    
    <div class="container">
        <div class="header">
            <h1>📖 Liturgia</h1>
            <p>{{ data }}</p>
        </div>

        <div class="liturgia-content">
            {% for tipo, texto in liturgia.leituras.items() %}
                <div class="liturgia-item">
                    <div class="liturgia-title">
                        {% if tipo == 'Primeira Leitura' %}
                            📖 Primeira Leitura
                        {% elif tipo == 'Segunda Leitura' %}
                            📖 Segunda Leitura
                        {% elif tipo == 'Salmo' %}
                            🎵 Salmo Responsorial
                        {% elif tipo == 'Evangelho' %}
                            ✝️ Evangelho
                        {% else %}
                            📖 {{ tipo }}
                        {% endif %}
                    </div>
                    <div class="liturgia-text">{{ texto | safe }}</div>
                </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        ''', liturgia=liturgia, data=data)

    except ValueError:
        return "Data inválida", 400
    except Exception as e:
        logger.error(f"Erro ao visualizar liturgia: {str(e)}")
        return f"Erro ao carregar liturgia: {str(e)}", 500 