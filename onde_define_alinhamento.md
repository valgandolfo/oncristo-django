# Onde Define o Alinhamento (Esquerda/Direita)

## Propriedades CSS que Controlam o Alinhamento

### 📍 **Alinhamento Horizontal (Esquerda/Direita)**

#### **1. `justify-content: flex-start` - LINHA 30**
```css
.linha-busca {
    display: flex;
    gap: 1.25rem;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-start;  /* ← ALINHA À ESQUERDA */
    padding: 0.5rem 0;
}
```
- **Localização:** Linha 30 do template
- **O que faz:** Alinha todos os elementos dentro de `.linha-busca` à **ESQUERDA**
- **Valores possíveis:**
  - `flex-start` = Esquerda ✅ (atual)
  - `flex-end` = Direita
  - `center` = Centro
  - `space-between` = Espaçado entre elementos

---

#### **2. `margin-right: auto` - LINHA 65**
```css
.campo-botao {
    margin-right: auto;  /* ← EMPURRA O BOTÃO PARA A DIREITA */
}
```
- **Localização:** Linha 65 do template
- **O que faz:** Empurra o botão BUSCAR para a **DIREITA** (mas não está funcionando como esperado)
- **Problema:** O `justify-content: flex-start` na linha 30 está forçando tudo à esquerda

---

### 📍 **Alinhamento Vertical (Topo/Meio/Baixo)**

#### **3. `align-items: center` - LINHAS 29, 70, 80**
```css
.linha-busca {
    align-items: center;  /* ← ALINHA VERTICALMENTE NO CENTRO */
}
```
- **Localização:** Linha 29 do template
- **O que faz:** Alinha os elementos verticalmente no **CENTRO** da linha
- **Valores possíveis:**
  - `center` = Centro ✅ (atual)
  - `flex-start` = Topo
  - `flex-end` = Baixo
  - `stretch` = Estica para preencher

---

## Como Mudar o Alinhamento

### **Para Alinhar TUDO à DIREITA:**
```css
.linha-busca {
    justify-content: flex-end;  /* ← MUDAR DE flex-start PARA flex-end */
}
```

### **Para Alinhar TUDO ao CENTRO:**
```css
.linha-busca {
    justify-content: center;  /* ← MUDAR PARA center */
}
```

### **Para Alinhar o Botão BUSCAR à DIREITA (mantendo outros à esquerda):**
```css
.campo-botao {
    margin-left: auto;  /* ← MUDAR DE margin-right PARA margin-left */
    margin-right: 0;    /* ← REMOVER margin-right */
}
```

---

## Resumo das Propriedades de Alinhamento

| Propriedade | Linha | Valor Atual | Efeito |
|------------|-------|-------------|--------|
| `justify-content` | 30 | `flex-start` | Alinha elementos à **ESQUERDA** horizontalmente |
| `align-items` | 29 | `center` | Alinha elementos no **CENTRO** verticalmente |
| `margin-right` | 65 | `auto` | Tenta empurrar botão para direita (mas não funciona por causa do `flex-start`) |

---

## Onde Está Definido no Template

```
Linha 25-32: .linha-busca
    ├─ justify-content: flex-start  ← ALINHAMENTO HORIZONTAL (ESQUERDA)
    └─ align-items: center         ← ALINHAMENTO VERTICAL (CENTRO)

Linha 64-66: .campo-botao
    └─ margin-right: auto          ← TENTA EMPURRAR BOTÃO PARA DIREITA
```

---

## Para Alinhar o Botão BUSCAR à Direita (Correção)

**Opção 1:** Mudar `margin-right` para `margin-left`:
```css
.campo-botao {
    margin-left: auto;   /* ← EMPURRA PARA DIREITA */
    margin-right: 0;     /* ← REMOVE MARGEM DIREITA */
}
```

**Opção 2:** Manter `justify-content: flex-start` mas adicionar `margin-left: auto` no botão:
```css
.campo-botao {
    margin-left: auto;  /* ← ISSO EMPURRA O BOTÃO PARA A DIREITA */
}
```

