# Layout - Gerenciar Coleta Dízimo

## Representação Visual do Formulário de Busca

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  Mês:                    Ano:                                        │  │
│  │  [Novembro ▼]            [2025]        [🔍 BUSCAR]                    │  │
│  │                                                                       │  │
│  │  Dizimista:                                                          │  │
│  │  [Todos ▼]                                                           │  │
│  │                                                                       │  │
│  │  Status:  (•) Todos  ( ) Pagos  ( ) em Aberto  ( ) Parcialmente     │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Estrutura

### Labels
```
Mês:                    Ano:
```

### Campos e Botão
```
[Novembro ▼]            [2025]        [🔍 BUSCAR]
```

### Label Dizimista
```
Dizimista:
```

### Select Dizimista
```
[Todos ▼]
```

### Status (Radio Buttons)
```
Status:  (•) Todos  ( ) Pagos  ( ) em Aberto  ( ) Parcialmente
```

## Características Visuais

- **Container**: Borda arredondada (border-radius: 12px)
- **Fundo**: Branco (#ffffff)
- **Borda**: Cinza claro (#dee2e6) com 2px
- **Sombra**: Box-shadow sutil para profundidade
- **Padding**: 1.5rem interno
- **Espaçamento**: Gap de 0.85rem entre linhas

## Alinhamento

- Todos os campos alinhados à **esquerda**
- Botão BUSCAR na mesma linha dos campos Mês e Ano
- Campo Dizimista abaixo do campo Mês, alinhado à esquerda
- Radio buttons de Status na mesma linha, alinhados à esquerda

