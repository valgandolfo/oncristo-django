// ==================== FUNÇÕES GLOBAIS PARA FORMULÁRIOS ====================
// Biblioteca de funções reutilizáveis para formulários

/**
 * Busca dados do CEP usando a API ViaCEP (JSONP)
 * @param {string} cep - CEP a ser buscado (com ou sem formatação)
 * @param {Object} campos - Objeto com IDs dos campos para preenchimento
 * @param {string} campos.endereco - ID do campo endereço (pode ser 'id_PAR_endereco' ou 'PAR_endereco')
 * @param {string} campos.bairro - ID do campo bairro
 * @param {string} campos.cidade - ID do campo cidade
 * @param {string} campos.estado - ID do campo estado (ou 'uf')
 * @param {Function} callback - Função de callback (opcional)
 */
function buscarCep(cep, campos = {}, callback = null) {
    console.log('🔍 Buscando CEP:', cep);
    
    // Limpa o CEP (remove formatação)
    const cepLimpo = cep.replace(/\D/g, '');
    console.log('🔍 CEP limpo:', cepLimpo);
    
    // Valida se o CEP tem 8 dígitos
    if (cepLimpo.length !== 8) {
        console.warn('❌ CEP deve ter 8 dígitos');
        if (callback) callback({ erro: 'CEP deve ter 8 dígitos' });
        return;
    }
    
    // Função global temporária para callback JSONP
    const callbackName = 'buscarCepCallback_' + Date.now();
    window[callbackName] = function(conteudo) {
        console.log('📋 Dados recebidos do ViaCEP:', conteudo);
        
        // Remove a função temporária
        delete window[callbackName];
        document.body.removeChild(script);
        
        if (!("erro" in conteudo)) {
            console.log('✅ Preenchendo campos...');
            
            // Função auxiliar para encontrar campo por múltiplos métodos
            const encontrarCampo = function(id) {
                return document.getElementById('id_' + id) || 
                       document.getElementById(id) ||
                       document.querySelector('[name="' + id + '"]');
            };
            
            // Preenche os campos automaticamente
            if (campos.endereco) {
                const campoEndereco = encontrarCampo(campos.endereco);
                if (campoEndereco) {
                    campoEndereco.value = conteudo.logradouro || '';
                    console.log('📍 Endereço preenchido:', conteudo.logradouro);
                }
            }
            
            if (campos.bairro) {
                const campoBairro = encontrarCampo(campos.bairro);
                if (campoBairro) {
                    campoBairro.value = conteudo.bairro || '';
                    console.log('🏘️ Bairro preenchido:', conteudo.bairro);
                }
            }
            
            if (campos.cidade) {
                const campoCidade = encontrarCampo(campos.cidade);
                if (campoCidade) {
                    campoCidade.value = conteudo.localidade || '';
                    console.log('🏙️ Cidade preenchida:', conteudo.localidade);
                }
            }
            
            if (campos.estado || campos.uf) {
                const campoEstado = encontrarCampo(campos.estado || campos.uf);
                if (campoEstado) {
                    campoEstado.value = conteudo.uf || '';
                    console.log('🗺️ Estado preenchido:', conteudo.uf);
                }
            }
            
            // Callback de sucesso
            if (callback) callback(conteudo);
        } else {
            console.warn('❌ Erro ao buscar CEP:', conteudo.erro);
            alert('CEP não encontrado');
            if (callback) callback({ erro: conteudo.erro });
        }
    };
    
    // Cria script JSONP
    const script = document.createElement('script');
    script.src = 'https://viacep.com.br/ws/' + cepLimpo + '/json/?callback=' + callbackName;
    script.onerror = function() {
        console.error('💥 Erro ao carregar script ViaCEP');
        delete window[callbackName];
        if (callback) callback({ erro: 'Erro na requisição' });
    };
    document.body.appendChild(script);
}

/**
 * Verifica se um telefone já está cadastrado
 * @param {string} telefone - Telefone a ser verificado
 * @param {string} campoId - ID do campo de telefone
 * @param {Function} callback - Função de callback (opcional)
 */
function verificarTelefone(telefone, campoId = 'DIS_telefone', callback = null) {
    const telefoneLimpo = telefone.replace(/\D/g, '');
    
    if (telefoneLimpo.length < 10) {
        console.warn('Telefone deve ter pelo menos 10 dígitos');
        if (callback) callback({ existe: false, erro: 'Telefone inválido' });
        return;
    }
    
    fetch(`/app_igreja/verificar-telefone/?telefone=${telefoneLimpo}`)
    .then(response => response.json())
    .then(data => {
        const campoTelefone = document.getElementById(campoId);
        
        if (data.existe && campoTelefone) {
            campoTelefone.setCustomValidity('Este telefone já está cadastrado');
            campoTelefone.reportValidity();
        } else if (campoTelefone) {
            campoTelefone.setCustomValidity('');
        }
        
        if (callback) callback(data);
    })
    .catch(error => {
        console.error('Erro ao verificar telefone:', error);
        if (callback) callback({ existe: false, erro: 'Erro na verificação' });
    });
}

/**
 * Aplica máscara de telefone
 * @param {string} valor - Valor a ser formatado
 * @returns {string} - Valor formatado
 */
function mascaraTelefone(valor) {
    const numeros = valor.replace(/\D/g, '');
    
    if (numeros.length <= 10) {
        return numeros.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    } else if (numeros.length <= 11) {
        return numeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
    
    return numeros.substring(0, 11).replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
}

/**
 * Aplica máscara de CEP
 * @param {string} valor - Valor a ser formatado
 * @returns {string} - Valor formatado
 */
function mascaraCep(valor) {
    const numeros = valor.replace(/\D/g, '');
    return numeros.substring(0, 8).replace(/(\d{5})(\d{3})/, '$1-$2');
}

/**
 * Aplica máscara de CPF
 * @param {string} valor - Valor a ser formatado
 * @returns {string} - Valor formatado
 */
function mascaraCpf(valor) {
    const numeros = valor.replace(/\D/g, '');
    return numeros.substring(0, 11).replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

/**
 * Aplica máscara de CNPJ
 * @param {string} valor - Valor a ser formatado
 * @returns {string} - Valor formatado
 */
function mascaraCnpj(valor) {
    const numeros = valor.replace(/\D/g, '');
    if (numeros.length <= 14) {
        return numeros.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    return numeros.substring(0, 14).replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
}

/**
 * Valida CPF
 * @param {string} cpf - CPF a ser validado
 * @returns {boolean} - True se válido
 */
function validarCpf(cpf) {
    const numeros = cpf.replace(/\D/g, '');
    
    if (numeros.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(numeros)) return false; // Todos os dígitos iguais
    
    let soma = 0;
    for (let i = 0; i < 9; i++) {
        soma += parseInt(numeros.charAt(i)) * (10 - i);
    }
    let resto = 11 - (soma % 11);
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(numeros.charAt(9))) return false;
    
    soma = 0;
    for (let i = 0; i < 10; i++) {
        soma += parseInt(numeros.charAt(i)) * (11 - i);
    }
    resto = 11 - (soma % 11);
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(numeros.charAt(10))) return false;
    
    return true;
}

/**
 * Preview de foto
 * @param {HTMLInputElement} input - Input de arquivo
 * @param {string} previewId - ID do elemento de preview
 */
function previewFoto(input, previewId = 'foto-preview') {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            const img = preview.querySelector('img');
            if (img) {
                img.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Função auxiliar para encontrar campo por múltiplos métodos
 * @param {string} id - ID ou nome do campo (sem prefixo 'id_')
 * @returns {HTMLElement|null} - Elemento encontrado ou null
 */
function encontrarCampo(id) {
    return document.getElementById('id_' + id) || 
           document.getElementById(id) ||
           document.querySelector('[name="' + id + '"]');
}

/**
 * Inicializa máscaras para campos específicos
 * @param {Object} config - Objeto de configuração
 * @param {Object} config.campos - IDs dos campos (telefone, cep, cpf, cnpj)
 * @param {Object} config.cepCampos - Campos para preenchimento automático do CEP (endereco, bairro, cidade, estado/uf)
 * @param {boolean} config.verificarTelefone - Se deve verificar telefone duplicado (padrão: false)
 */
function inicializarMascaras(config = {}) {
    console.log('🚀 Inicializando máscaras...', config);
    
    const campos = config.campos || {};
    const cepCampos = config.cepCampos || {};
    const verificarTelefoneFlag = config.verificarTelefone || false;
    
    // Máscara do telefone
    if (campos.telefone) {
        const campo = encontrarCampo(campos.telefone);
        if (campo) {
            console.log('✅ Configurando máscara para Telefone:', campos.telefone);
            campo.addEventListener('input', function(e) {
                e.target.value = mascaraTelefone(e.target.value);
            });
            if (verificarTelefoneFlag) {
                campo.addEventListener('blur', function(e) {
                    verificarTelefone(e.target.value, campos.telefone);
                });
            }
        } else {
            console.warn('❌ Campo Telefone não encontrado:', campos.telefone);
        }
    }
    
    // Máscara do CEP
    if (campos.cep) {
        const campo = encontrarCampo(campos.cep);
        if (campo) {
            console.log('✅ Configurando máscara para CEP:', campos.cep);
            campo.addEventListener('input', function(e) {
                e.target.value = mascaraCep(e.target.value);
            });
            campo.addEventListener('blur', function(e) {
                const cep = e.target.value.replace(/\D/g, '');
                if (cep.length === 8) {
                    buscarCep(e.target.value, cepCampos);
                }
            });
        } else {
            console.warn('❌ Campo CEP não encontrado:', campos.cep);
        }
    }
    
    // Máscara do CPF
    if (campos.cpf) {
        const campo = encontrarCampo(campos.cpf);
        if (campo) {
            console.log('✅ Configurando máscara para CPF:', campos.cpf);
            campo.addEventListener('input', function(e) {
                e.target.value = mascaraCpf(e.target.value);
            });
        } else {
            console.warn('❌ Campo CPF não encontrado:', campos.cpf);
        }
    }
    
    // Máscara do CNPJ
    if (campos.cnpj) {
        const campo = encontrarCampo(campos.cnpj);
        if (campo) {
            console.log('✅ Configurando máscara para CNPJ:', campos.cnpj);
            campo.addEventListener('input', function(e) {
                e.target.value = mascaraCnpj(e.target.value);
            });
        } else {
            console.warn('❌ Campo CNPJ não encontrado:', campos.cnpj);
        }
    }
}

// ==================== EXEMPLO DE USO ====================
/*
// Uso básico - campos padrão
inicializarMascaras();

// Uso personalizado - campos específicos
inicializarMascaras({
    telefone: 'meu_telefone',
    cep: 'meu_cep',
    cpf: 'meu_cpf'
});

// Buscar CEP manualmente
buscarCep('12345678', {
    endereco: 'meu_endereco',
    bairro: 'meu_bairro'
});

// Verificar telefone manualmente
verificarTelefone('11999999999', 'meu_telefone');

// Preview de foto
const inputFoto = document.getElementById('foto');
previewFoto(inputFoto, 'meu_preview');
*/
