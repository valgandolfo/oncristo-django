/**
 * Função para busca automática de CEP
 * Reutilizável em qualquer formulário
 */

class CEPAutomation {
    constructor(options = {}) {
        this.options = {
            cepField: 'cep',
            logradouroField: 'logradouro',
            cidadeField: 'cidade',
            ufField: 'uf',
            bairroField: 'bairro',
            numeroField: 'numero',
            ...options
        };
        
        this.init();
    }
    
    init() {
        // Encontrar todos os campos de CEP na página
        const cepFields = document.querySelectorAll(`input[id*="${this.options.cepField}"], input[name*="${this.options.cepField}"]`);
        
        cepFields.forEach(cepField => {
            this.setupCEPField(cepField);
        });
        
        // Configurar máscara para CPF
        this.setupCPFMask();
        
        // Configurar máscara para telefone
        this.setupTelefoneMask();
    }
    
    setupCEPField(cepField) {
        // Máscara do CEP
        cepField.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) {
                value = value.substring(0, 8);
            }
            if (value.length > 5) {
                value = value.substring(0, 5) + '-' + value.substring(5);
            }
            e.target.value = value;
        });
        
        // Busca automática do CEP
        cepField.addEventListener('blur', (e) => {
            const cep = e.target.value.replace(/\D/g, '');
            if (cep.length === 8) {
                this.buscarCEP(cep, cepField);
            }
        });
    }
    
    buscarCEP(cep, cepField) {
        console.log('🔍 Buscando CEP:', cep);
        
        // Mostrar loading
        this.showLoading(cepField);
        
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                console.log('📡 Resposta da API:', data);
                
                if (!data.erro) {
                    this.preencherCampos(data, cepField);
                    console.log('🎉 CEP encontrado e preenchido com sucesso!');
                } else {
                    console.log('❌ CEP não encontrado');
                    this.showError(cepField, 'CEP não encontrado. Verifique o número digitado.');
                }
            })
            .catch(error => {
                console.error('💥 Erro ao buscar CEP:', error);
                this.showError(cepField, 'Erro ao buscar CEP. Tente novamente.');
            })
            .finally(() => {
                this.hideLoading(cepField);
            });
    }
    
    preencherCampos(data, cepField) {
        // Encontrar campos relacionados baseado no ID do campo CEP
        const fieldPrefix = this.getFieldPrefix(cepField);
        
        const campos = {
            logradouro: document.getElementById(`${fieldPrefix}_${this.options.logradouroField}`) || 
                       document.getElementById(`${fieldPrefix}_endereco`),
            cidade: document.getElementById(`${fieldPrefix}_${this.options.cidadeField}`),
            uf: document.getElementById(`${fieldPrefix}_${this.options.ufField}`),
            bairro: document.getElementById(`${fieldPrefix}_${this.options.bairroField}`),
            numero: document.getElementById(`${fieldPrefix}_${this.options.numeroField}`)
        };
        
        console.log('🎯 Campos encontrados:', campos);
        
        // Preencher campos automaticamente
        if (campos.logradouro) {
            campos.logradouro.value = `${data.logradouro}, ${data.bairro}`;
            console.log('✅ Endereço preenchido:', campos.logradouro.value);
        }
        
        if (campos.cidade) {
            campos.cidade.value = data.localidade;
            console.log('✅ Cidade preenchida:', campos.cidade.value);
        }
        
        if (campos.uf) {
            campos.uf.value = data.uf;
            console.log('✅ UF preenchida:', campos.uf.value);
        }
        
        if (campos.bairro) {
            campos.bairro.value = data.bairro;
            console.log('✅ Bairro preenchido:', campos.bairro.value);
        }
    }
    
    getFieldPrefix(cepField) {
        // Extrair prefixo do campo CEP (ex: PAR_cep -> PAR)
        const id = cepField.id;
        const parts = id.split('_');
        return parts.length > 1 ? parts[0] : '';
    }
    
    showLoading(cepField) {
        // Adicionar indicador de loading
        const loading = document.createElement('span');
        loading.className = 'cep-loading';
        loading.innerHTML = ' <i class="fas fa-spinner fa-spin"></i>';
        loading.style.color = '#007bff';
        cepField.parentNode.appendChild(loading);
    }
    
    hideLoading(cepField) {
        // Remover indicador de loading
        const loading = cepField.parentNode.querySelector('.cep-loading');
        if (loading) {
            loading.remove();
        }
    }
    
    showError(cepField, message) {
        // Mostrar erro
        const error = document.createElement('div');
        error.className = 'cep-error text-danger small mt-1';
        error.textContent = message;
        cepField.parentNode.appendChild(error);
        
        // Remover erro após 5 segundos
        setTimeout(() => {
            if (error.parentNode) {
                error.remove();
            }
        }, 5000);
    }
    
    setupCPFMask() {
        // Encontrar todos os campos de CPF na página
        const cpfFields = document.querySelectorAll('input[id*="cpf"], input[name*="cpf"], input[id*="CPF"], input[name*="CPF"]');
        
        cpfFields.forEach(cpfField => {
            // Máscara do CPF
            cpfField.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                
                // Limitar a 11 dígitos
                if (value.length > 11) {
                    value = value.substring(0, 11);
                }
                
                // Aplicar máscara 999.999.999-99
                if (value.length > 9) {
                    value = value.substring(0, 3) + '.' + 
                           value.substring(3, 6) + '.' + 
                           value.substring(6, 9) + '-' + 
                           value.substring(9);
                } else if (value.length > 6) {
                    value = value.substring(0, 3) + '.' + 
                           value.substring(3, 6) + '.' + 
                           value.substring(6);
                } else if (value.length > 3) {
                    value = value.substring(0, 3) + '.' + 
                           value.substring(3);
                }
                
                e.target.value = value;
            });
            
            // Validação básica do CPF
            cpfField.addEventListener('blur', (e) => {
                const cpf = e.target.value.replace(/\D/g, '');
                if (cpf.length === 11) {
                    if (!this.validarCPF(cpf)) {
                        this.showCPFError(cpfField, 'CPF inválido');
                    }
                }
            });
        });
    }
    
    validarCPF(cpf) {
        // Remove caracteres não numéricos
        cpf = cpf.replace(/\D/g, '');
        
        // Verifica se tem 11 dígitos
        if (cpf.length !== 11) return false;
        
        // Verifica se todos os dígitos são iguais
        if (/^(\d)\1{10}$/.test(cpf)) return false;
        
        // Validação do primeiro dígito verificador
        let soma = 0;
        for (let i = 0; i < 9; i++) {
            soma += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let resto = 11 - (soma % 11);
        let dv1 = resto < 2 ? 0 : resto;
        
        if (parseInt(cpf.charAt(9)) !== dv1) return false;
        
        // Validação do segundo dígito verificador
        soma = 0;
        for (let i = 0; i < 10; i++) {
            soma += parseInt(cpf.charAt(i)) * (11 - i);
        }
        resto = 11 - (soma % 11);
        let dv2 = resto < 2 ? 0 : resto;
        
        return parseInt(cpf.charAt(10)) === dv2;
    }
    
    showCPFError(cpfField, message) {
        // Remover erro anterior se existir
        const existingError = cpfField.parentNode.querySelector('.cpf-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Mostrar novo erro
        const error = document.createElement('div');
        error.className = 'cpf-error text-danger small mt-1';
        error.textContent = message;
        cpfField.parentNode.appendChild(error);
        
        // Remover erro após 5 segundos
        setTimeout(() => {
            if (error.parentNode) {
                error.remove();
            }
        }, 5000);
    }
    
    setupTelefoneMask() {
        // Encontrar todos os campos de telefone na página
        const telefoneFields = document.querySelectorAll('input[id*="telefone"], input[name*="telefone"], input[id*="Telefone"], input[name*="Telefone"]');
        
        telefoneFields.forEach(telefoneField => {
            // Máscara do telefone
            telefoneField.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                
                // Limitar a 11 dígitos
                if (value.length > 11) {
                    value = value.substring(0, 11);
                }
                
                // Aplicar máscara (00) 00000-0000 ou (00) 0000-0000
                if (value.length > 6) {
                    // Celular: (00) 00000-0000
                    value = '(' + value.substring(0, 2) + ') ' + 
                           value.substring(2, 7) + '-' + 
                           value.substring(7);
                } else if (value.length > 2) {
                    // Telefone fixo: (00) 0000-0000
                    value = '(' + value.substring(0, 2) + ') ' + 
                           value.substring(2);
                } else if (value.length > 0) {
                    value = '(' + value;
                }
                
                e.target.value = value;
            });
        });
    }
}

// Auto-inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar busca automática de CEP
    new CEPAutomation();
});

// Exportar para uso global se necessário
window.CEPAutomation = CEPAutomation;
