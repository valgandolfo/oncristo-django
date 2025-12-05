/**
 * Funções Globais Reutilizáveis - DRY Principle
 * Sistema On Cristo
 */

// ============================================================================
// CONSTANTES GLOBAIS
// ============================================================================

const GLOBAL_CONSTANTS = {
    MESES: [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ],
    
    DIAS_SEMANA: [
        'Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira',
        'Quinta-feira', 'Sexta-feira', 'Sábado'
    ],
    
    ESTADOS_UF: {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
        'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
        'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    },
    
    STATUS_COLABORADOR: {
        'ATIVO': { label: 'Ativo', class: 'bg-success' },
        'PENDENTE': { label: 'Pendente', class: 'bg-warning' },
        'INATIVO': { label: 'Inativo', class: 'bg-danger' }
    },
    
    SEXO: {
        'M': 'Masculino',
        'F': 'Feminino'
    }
};

// ============================================================================
// FUNÇÕES DE FORMATAÇÃO
// ============================================================================

/**
 * Formata data para exibição brasileira
 * @param {Date|string} data - Data para formatar
 * @param {string} formato - Formato desejado (padrão: 'dd/mm/yyyy')
 * @returns {string} Data formatada
 */
function formatarData(data, formato = 'dd/mm/yyyy') {
    if (!data) return 'Não informado';
    
    const dataObj = new Date(data);
    if (isNaN(dataObj.getTime())) return 'Data inválida';
    
    const dia = String(dataObj.getDate()).padStart(2, '0');
    const mes = String(dataObj.getMonth() + 1).padStart(2, '0');
    const ano = dataObj.getFullYear();
    const hora = String(dataObj.getHours()).padStart(2, '0');
    const minuto = String(dataObj.getMinutes()).padStart(2, '0');
    
    switch (formato) {
        case 'dd/mm/yyyy':
            return `${dia}/${mes}/${ano}`;
        case 'dd/mm/yyyy hh:mm':
            return `${dia}/${mes}/${ano} ${hora}:${minuto}`;
        case 'dd de mês de yyyy':
            return `${dia} de ${GLOBAL_CONSTANTS.MESES[dataObj.getMonth()]} de ${ano}`;
        case 'dia da semana, dd de mês de yyyy':
            return `${GLOBAL_CONSTANTS.DIAS_SEMANA[dataObj.getDay()]}, ${dia} de ${GLOBAL_CONSTANTS.MESES[dataObj.getMonth()]} de ${ano}`;
        default:
            return `${dia}/${mes}/${ano}`;
    }
}

/**
 * Formata telefone brasileiro
 * @param {string} telefone - Telefone para formatar
 * @returns {string} Telefone formatado
 */
function formatarTelefone(telefone) {
    if (!telefone) return 'Não informado';
    
    const numeros = telefone.replace(/\D/g, '');
    
    if (numeros.length === 11) {
        return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 7)}-${numeros.slice(7)}`;
    } else if (numeros.length === 10) {
        return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 6)}-${numeros.slice(6)}`;
    }
    
    return telefone;
}

/**
 * Formata CEP brasileiro
 * @param {string} cep - CEP para formatar
 * @returns {string} CEP formatado
 */
function formatarCEP(cep) {
    if (!cep) return 'Não informado';
    
    const numeros = cep.replace(/\D/g, '');
    if (numeros.length === 8) {
        return `${numeros.slice(0, 5)}-${numeros.slice(5)}`;
    }
    
    return cep;
}

/**
 * Formata CPF brasileiro
 * @param {string} cpf - CPF para formatar
 * @returns {string} CPF formatado
 */
function formatarCPF(cpf) {
    if (!cpf) return 'Não informado';
    
    const numeros = cpf.replace(/\D/g, '');
    if (numeros.length === 11) {
        return `${numeros.slice(0, 3)}.${numeros.slice(3, 6)}.${numeros.slice(6, 9)}-${numeros.slice(9)}`;
    }
    
    return cpf;
}

// ============================================================================
// FUNÇÕES DE VALIDAÇÃO
// ============================================================================

/**
 * Valida CPF brasileiro
 * @param {string} cpf - CPF para validar
 * @returns {boolean} True se válido
 */
function validarCPF(cpf) {
    if (!cpf) return false;
    
    const numeros = cpf.replace(/\D/g, '');
    if (numeros.length !== 11) return false;
    
    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(numeros)) return false;
    
    // Validar dígitos verificadores
    let soma = 0;
    for (let i = 0; i < 9; i++) {
        soma += parseInt(numeros[i]) * (10 - i);
    }
    let resto = soma % 11;
    let digito1 = resto < 2 ? 0 : 11 - resto;
    
    if (parseInt(numeros[9]) !== digito1) return false;
    
    soma = 0;
    for (let i = 0; i < 10; i++) {
        soma += parseInt(numeros[i]) * (11 - i);
    }
    resto = soma % 11;
    let digito2 = resto < 2 ? 0 : 11 - resto;
    
    return parseInt(numeros[10]) === digito2;
}

/**
 * Valida CEP brasileiro
 * @param {string} cep - CEP para validar
 * @returns {boolean} True se válido
 */
function validarCEP(cep) {
    if (!cep) return false;
    
    const numeros = cep.replace(/\D/g, '');
    return numeros.length === 8 && /^\d{8}$/.test(numeros);
}

/**
 * Valida email
 * @param {string} email - Email para validar
 * @returns {boolean} True se válido
 */
function validarEmail(email) {
    if (!email) return false;
    
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// ============================================================================
// FUNÇÕES DE UTILIDADE
// ============================================================================

/**
 * Obtém nome completo do estado pela UF
 * @param {string} uf - UF do estado
 * @returns {string} Nome completo do estado
 */
function obterNomeEstado(uf) {
    return GLOBAL_CONSTANTS.ESTADOS_UF[uf] || uf;
}

/**
 * Obtém nome do mês pelo número
 * @param {number} numeroMes - Número do mês (1-12)
 * @returns {string} Nome do mês
 */
function obterNomeMes(numeroMes) {
    return GLOBAL_CONSTANTS.MESES[numeroMes - 1] || 'Mês inválido';
}

/**
 * Obtém nome do dia da semana pelo número
 * @param {number} numeroDia - Número do dia (0-6, onde 0 = domingo)
 * @returns {string} Nome do dia da semana
 */
function obterNomeDiaSemana(numeroDia) {
    return GLOBAL_CONSTANTS.DIAS_SEMANA[numeroDia] || 'Dia inválido';
}

/**
 * Cria badge Bootstrap para status
 * @param {string} status - Status do colaborador
 * @returns {string} HTML do badge
 */
function criarBadgeStatus(status) {
    const statusInfo = GLOBAL_CONSTANTS.STATUS_COLABORADOR[status];
    if (!statusInfo) return `<span class="badge bg-secondary">${status}</span>`;
    
    return `<span class="badge ${statusInfo.class}">${statusInfo.label}</span>`;
}

/**
 * Cria badge Bootstrap para sexo
 * @param {string} sexo - Sexo (M/F)
 * @returns {string} HTML do badge
 */
function criarBadgeSexo(sexo) {
    const sexoInfo = GLOBAL_CONSTANTS.SEXO[sexo];
    if (!sexoInfo) return `<span class="badge bg-secondary">Não informado</span>`;
    
    return `<span class="badge bg-info">${sexoInfo}</span>`;
}

// ============================================================================
// FUNÇÕES DE FORMATAÇÃO DE ENDEREÇO
// ============================================================================

/**
 * Formata endereço completo
 * @param {Object} endereco - Objeto com dados do endereço
 * @returns {string} Endereço formatado
 */
function formatarEnderecoCompleto(endereco) {
    if (!endereco) return 'Não informado';
    
    const partes = [];
    
    if (endereco.endereco) {
        let enderecoCompleto = endereco.endereco;
        if (endereco.numero) enderecoCompleto += `, ${endereco.numero}`;
        if (endereco.complemento) enderecoCompleto += `, ${endereco.complemento}`;
        partes.push(enderecoCompleto);
    }
    
    if (endereco.bairro) partes.push(endereco.bairro);
    if (endereco.cidade) partes.push(endereco.cidade);
    if (endereco.estado) partes.push(endereco.estado);
    if (endereco.cep) partes.push(formatarCEP(endereco.cep));
    
    return partes.length > 0 ? partes.join(' - ') : 'Não informado';
}

// ============================================================================
// FUNÇÕES DE NOTIFICAÇÃO
// ============================================================================

/**
 * Exibe notificação toast
 * @param {string} mensagem - Mensagem para exibir
 * @param {string} tipo - Tipo da notificação (success, error, warning, info)
 * @param {number} duracao - Duração em milissegundos (padrão: 3000)
 */
function exibirNotificacao(mensagem, tipo = 'info', duracao = 3000) {
    // Criar container de notificações se não existir
    let container = document.getElementById('notificacoes-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificacoes-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Criar notificação
    const notificacao = document.createElement('div');
    notificacao.className = `alert alert-${tipo} alert-dismissible fade show`;
    notificacao.style.cssText = `
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    `;
    
    notificacao.innerHTML = `
        <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'exclamation-circle' : tipo === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notificacao);
    
    // Remover automaticamente após a duração especificada
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.remove();
        }
    }, duracao);
}

// ============================================================================
// FUNÇÕES DE FORMATAÇÃO DE TABELA
// ============================================================================

/**
 * Formata dados de colaborador para exibição em tabela
 * @param {Object} colaborador - Dados do colaborador
 * @returns {Object} Dados formatados
 */
function formatarDadosColaborador(colaborador) {
    return {
        id: colaborador.COL_id || 'N/A',
        nome: colaborador.COL_nome_completo || 'Não informado',
        telefone: formatarTelefone(colaborador.COL_telefone),
        status: criarBadgeStatus(colaborador.COL_status),
        sexo: criarBadgeSexo(colaborador.COL_sexo),
        dataNascimento: formatarData(colaborador.COL_data_nascimento),
        dataCadastro: formatarData(colaborador.COL_data_cadastro),
        endereco: formatarEnderecoCompleto({
            endereco: colaborador.COL_endereco,
            numero: colaborador.COL_numero,
            complemento: colaborador.COL_complemento,
            bairro: colaborador.COL_bairro,
            cidade: colaborador.COL_cidade,
            estado: colaborador.COL_estado,
            cep: colaborador.COL_cep
        })
    };
}

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

// Disponibilizar funções globalmente
window.GlobalUtils = {
    formatarData,
    formatarTelefone,
    formatarCEP,
    formatarCPF,
    validarCPF,
    validarCEP,
    validarEmail,
    obterNomeEstado,
    obterNomeMes,
    obterNomeDiaSemana,
    criarBadgeStatus,
    criarBadgeSexo,
    formatarEnderecoCompleto,
    exibirNotificacao,
    formatarDadosColaborador,
    CONSTANTS: GLOBAL_CONSTANTS
};

// Log de inicialização
console.log('🚀 GlobalUtils carregado com sucesso!');
console.log('📋 Funções disponíveis:', Object.keys(window.GlobalUtils));
