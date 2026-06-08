/**
 * Venta Form Fields Initialization
 * Used by both full page (venta_form.html) and modal (venta_form_modal.html)
 */

window.initVentaFormFields = function() {
    const baseId = (document.body.getAttribute('data-lead-telefono') || '');
    const productoSelect = document.getElementById('id_producto_nombre_display') || document.getElementById('id_producto_nombre');
    const origenSelect = document.getElementById('id_origen_display') || document.getElementById('id_origen');
    const operadorSelect = document.getElementById('id_operador_display') || document.getElementById('id_operador');
    const telefonoPortarInput = document.getElementById('id_telefono_portar_display') || document.getElementById('id_telefono_portar');
    const telefonoPortarGroup = document.getElementById('telefono_portar_group');
    const modeloGroup = document.getElementById('modelo_producto_group');
    const modeloSelect = document.getElementById('id_modelo_producto');
    const precioVentaSelect = document.getElementById('id_precio_venta_display') || document.getElementById('id_precio_venta');
    const planSelect = document.getElementById('id_plan_producto_display') || document.getElementById('id_plan_producto');
    const precioPlanInput = document.getElementById('id_precio_plan_display') || document.getElementById('id_precio_plan');
    const tipoRentaInput = document.getElementById('id_tipo_renta');

    function syncHiddenField(hiddenId, value) {
        const hidden = document.getElementById(hiddenId);
        if (hidden) hidden.value = value;
    }

    const planPrecioMap = {
        'ENTEL_CHIP_29_CONTROL': 29, 'ENTEL_CHIP_39_CONTROL': 39,
        'ENTEL_CHIP_45_CONTROL': 45, 'ENTEL_CHIP_59_CONTROL': 59,
        'ENTEL_CHIP_74_CONTROL': 74, 'ENTEL_CHIP_89_CONTROL': 89,
        'ENTEL_CHIP_109_CONTROL': 109, 'ENTEL_CHIP_145_CONTROL': 145,
        'ENTEL_CONTROL_49_CONTROL': 49, 'ENTEL_CONTROL_75_CONTROL': 75,
        'ENTEL_CONTROL_99_CONTROL': 99, 'ENTEL_CONTROL_149_CONTROL': 149,
        'ENTEL_CONTROL_199_CONTROL': 199,
        'ENTEL_75_CONTROL': 75,
        'ENTEL_LIBRE_149_LIBRE': 149,
        'ENTEL_LIBRE_99_LIBRE': 99
    };

    const modeloPreciosMap = {
        'ZTE_BLADE_L5_GRIS': [1, 49, 59, 79, 119],
        'ZTE_BLADE_L5_BLANCO': [49, 59, 119],
        'ZTE_BLADE_A315_NEGRO': [1, 29, 99, 109, 119, 129, 149, 189],
        'ZTE_BLADE_A315_BLANCO': [1, 29, 39, 99, 109, 119, 129, 149, 189],
        'ZTE_BLADE_A610_GRIS_4G': [1],
        'HUAWEI_Y360_NEGRO': [1, 9, 29, 39, 49, 59, 79, 89, 99, 129, 149, 199, 499],
        'HUAWEI_Y360_BLANCO': [9, 29, 39, 49, 59, 79, 99],
        'HUAWEI_Y360_II_NEGRO_3G': [29, 39, 89],
        'HUAWEI_P9_LITE': [1, 49, 99, 149],
        'GALAXY_J7': [1, 189, 199, 229, 349, 399],
        'LG_X_STYLE_NEGRO': [1, 49],
        'LG_X_STYLE_BLANCO': [1, 29, 49],
        'MOTO_G_PLAY': [1, 49, 99, 199],
        'MOTO_G_PLUS': [1, 49, 119, 349, 399],
        'MOTO_X_PLAY': [1, 49, 99],
        'MOTO_Z_PLAY': [1, 49, 399, 599, 699],
        'IPHONE_4S': [],
        'IPHONE_6_PLUS': [],
        'HUAWEI_MATE_S': [],
        'HUAWEI_MATE_S_NEGRO': [],
        'HUAWEI_Y360_II_BLANCO': [],
        'HUAWEI_Y360_II_NEGRO': [],
        'HUAWEI_Y360_II_NEGRO_DASH': [],
        'LG_G4_STYLUS_BLANCO': [],
        'LG_G4_STYLUS_METALICO': [],
        'LG_G5_TITAN': [],
        'GALAXY_J1': [],
        'SUPER_CHIP_ENTEL_PLUS': [],
        'SUPERCHIP_ENTEL': [],
        'ZTE_BLADE_A610_GRIS': [],
        'ZTE_BLADE_A610_GRIS_DASH': [],
        'ZTE_BLADE_A610_BLANCO': [],
        'ZTE_BLADE_A610_GRIS_CLEAN': [],
        'ZTE_BLADE_A610_NEGRO': [],
        'ZTE_BLADE_A610_NEGRO_4G': []
    };

    function updatePorProducto() {
        const valor = (productoSelect.value || '').trim();
        const isPack = valor === 'PACK';
        if (modeloGroup) modeloGroup.style.display = isPack ? '' : 'none';
        if (modeloSelect) modeloSelect.disabled = !isPack;
        if (precioVentaSelect) precioVentaSelect.disabled = !isPack;
    }

    function updatePorOrigen() {
        const isPortabilidad = origenSelect && origenSelect.value === 'PORTABILIDAD';
        if (operadorSelect) operadorSelect.required = isPortabilidad;
        if (telefonoPortarGroup) telefonoPortarGroup.style.display = isPortabilidad ? '' : 'none';
        if (telefonoPortarInput) telefonoPortarInput.required = isPortabilidad;
        if (!isPortabilidad && telefonoPortarInput) telefonoPortarInput.value = '';
    }

    function updatePrecioPlan() {
        const plan = planSelect.value;
        if (planPrecioMap[plan]) {
            precioPlanInput.value = planPrecioMap[plan];
            precioPlanInput.readOnly = true;
        } else {
            precioPlanInput.value = '';
        }
        syncHiddenField('id_precio_plan', precioPlanInput.value);
        updateTipoRenta();
    }

    function filtrarPreciosPorModelo() {
        const modelo = modeloSelect.value;
        const preciosValidos = modeloPreciosMap[modelo] || [];
        Array.from(precioVentaSelect.options).forEach(option => {
            const valor = parseInt(option.value);
            if (option.value === '' || preciosValidos.includes(valor)) {
                option.style.display = '';
            } else {
                option.style.display = 'none';
            }
        });
        if (preciosValidos.length > 0) {
            precioVentaSelect.value = preciosValidos[0];
        }
        updateTipoRenta();
    }

    function updateTipoRenta() {
        if (!precioVentaSelect || !precioPlanInput || !tipoRentaInput) return;
        const pv = parseInt(precioVentaSelect.value, 10) || 0;
        const pp = parseInt(precioPlanInput.value, 10) || 0;
        let renta = '';
        if (pv === 1 && pp <= 49) renta = 'R.BAJA';
        else if (pv <= 99 && pp >= 50 && pp <= 89) renta = 'R.MEDIA';
        else if (pv >= 99 && pp >= 89) renta = 'R.ALTA';
        tipoRentaInput.value = renta;
    }

    if (productoSelect) productoSelect.addEventListener('change', function() {
        syncHiddenField('id_producto_nombre', productoSelect.value);
        updatePorProducto();
        updateTipoRenta();
    });
    if (origenSelect) origenSelect.addEventListener('change', function() {
        syncHiddenField('id_origen', origenSelect.value);
        updatePorOrigen();
        updateTipoRenta();
    });
    if (planSelect) planSelect.addEventListener('change', function() {
        updatePrecioPlan();
        syncHiddenField('id_plan_producto', planSelect.value);
    });
    if (modeloSelect) modeloSelect.addEventListener('change', function() {
        filtrarPreciosPorModelo();
        syncHiddenField('id_modelo_producto', modeloSelect.value);
    });
    if (precioVentaSelect) precioVentaSelect.addEventListener('change', function() {
        updateTipoRenta();
        syncHiddenField('id_precio_venta', precioVentaSelect.value);
    });
    if (operadorSelect) operadorSelect.addEventListener('change', function() {
        syncHiddenField('id_operador', operadorSelect.value);
    });
    if (telefonoPortarInput) telefonoPortarInput.addEventListener('input', function() {
        syncHiddenField('id_telefono_portar', telefonoPortarInput.value);
    });

    const productoNombreInput = document.querySelector('[name="producto_nombre"]');
    if (productoNombreInput && productoSelect && productoNombreInput.value) {
        productoSelect.value = productoNombreInput.value;
    }
    const origenInput = document.querySelector('[name="origen"]');
    if (origenInput && origenSelect && origenInput.value) {
        origenSelect.value = origenInput.value;
    }
    const operadorInput = document.querySelector('[name="operador"]');
    if (operadorInput && operadorSelect && operadorInput.value) {
        operadorSelect.value = operadorInput.value;
    }
    const modeloInput = document.querySelector('[name="modelo_producto"]');
    if (modeloInput && modeloSelect && modeloInput.value) {
        modeloSelect.value = modeloInput.value;
        filtrarPreciosPorModelo();
    }
    const planInput = document.querySelector('[name="plan_producto"]');
    if (planInput && planSelect && planInput.value) {
        planSelect.value = planInput.value;
        updatePrecioPlan();
    }
    const telefonoPortarInputHidden = document.querySelector('[name="telefono_portar"]');
    if (telefonoPortarInputHidden && telefonoPortarInput && telefonoPortarInputHidden.value) {
        telefonoPortarInput.value = telefonoPortarInputHidden.value;
    }

    updatePorProducto();
    updatePorOrigen();
    updateTipoRenta();
};

    const modeloPreciosMap = {
        'ZTE_BLADE_L5_GRIS': [1, 49, 59, 79, 119],
        'ZTE_BLADE_L5_BLANCO': [49, 59, 119],
        'ZTE_BLADE_A315_NEGRO': [1, 29, 99, 109, 119, 129, 149, 189],
        'ZTE_BLADE_A315_BLANCO': [1, 29, 39, 99, 109, 119, 129, 149, 189],
        'ZTE_BLADE_A610_GRIS_4G': [1],
        'HUAWEI_Y360_NEGRO': [1, 9, 29, 39, 49, 59, 79, 89, 99, 129, 149, 199, 499],
        'HUAWEI_Y360_BLANCO': [9, 29, 39, 49, 59, 79, 99],
        'HUAWEI_Y360_II_NEGRO_3G': [29, 39, 89],
        'HUAWEI_P9_LITE': [1, 49, 99, 149],
        'GALAXY_J7': [1, 189, 199, 229, 349, 399],
        'LG_X_STYLE_NEGRO': [1, 49],
        'LG_X_STYLE_BLANCO': [1, 29, 49],
        'MOTO_G_PLAY': [1, 49, 99, 199],
        'MOTO_G_PLUS': [1, 49, 119, 349, 399],
        'MOTO_X_PLAY': [1, 49, 99],
        'MOTO_Z_PLAY': [1, 49, 399, 599, 699],
        'IPHONE_4S': [],
        'IPHONE_6_PLUS': [],
        'HUAWEI_MATE_S': [],
        'HUAWEI_MATE_S_NEGRO': [],
        'HUAWEI_Y360_II_BLANCO': [],
        'HUAWEI_Y360_II_NEGRO': [],
        'HUAWEI_Y360_II_NEGRO_DASH': [],
        'LG_G4_STYLUS_BLANCO': [],
        'LG_G4_STYLUS_METALICO': [],
        'LG_G5_TITAN': [],
        'GALAXY_J1': [],
        'SUPER_CHIP_ENTEL_PLUS': [],
        'SUPERCHIP_ENTEL': [],
        'ZTE_BLADE_A610_GRIS': [],
        'ZTE_BLADE_A610_GRIS_DASH': [],
        'ZTE_BLADE_A610_BLANCO': [],
        'ZTE_BLADE_A610_GRIS_CLEAN': [],
        'ZTE_BLADE_A610_NEGRO': [],
        'ZTE_BLADE_A610_NEGRO_4G': []
    };

    function updatePorProducto() {
        const valor = (productoSelect.value || '').trim();
        const isPack = valor === 'PACK';
        const modeloGroup = document.getElementById('modelo_producto_group');

        if (isPack) {
            if (modeloSelect) modeloSelect.disabled = false;
            if (modeloGroup) modeloGroup.style.display = 'block';
            if (precioVentaSelect) precioVentaSelect.disabled = false;
        } else {
            if (modeloSelect) {
                modeloSelect.value = '';
                modeloSelect.disabled = true;
            }
            if (modeloGroup) modeloGroup.style.display = 'none';
            if (precioVentaSelect) {
                precioVentaSelect.value = '1';
                precioVentaSelect.disabled = true;
            }
        }
    }

    function updatePorOrigen() {
        const isPortabilidad = origenSelect.value === 'PORTABILIDAD';
        
        if (isPortabilidad) {
            operadorSelect.required = true;
            if (telefonoPortarGroup) telefonoPortarGroup.style.display = 'block';
            if (telefonoPortarInput) telefonoPortarInput.required = true;
        } else {
            operadorSelect.required = false;
            if (telefonoPortarGroup) telefonoPortarGroup.style.display = 'none';
            if (telefonoPortarInput) {
                telefonoPortarInput.required = false;
                telefonoPortarInput.value = '';
            }
        }
    }

    function updatePrecioPlan() {
        const plan = planSelect.value;
        if (planPrecioMap[plan]) {
            precioPlanInput.value = planPrecioMap[plan];
            precioPlanInput.readOnly = true;
        } else {
            precioPlanInput.value = '';
        }
        syncHiddenField('id_precio_plan', precioPlanInput.value);
        updateTipoRenta();
    }

    function filtrarPreciosPorModelo() {
        const modelo = modeloSelect.value;
        const preciosValidos = modeloPreciosMap[modelo] || [];
        
        Array.from(precioVentaSelect.options).forEach(option => {
            const valor = parseInt(option.value);
            if (option.value === '' || preciosValidos.includes(valor)) {
                option.style.display = '';
            } else {
                option.style.display = 'none';
            }
        });
        
        if (preciosValidos.length > 0) {
            precioVentaSelect.value = preciosValidos[0];
        }
        updateTipoRenta();
    }

    function updateTipoRenta() {
        const pv = parseInt(precioVentaSelect.value) || 0;
        const pp = parseInt(precioPlanInput.value) || 0;
        let renta = '';
        
        if (pv === 1 && pp <= 49) renta = 'R.BAJA';
        else if (pv <= 99 && pp >= 50 && pp <= 89) renta = 'R.MEDIA';
        else if (pv >= 99 && pp >= 89) renta = 'R.ALTA';
        
        if (tipoRentaInput) tipoRentaInput.value = renta;
    }

    // Set up event listeners
    if (productoSelect) {
        productoSelect.addEventListener('change', function() {
            const valor = (productoSelect.value || '').trim();
            syncHiddenField('id_producto_nombre', valor);
            updatePorProducto();
        });
    }
    if (origenSelect) origenSelect.addEventListener('change', function() {
        updatePorOrigen();
        syncHiddenField('id_origen', origenSelect.value);
    });
    if (planSelect) planSelect.addEventListener('change', function() {
        updatePrecioPlan();
        syncHiddenField('id_plan_producto', planSelect.value);
    });
    if (modeloSelect) modeloSelect.addEventListener('change', function() {
        filtrarPreciosPorModelo();
        syncHiddenField('id_modelo_producto', modeloSelect.value);
    });
    if (precioVentaSelect) precioVentaSelect.addEventListener('change', function() {
        updateTipoRenta();
        syncHiddenField('id_precio_venta', precioVentaSelect.value);
    });
    if (operadorSelect) operadorSelect.addEventListener('change', function() {
        syncHiddenField('id_operador', operadorSelect.value);
    });
    if (telefonoPortarInput) telefonoPortarInput.addEventListener('input', function() {
        syncHiddenField('id_telefono_portar', telefonoPortarInput.value);
    });
    if (tipoLineaSelect) tipoLineaSelect.addEventListener('change', function() {
        syncHiddenField('id_tipo_linea', tipoLineaSelect.value);
    });
    if (tipoPagoSelect) tipoPagoSelect.addEventListener('change', function() {
        syncHiddenField('id_tipo_pago', tipoPagoSelect.value);
    });

    // Inicializar valores desde formulario
    const productoNombreInput = document.querySelector('[name="producto_nombre"]');
    if (productoNombreInput && productoSelect && productoNombreInput.value) {
        productoSelect.value = productoNombreInput.value;
        updatePorProducto();
    }
    const origenInput = document.querySelector('[name="origen"]');
    if (origenInput && origenSelect && origenInput.value) {
        origenSelect.value = origenInput.value;
        updatePorOrigen();
    }
    const operadorInput = document.querySelector('[name="operador"]');
    if (operadorInput && operadorSelect && operadorInput.value) {
        operadorSelect.value = operadorInput.value;
    }
    const modeloInput = document.querySelector('[name="modelo_producto"]');
    if (modeloInput && modeloSelect && modeloInput.value) {
        modeloSelect.value = modeloInput.value;
        filtrarPreciosPorModelo();
    }
    const planInput = document.querySelector('[name="plan_producto"]');
    if (planInput && planSelect && planInput.value) {
        planSelect.value = planInput.value;
        updatePrecioPlan();
    }
    const telefonoPortarInputHidden = document.querySelector('[name="telefono_portar"]');
    if (telefonoPortarInputHidden && telefonoPortarInput && telefonoPortarInputHidden.value) {
        telefonoPortarInput.value = telefonoPortarInputHidden.value;
    }
    const tipoLineaInput = document.querySelector('[name="tipo_linea"]');
    if (tipoLineaInput && tipoLineaSelect && tipoLineaInput.value) {
        tipoLineaSelect.value = tipoLineaInput.value;
    }
    const tipoPagoInput = document.querySelector('[name="tipo_pago"]');
    if (tipoPagoInput && tipoPagoSelect && tipoPagoInput.value) {
        tipoPagoSelect.value = tipoPagoInput.value;
    }

    // Ubigeo - Combos jerárquicos
    const configScript = document.getElementById('venta-form-config');
    const urls = configScript ? JSON.parse(configScript.textContent) : {};
    const urlProvincias = urls.urlProvincias || '/api/ubigeo/provincias/';
    const urlDistritos = urls.urlDistritos || '/api/ubigeo/distritos/';

    const deptoSelect = document.getElementById('id_departamento');
    const provinciaSelect = document.getElementById('id_provincia');
    const distritoSelect = document.getElementById('id_distrito');

    function loadProvincias(deptoCode, selectedProvincia) {
        if (!deptoCode) {
            provinciaSelect.innerHTML = '<option value="">-- Primero seleccione departamento --</option>';
            provinciaSelect.disabled = true;
            distritoSelect.innerHTML = '<option value="">-- Primero seleccione provincia --</option>';
            distritoSelect.disabled = true;
            return;
        }
        
        fetch(urlProvincias + '?departamento=' + encodeURIComponent(deptoCode))
            .then(response => response.json())
            .then(data => {
                provinciaSelect.innerHTML = '<option value="">-- Seleccione provincia --</option>';
                data.provincias.forEach(prov => {
                    const option = document.createElement('option');
                    option.value = prov[0];
                    option.textContent = prov[1];
                    if (selectedProvincia && prov[0] === selectedProvincia) {
                        option.selected = true;
                    }
                    provinciaSelect.appendChild(option);
                });
                provinciaSelect.disabled = false;
                
                if (selectedProvincia) {
                    loadDistritos(deptoCode, selectedProvincia, null);
                } else {
                    distritoSelect.innerHTML = '<option value="">-- Primero seleccione provincia --</option>';
                    distritoSelect.disabled = true;
                }
            });
    }

    function loadDistritos(deptoCode, provinciaCode, selectedDistrito) {
        if (!deptoCode || !provinciaCode) {
            distritoSelect.innerHTML = '<option value="">-- Primero seleccione provincia --</option>';
            distritoSelect.disabled = true;
            return;
        }
        
        fetch(urlDistritos + '?departamento=' + encodeURIComponent(deptoCode) + '&provincia=' + encodeURIComponent(provinciaCode))
            .then(response => response.json())
            .then(data => {
                distritoSelect.innerHTML = '<option value="">-- Seleccione distrito --</option>';
                data.distritos.forEach(dist => {
                    const option = document.createElement('option');
                    option.value = dist[0];
                    option.textContent = dist[1];
                    if (selectedDistrito && dist[0] === selectedDistrito) {
                        option.selected = true;
                    }
                    distritoSelect.appendChild(option);
                });
                distritoSelect.disabled = false;
            });
    }

    if (deptoSelect) {
        deptoSelect.addEventListener('change', function() {
            loadProvincias(this.value, null);
        });

        const initialDepto = deptoSelect.value;
        const initialProvincia = provinciaSelect ? provinciaSelect.value : '';
        const initialDistrito = distritoSelect ? distritoSelect.value : '';

        if (initialDepto) {
            loadProvincias(initialDepto, initialProvincia);
        }

        if (initialProvincia && initialDepto) {
            loadDistritos(initialDepto, initialProvincia, initialDistrito);
        }
    }

    if (provinciaSelect) {
        provinciaSelect.addEventListener('change', function() {
            const depto = deptoSelect ? deptoSelect.value : '';
            const prov = this.value;
            loadDistritos(depto, prov, null);
        });
    }

    // Sincronizar ubigeo con campos ocultos
    const departamentoInput = document.querySelector('[name="departamento"]');
    const provinciaInput = document.querySelector('[name="provincia"]');
    const distritoInput = document.querySelector('[name="distrito"]');
    
    if (deptoSelect && departamentoInput) {
        deptoSelect.addEventListener('change', function() {
            departamentoInput.value = this.value;
        });
    }
    if (provinciaSelect && provinciaInput) {
        provinciaSelect.addEventListener('change', function() {
            provinciaInput.value = this.value;
        });
    }
    if (distritoSelect && distritoInput) {
        distritoSelect.addEventListener('change', function() {
            distritoInput.value = this.value;
        });
    }

    // Validación: Si no hay número_via, obligar manzana o lote
    const numeroVia = document.querySelector('[name="numero_via"]');
    const manzana = document.querySelector('[name="manzana"]');
    const lote = document.querySelector('[name="lote"]');

    function validateNumeroVia() {
        if (numeroVia) {
            if (numeroVia.value === '' || numeroVia.value === null) {
                if (manzana && (manzana.value === '' || manzana.value === null) &&
                    lote && (lote.value === '' || lote.value === null)) {
                    numeroVia.setCustomValidity('Si no ingresa número, debe indicar manzana o lote');
                    numeroVia.style.borderColor = 'red';
                } else {
                    numeroVia.setCustomValidity('');
                    numeroVia.style.borderColor = '';
                }
            } else {
                numeroVia.setCustomValidity('');
                numeroVia.style.borderColor = '';
            }
        }
    }

    if (numeroVia) {
        numeroVia.addEventListener('input', validateNumeroVia);
        if (manzana) manzana.addEventListener('input', validateNumeroVia);
        if (lote) lote.addEventListener('input', validateNumeroVia);
        validateNumeroVia();
    }
};

// Auto-inicialización cuando el script se carga en página completa
document.addEventListener('DOMContentLoaded', function() {
    if (typeof initVentaFormFields === 'function') {
        initVentaFormFields();
    }
});

// Escuchar evento de formulario cargado en modal
document.addEventListener('ventaFormLoaded', function() {
    if (typeof initVentaFormFields === 'function') {
        initVentaFormFields();
    }
    if (typeof initClienteSearch === 'function') {
        initClienteSearch();
    }
});

/**
 * Cliente Search Initialization
 * Used by both full page and modal forms
 */
window.initClienteSearch = function() {
    const configScript = document.getElementById('cliente-search-config');
    const config = configScript ? JSON.parse(configScript.textContent) : {};
    const urlBuscar = config.urlBuscar || '/ventas/buscar-cliente/';
    const urlValidar = config.urlValidar || '/ventas/validar-cliente/';
    const baseId = config.baseId || '';
    const urlRecargar = baseId ? "/ventas/recargar-lead/" + baseId + "/" : "";

    const btnBuscar = document.getElementById('btnBuscarCliente');
    const btnValidar = document.getElementById('btnValidarCliente');
    const btnRecargar = document.getElementById('btnRecargarLead');
    const campoDocumento = document.getElementById('id_cliente_documento');
    const campoTipoDocumento = document.getElementById('id_cliente_tipo_documento');
    const mensaje = document.getElementById('clienteMensaje');
    const camposCliente = document.querySelectorAll('.cliente-campos input');
    const checkboxNuevo = document.getElementById('id_registrar_nuevo_cliente');

    function setValue(id, valor) {
        const el = document.getElementById(id);
        if (el) el.value = valor;
    }

    function mostrarMensaje(texto, tipo) {
        mensaje.className = 'alert alert-' + tipo;
        mensaje.textContent = texto;
        mensaje.style.display = 'block';
    }

    function bloquearCamposCliente(bloquear) {
        camposCliente.forEach(function(input) {
            if (input.id === 'id_cliente_documento') return;
            if (bloquear) {
                input.classList.remove('form-control');
                input.classList.add('form-control-plaintext');
            } else {
                input.classList.remove('form-control-plaintext');
                input.classList.add('form-control');
            }
            input.disabled = bloquear;
        });
    }

    function limpiarErroresCampos() {
        camposCliente.forEach(function(input) {
            input.classList.remove('is-invalid');
            const fb = input.parentElement.querySelector('.invalid-feedback');
            if (fb) fb.remove();
        });
    }

    function mostrarErrorCampo(input, texto) {
        input.classList.add('is-invalid');
        let fb = input.parentElement.querySelector('.invalid-feedback');
        if (!fb) {
            fb = document.createElement('div');
            fb.className = 'invalid-feedback';
            input.parentElement.appendChild(fb);
        }
        fb.textContent = texto;
    }

    function buscarCliente() {
        const tipo = campoTipoDocumento ? campoTipoDocumento.value.trim() : 'DNI';
        const documento = campoDocumento.value.trim();
        if (!documento) {
            mostrarMensaje('Ingrese un documento para buscar.', 'warning');
            return;
        }
        limpiarErroresCampos();
        setValue('id_cliente_telefono_1', '');
        setValue('id_cliente_telefono_2', '');
        mostrarMensaje('Buscando cliente...', 'info');
        fetch(urlBuscar + '?tipo_documento=' + encodeURIComponent(tipo) + '&documento=' + encodeURIComponent(documento) + '&csrfmiddlewaretoken=' + document.querySelector('[name=csrfmiddlewaretoken]').value, {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.json())
        .then(data => {
            if (data.encontrado) {
                const c = data.cliente;
                if (campoTipoDocumento) setValue('id_cliente_tipo_documento', c.tipo_documento);
                setValue('id_cliente_nombres', c.nombres);
                setValue('id_cliente_paterno', c.paterno);
                setValue('id_cliente_materno', c.materno);
                setValue('id_cliente_documento', c.documento);
                setValue('id_cliente_telefono_1', c.telefono_1 || '');
                setValue('id_cliente_telefono_2', c.telefono_2 || '');
                if (checkboxNuevo) {
                    checkboxNuevo.checked = false;
                    checkboxNuevo.disabled = true;
                }
                bloquearCamposCliente(true);
                limpiarErroresCampos();
                mostrarMensaje('Cliente encontrado: ' + c.nombres + ' ' + c.paterno + ' ' + c.materno, 'success');
            } else {
                setValue('id_cliente_nombres', '');
                setValue('id_cliente_paterno', '');
                setValue('id_cliente_materno', '');
                setValue('id_cliente_documento', documento);
                setValue('id_cliente_telefono_1', '');
                setValue('id_cliente_telefono_2', '');
                if (checkboxNuevo) {
                    checkboxNuevo.checked = true;
                    checkboxNuevo.disabled = false;
                }
                bloquearCamposCliente(false);
                limpiarErroresCampos();
                mostrarMensaje('Cliente no encontrado. Complete los datos para registrar uno nuevo.', 'warning');
            }
        })
        .catch(function() {
            mostrarMensaje('Error al buscar cliente.', 'danger');
        });
    }

    function validarCliente() {
        const tipo = campoTipoDocumento ? campoTipoDocumento.value.trim() : 'DNI';
        const documento = campoDocumento.value.trim();
        if (!documento) {
            mostrarMensaje('Ingrese un documento para validar.', 'warning');
            return;
        }
        mostrarMensaje('Validando cliente...', 'info');
        limpiarErroresCampos();
        fetch(urlValidar + '?tipo_documento=' + encodeURIComponent(tipo) + '&documento=' + encodeURIComponent(documento) + '&csrfmiddlewaretoken=' + document.querySelector('[name=csrfmiddlewaretoken]').value, {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.json())
        .then(function(data) {
            if (data.existe) {
                const c = data.cliente;
                if (campoTipoDocumento) setValue('id_cliente_tipo_documento', c.tipo_documento);
                setValue('id_cliente_nombres', c.nombres);
                setValue('id_cliente_paterno', c.paterno);
                setValue('id_cliente_materno', c.materno);
                setValue('id_cliente_documento', c.documento);
                setValue('id_cliente_telefono_1', c.telefono_1 || '');
                setValue('id_cliente_telefono_2', c.telefono_2 || '');
                if (checkboxNuevo) {
                    checkboxNuevo.checked = false;
                    checkboxNuevo.disabled = true;
                }
                bloquearCamposCliente(true);
                limpiarErroresCampos();
                mostrarMensaje('Cliente existente validado. Datos protegidos.', 'success');
            } else {
                bloquearCamposCliente(false);
                const nombres = document.getElementById('id_cliente_nombres');
                const paterno = document.getElementById('id_cliente_paterno');
                const materno = document.getElementById('id_cliente_materno');
                const doc = document.getElementById('id_cliente_documento');
                const tel1 = document.getElementById('id_cliente_telefono_1');
                const tel2 = document.getElementById('id_cliente_telefono_2');

                let hayErrores = false;

                if (!doc || !doc.value.trim()) {
                    mostrarErrorCampo(doc, 'Documento es obligatorio.');
                    hayErrores = true;
                }
                if (!nombres || !nombres.value.trim()) {
                    mostrarErrorCampo(nombres, 'Nombres es obligatorio.');
                    hayErrores = true;
                } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(nombres.value.trim())) {
                    mostrarErrorCampo(nombres, 'Nombres solo debe contener letras.');
                    hayErrores = true;
                }
                if (!paterno || !paterno.value.trim()) {
                    mostrarErrorCampo(paterno, 'Paterno es obligatorio.');
                    hayErrores = true;
                } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(paterno.value.trim())) {
                    mostrarErrorCampo(paterno, 'Paterno solo debe contener letras.');
                    hayErrores = true;
                }
                if (!materno || !materno.value.trim()) {
                    mostrarErrorCampo(materno, 'Materno es obligatorio.');
                    hayErrores = true;
                } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(materno.value.trim())) {
                    mostrarErrorCampo(materno, 'Materno solo debe contener letras.');
                    hayErrores = true;
                }
                if (tel1 && tel1.value.trim() && !/^\d+$/.test(tel1.value.trim())) {
                    mostrarErrorCampo(tel1, 'Teléfono 01 solo debe contener números.');
                    hayErrores = true;
                }
                if (tel2 && tel2.value.trim() && !/^\d+$/.test(tel2.value.trim())) {
                    mostrarErrorCampo(tel2, 'Teléfono 02 solo debe contener números.');
                    hayErrores = true;
                }

                if (!hayErrores) {
                    if (checkboxNuevo) {
                        checkboxNuevo.checked = true;
                        checkboxNuevo.disabled = false;
                    }
                    bloquearCamposCliente(true);
                    limpiarErroresCampos();
                    mostrarMensaje('Cliente no encontrado. Datos válidos. Se guardará como cliente nuevo.', 'success');
                } else {
                    if (checkboxNuevo) {
                        checkboxNuevo.checked = true;
                        checkboxNuevo.disabled = false;
                    }
                }
            }
        })
        .catch(function() {
            mostrarMensaje('Error al validar cliente.', 'danger');
        });
    }

    function recargarLead() {
        if (!baseId) {
            mostrarMensaje('No hay lead asignado para recargar.', 'warning');
            return;
        }
        fetch(urlRecargar, {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(r => r.json())
        .then(function(data) {
            if (data.ok) {
                const l = data.lead;
                setValue('id_base_telefono', l.telefono || '');
                setValue('id_base_nombres', l.nombres || '');
                setValue('id_base_paterno', l.paterno || '');
                setValue('id_base_materno', l.materno || '');
                setValue('id_base_documento', l.documento || '');
                setValue('id_base_correo', l.correo || '');
                setValue('id_base_observaciones', l.observaciones || '');
                if (campoTipoDocumento) setValue('id_cliente_tipo_documento', l.tipo_documento || 'DNI');
                setValue('id_cliente_documento', l.documento || '');
                setValue('id_cliente_nombres', l.nombres || '');
                setValue('id_cliente_paterno', l.paterno || '');
                setValue('id_cliente_materno', l.materno || '');
                setValue('id_cliente_telefono_1', l.telefono || '');
                setValue('id_cliente_telefono_2', '');
                if (checkboxNuevo) {
                    checkboxNuevo.checked = true;
                    checkboxNuevo.disabled = false;
                }
                bloquearCamposCliente(false);
                limpiarErroresCampos();
                mostrarMensaje('Datos del lead recargados correctamente.', 'success');
            } else {
                mostrarMensaje(data.mensaje || 'Error al recargar lead.', 'danger');
            }
        })
        .catch(function() {
            mostrarMensaje('Error al recargar datos del lead.', 'danger');
        });
    }

    if (btnBuscar && campoDocumento) {
        btnBuscar.addEventListener('click', buscarCliente);
        if (btnValidar) {
            btnValidar.addEventListener('click', validarCliente);
        }
        if (btnRecargar) {
            btnRecargar.addEventListener('click', recargarLead);
        }
    }

    const btnTelefonoPortar = document.getElementById('btnTelefonoPortar');
    if (btnTelefonoPortar) {
        btnTelefonoPortar.addEventListener('click', function() {
            const campoPortar = document.getElementById('id_telefono_portar');
            const tel1 = document.getElementById('id_cliente_telefono_1');
            const tel2 = document.getElementById('id_cliente_telefono_2');
            const leadTel = document.getElementById('id_base_telefono');
            let valor = '';
            if (leadTel && leadTel.value) {
                valor = leadTel.value;
            } else if (tel1 && tel1.value) {
                valor = tel1.value;
            } else if (tel2 && tel2.value) {
                valor = tel2.value;
            }
            campoPortar.value = valor;
            campoPortar.dispatchEvent(new Event('change'));
        });
    }
};

// Auto-inicialización para página completa (cliente search)
document.addEventListener('DOMContentLoaded', function() {
    if (typeof initClienteSearch === 'function') {
        initClienteSearch();
    }
});