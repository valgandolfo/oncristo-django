# Onde o Template Desenha a Tela - Gerenciar Coleta Dízimo

## Localização dos Elementos no Template

### 📍 **Container Principal (Borda Arredondada)**
**Linha 104:** `<form method="get" class="busca-campos form-coleta-wrapper">`
- A classe `form-coleta-wrapper` aplica:
  - Borda arredondada (border-radius: 12px)
  - Borda cinza (2px solid #dee2e6)
  - Fundo branco (#ffffff)
  - Sombra (box-shadow)
  - Padding interno (1.5rem)

---

### 📍 **Linha 1: Labels "Mês:" e "Ano:"**
**Linhas 106-109:**
```html
<div class="linha-busca linha-labels">
    <strong>Mês:</strong>
    <strong>Ano:</strong>
</div>
```
- Renderiza os labels "Mês:" e "Ano:" lado a lado
- CSS: `.linha-labels strong` (linha 34-38) define cor e tamanho

---

### 📍 **Linha 2: Select Mês, Input Ano e Botão BUSCAR**
**Linhas 112-126:**
```html
<div class="linha-busca">
    <div class="campo-input campo-mes">
        <select id="mes" name="mes" required>
            {% opcoes_mes mes incluir_todos=True %}
        </select>
    </div>
    <div class="campo-input campo-ano">
        <input type="number" id="ano" name="ano" value="{{ ano }}" ...>
    </div>
    <div class="campo-botao">
        <button type="submit" class="cont_busca_btnbusca">
            <i class="fas fa-search"></i> BUSCAR
        </button>
    </div>
</div>
```
- **Select Mês:** Linha 114-116 - Dropdown com meses (usa template tag `opcoes_mes`)
- **Input Ano:** Linha 119 - Campo numérico para ano
- **Botão BUSCAR:** Linha 122-124 - Botão de submit com ícone de busca
- CSS: `.campo-mes` (linha 50-53), `.campo-ano` (linha 55-57), `.campo-botao` (linha 64-66)

---

### 📍 **Linha 3: Label "Dizimista:"**
**Linhas 129-131:**
```html
<div class="linha-busca">
    <strong>Dizimista:</strong>
</div>
```
- Renderiza apenas o label "Dizimista:"
- Alinhado à esquerda, abaixo do campo Mês

---

### 📍 **Linha 4: Select Dizimista**
**Linhas 134-143:**
```html
<div class="linha-busca">
    <div class="campo-input campo-dizimista">
        <select id="dizimista" name="dizimista">
            <option value="">Todos</option>
            {% for dizimista in form.dizimista.queryset %}
                <option value="{{ dizimista.pk }}" ...>{{ dizimista.DIS_nome }}</option>
            {% endfor %}
        </select>
    </div>
</div>
```
- **Select Dizimista:** Linha 136-141 - Dropdown com lista de dizimistas
- Opção "Todos" como padrão (linha 137)
- Loop para carregar dizimistas do banco (linha 138-140)
- CSS: `.campo-dizimista` (linha 59-62) define largura máxima de 460px

---

### 📍 **Linha 5: Status com Radio Buttons**
**Linhas 146-164:**
```html
<div class="linha-busca linha-status">
    <strong>Status:</strong>
    <label>
        <input type="radio" name="status" value="TODOS" ...>
        Todos
    </label>
    <label>
        <input type="radio" name="status" value="PAGOS" ...>
        Pagos
    </label>
    <label>
        <input type="radio" name="status" value="EM_ABERTO" ...>
        em Aberto
    </label>
    <label>
        <input type="radio" name="status" value="PARCIAL" ...>
        Parcialmente
    </label>
</div>
```
- **Label "Status:"** - Linha 147
- **Radio "Todos"** - Linha 149-150
- **Radio "Pagos"** - Linha 153-154
- **Radio "em Aberto"** - Linha 157-158
- **Radio "Parcialmente"** - Linha 161-162
- CSS: `.linha-status` (linha 74-76) e `.linha-status label` (linha 78-84)

---

## CSS que Define o Visual

### **Container Principal** (Linhas 13-23)
```css
.form-coleta-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    background: #ffffff;
    border: 2px solid #dee2e6;
    border-radius: 12px;        /* ← BORDAS ARREDONDADAS */
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    margin-bottom: 1.5rem;
}
```

### **Linhas do Formulário** (Linhas 25-32)
```css
.linha-busca {
    display: flex;
    gap: 1.25rem;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-start;  /* ← ALINHAMENTO À ESQUERDA */
    padding: 0.5rem 0;
}
```

### **Campos de Input/Select** (Linhas 40-48)
```css
.campo-input select,
.campo-input input {
    width: 100%;
    border: 1px solid #c8d1da;
    border-radius: 6px;          /* ← BORDAS ARREDONDADAS NOS CAMPOS */
    padding: 0.45rem 0.75rem;
    background-color: #fff;
    font-size: 0.95rem;
}
```

---

## Resumo Visual

```
┌─────────────────────────────────────────────────────────┐
│  <form class="form-coleta-wrapper">  ← LINHA 104        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  <div class="linha-busca linha-labels">          │   │
│  │    <strong>Mês:</strong>  ← LINHA 107            │   │
│  │    <strong>Ano:</strong>  ← LINHA 108            │   │
│  │  </div>                                           │   │
│  │                                                    │   │
│  │  <div class="linha-busca">                        │   │
│  │    <select id="mes">  ← LINHA 114                │   │
│  │    <input id="ano">   ← LINHA 119                │   │
│  │    <button BUSCAR>    ← LINHA 122                │   │
│  │  </div>                                           │   │
│  │                                                    │   │
│  │  <div class="linha-busca">                        │   │
│  │    <strong>Dizimista:</strong>  ← LINHA 130      │   │
│  │  </div>                                           │   │
│  │                                                    │   │
│  │  <div class="linha-busca">                        │   │
│  │    <select id="dizimista">  ← LINHA 136          │   │
│  │  </div>                                           │   │
│  │                                                    │   │
│  │  <div class="linha-busca linha-status">          │   │
│  │    <strong>Status:</strong>  ← LINHA 147        │   │
│  │    <input type="radio"> Todos  ← LINHA 149       │   │
│  │    <input type="radio"> Pagos  ← LINHA 153       │   │
│  │    <input type="radio"> em Aberto  ← LINHA 157   │   │
│  │    <input type="radio"> Parcialmente  ← LINHA 161│   │
│  │  </div>                                           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Onde Cada Elemento Aparece na Tela

1. **Container com bordas arredondadas:** Linha 104 (`form-coleta-wrapper`)
2. **Labels Mês/Ano:** Linhas 107-108
3. **Select Mês:** Linha 114
4. **Input Ano:** Linha 119
5. **Botão BUSCAR:** Linha 122
6. **Label Dizimista:** Linha 130
7. **Select Dizimista:** Linha 136
8. **Label Status:** Linha 147
9. **Radio Buttons:** Linhas 149, 153, 157, 161

