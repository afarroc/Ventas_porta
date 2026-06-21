/**
 * Venta Form Fields Initialization
 * Used by both full page (venta_form.html) and modal (venta_form_modal.html)
 */

window.initVentaFormFields = function() {
    const baseId = (document.body.getAttribute('data-lead-telefono') || '');
    const productoSelect = document.getElementById('id_producto_nombre_display') || document.getElementById('id_producto_nombre');
    const origenSelect = document.getElementById('id_origen_display') || document.getElementById('id_origen');
    const operadorSelect = document.getElementById('id_operador_display') || document.getElementById('id_operador');
    const telefonoPortarGroup = document.getElementById('telefono_portar_group');
    const telefonoPortarField = document.getElementById('telefono_portar_field');
    const telefonoPortarInput = document.getElementById('id_telefono_portar_display') || document.getElementById('id_telefono_portar');
    const modeloGroup = document.getElementById('modelo_producto_group');
    const modeloSelect = document.getElementById('id_modelo_producto_display') || document.getElementById('id_modelo_producto');
    const precioVentaSelect = document.getElementById('id_precio_venta_display') || document.getElementById('id_precio_venta');
    const planSelect = document.getElementById('id_plan_producto_display') || document.getElementById('id_plan_producto');
    const precioPlanInput = document.getElementById('id_precio_plan_display') || document.getElementById('id_precio_plan');
    const tipoRentaInput = document.getElementById('id_tipo_renta');
    const tipoLineaSelect = document.getElementById('id_tipo_linea_display') || document.getElementById('id_tipo_linea');
    const tipoPagoSelect = document.getElementById('id_tipo_pago_display') || document.getElementById('id_tipo_pago');
    const btnValidarProducto = document.getElementById('btnValidarProducto');
    const productoMensaje = document.getElementById('productoMensaje');
    const productoValidado = document.getElementById('id_producto_validado');

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

    const tipoRentaTable = {
        'PORTABILIDAD_PACK_1': 'R.BAJA',
        'PORTABILIDAD_PACK_4': 'R.BAJA',
        'PORTABILIDAD_PACK_9': 'R.BAJA',
        'PORTABILIDAD_PACK_13': 'R.BAJA',
        'PORTABILIDAD_PACK_29': 'R.BAJA',
        'PORTABILIDAD_PACK_49': 'R.BAJA',
        'PORTABILIDAD_PACK_74': 'R.MEDIA',
        'PORTABILIDAD_PACK_75': 'R.MEDIA',
        'PORTABILIDAD_PACK_89': 'R.MEDIA',
        'PORTABILIDAD_PACK_99': 'R.ALTA',
        'PORTABILIDAD_PACK_129': 'R.ALTA',
        'PORTABILIDAD_PACK_149': 'R.ALTA',
        'PORTABILIDAD_PACK_189': 'R.ALTA',
        'PORTABILIDAD_PACK_199': 'R.ALTA',
        'PORTABILIDAD_PACK_229': 'R.ALTA',
        'PORTABILIDAD_PACK_249': 'R.ALTA',
        'PORTABILIDAD_PACK_299': 'R.ALTA',
        'PORTABILIDAD_PACK_349': 'R.ALTA',
        'PORTABILIDAD_PACK_399': 'R.ALTA',
        'PORTABILIDAD_PACK_599': 'R.ALTA',
        'PORTABILIDAD_PACK_699': 'R.ALTA',
        'PORTABILIDAD_CHIP_25': 'R.BAJA',
        'PORTABILIDAD_CHIP_29': 'R.BAJA',
        'PORTABILIDAD_CHIP_39': 'R.BAJA',
        'PORTABILIDAD_CHIP_45': 'R.BAJA',
        'PORTABILIDAD_CHIP_49': 'R.BAJA',
        'PORTABILIDAD_CHIP_59': 'R.MEDIA',
        'PORTABILIDAD_CHIP_74': 'R.MEDIA',
        'PORTABILIDAD_CHIP_75': 'R.MEDIA',
        'PORTABILIDAD_CHIP_89': 'R.MEDIA',
        'PORTABILIDAD_CHIP_99': 'R.ALTA',
        'PORTABILIDAD_CHIP_109': 'R.ALTA',
        'PORTABILIDAD_CHIP_145': 'R.ALTA',
        'PORTABILIDAD_CHIP_209': 'R.ALTA',
        'LINEA_NUEVA_PACK_1': 'R.BAJA',
        'LINEA_NUEVA_PACK_4': 'R.BAJA',
        'LINEA_NUEVA_PACK_9': 'R.BAJA',
        'LINEA_NUEVA_PACK_13': 'R.BAJA',
        'LINEA_NUEVA_PACK_29': 'R.BAJA',
        'LINEA_NUEVA_PACK_49': 'R.BAJA',
        'LINEA_NUEVA_PACK_75': 'R.MEDIA',
        'LINEA_NUEVA_PACK_89': 'R.MEDIA',
        'LINEA_NUEVA_PACK_99': 'R.ALTA',
        'LINEA_NUEVA_PACK_129': 'R.ALTA',
        'LINEA_NUEVA_PACK_149': 'R.ALTA',
        'LINEA_NUEVA_PACK_189': 'R.ALTA',
        'LINEA_NUEVA_PACK_199': 'R.ALTA',
        'LINEA_NUEVA_PACK_229': 'R.ALTA',
        'LINEA_NUEVA_PACK_249': 'R.ALTA',
        'LINEA_NUEVA_PACK_299': 'R.ALTA',
        'LINEA_NUEVA_PACK_349': 'R.ALTA',
        'LINEA_NUEVA_PACK_399': 'R.ALTA',
        'LINEA_NUEVA_PACK_599': 'R.ALTA',
        'LINEA_NUEVA_PACK_699': 'R.ALTA',
        'LINEA_NUEVA_CHIP_25': 'R.BAJA',
        'LINEA_NUEVA_CHIP_29': 'R.BAJA',
        'LINEA_NUEVA_CHIP_39': 'R.BAJA',
        'LINEA_NUEVA_CHIP_45': 'R.BAJA',
        'LINEA_NUEVA_CHIP_59': 'R.MEDIA',
        'LINEA_NUEVA_CHIP_74': 'R.MEDIA',
        'LINEA_NUEVA_CHIP_89': 'R.MEDIA',
        'LINEA_NUEVA_CHIP_109': 'R.ALTA',
        'LINEA_NUEVA_CHIP_145': 'R.ALTA',
        'LINEA_NUEVA_CHIP_209': 'R.ALTA'
    };

    const planChipList = [
        'ENTEL_CHIP_29_CONTROL',
        'ENTEL_CHIP_39_CONTROL',
        'ENTEL_CHIP_45_CONTROL',
        'ENTEL_CHIP_59_CONTROL',
        'ENTEL_CHIP_74_CONTROL',
        'ENTEL_CHIP_89_CONTROL',
        'ENTEL_CHIP_109_CONTROL',
        'ENTEL_CHIP_145_CONTROL',
    ];

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


    // Modelos agrupados por tipo de producto
    const modeloPackList = ['IPHONE_4S', 'IPHONE_6_PLUS', 'HUAWEI_MATE_S', 'HUAWEI_MATE_S_NEGRO',
        'HUAWEI_P9_LITE', 'HUAWEI_Y360_II_BLANCO', 'HUAWEI_Y360_II_NEGRO', 'HUAWEI_Y360_II_NEGRO_DASH',
        'HUAWEI_Y360_II_NEGRO_3G', 'HUAWEI_Y360_BLANCO', 'HUAWEI_Y360_NEGRO', 'LG_G4_STYLUS_BLANCO',
        'LG_G4_STYLUS_METALICO', 'LG_G5_TITAN', 'LG_X_STYLE_BLANCO', 'LG_X_STYLE_NEGRO',
        'MOTO_G_PLAY', 'MOTO_G_PLUS', 'MOTO_X_PLAY', 'MOTO_Z_PLAY', 'GALAXY_J1', 'GALAXY_J7',
        'ZTE_BLADE_A315_BLANCO', 'ZTE_BLADE_A315_NEGRO', 'ZTE_BLADE_A610_GRIS',
        'ZTE_BLADE_A610_GRIS_DASH', 'ZTE_BLADE_A610_BLANCO', 'ZTE_BLADE_A610_GRIS_CLEAN',
        'ZTE_BLADE_A610_NEGRO', 'ZTE_BLADE_A610_NEGRO_4G', 'ZTE_BLADE_L5_BLANCO', 'ZTE_BLADE_L5_GRIS'];
    const modeloChipList = ['SUPER_CHIP_ENTEL_PLUS', 'SUPERCHIP_ENTEL'];

    function filtrarPlanesPorProducto(producto) {
        if (!planSelect) return;
        const mostrarChip = producto === 'CHIP';

        Array.from(planSelect.options).forEach(option => {
            const value = option.value;
            const esPlanChip = planChipList.includes(value);
            if (!mostrarChip || esPlanChip) {
                option.style.display = '';
                option.disabled = false;
            } else {
                option.style.display = 'none';
                option.disabled = true;
            }
        });

        if (mostrarChip && planSelect.value && !planChipList.includes(planSelect.value)) {
            planSelect.value = '';
            updatePrecioPlan();
        }
        if (!mostrarChip && planSelect.value && planChipList.includes(planSelect.value)) {
            planSelect.value = '';
            updatePrecioPlan();
        }
        syncHiddenField('id_plan_producto', planSelect.value);
    }

    function updatePorProducto() {
        if (!productoSelect) return;
        const valor = (productoSelect.value || '').trim();
        const isPack = valor === 'PACK';

        if (isPack) {
            if (modeloSelect) {
                modeloSelect.disabled = false;
                if (!modeloSelect.value || !modeloPackList.includes(modeloSelect.value)) {
                    modeloSelect.value = '';
                }
                // Filtrar opciones: solo mostrar modelos PACK
                Array.from(modeloSelect.options).forEach(option => {
                    const value = option.value;
                    if (value === '' || modeloPackList.includes(value)) {
                        option.style.display = '';
                        option.disabled = false;
                    } else {
                        option.style.display = 'none';
                        option.disabled = true;
                    }
                });
                syncHiddenField('id_modelo_producto', modeloSelect.value);
            }
            if (modeloGroup) modeloGroup.style.display = 'block';
            if (precioVentaSelect) {
                precioVentaSelect.disabled = false;
                syncHiddenField('id_precio_venta', precioVentaSelect.value);
            }
            filtrarPlanesPorProducto('PACK');
        } else {
            if (modeloSelect) {
                modeloSelect.value = '';
                modeloSelect.disabled = true;
                syncHiddenField('id_modelo_producto', '');
                // Filtrar opciones: solo mostrar modelos CHIP (nada)
                Array.from(modeloSelect.options).forEach(option => {
                    option.style.display = 'none';
                    option.disabled = true;
                });
            }
            if (modeloGroup) modeloGroup.style.display = 'none';
            if (precioVentaSelect) {
                precioVentaSelect.value = '1';
                precioVentaSelect.disabled = true;
                syncHiddenField('id_precio_venta', '1');
            }
            filtrarPlanesPorProducto('CHIP');
        }
    }

    function updatePorOrigen() {
        if (!origenSelect) return;
        const isPortabilidad = origenSelect && origenSelect.value === 'PORTABILIDAD';

        if (isPortabilidad) {
            if (telefonoPortarGroup) telefonoPortarGroup.style.display = 'block';
            if (telefonoPortarField) telefonoPortarField.style.display = 'block';
            if (operadorSelect) operadorSelect.required = true;
            if (telefonoPortarInput) telefonoPortarInput.required = true;
        } else {
            if (telefonoPortarGroup) telefonoPortarGroup.style.display = 'none';
            if (telefonoPortarField) telefonoPortarField.style.display = 'none';
            if (operadorSelect) operadorSelect.required = false;
            if (telefonoPortarInput) {
                telefonoPortarInput.required = false;
                telefonoPortarInput.value = '';
            }
        }
    }

    function updatePrecioPlan() {
        if (!planSelect || !precioPlanInput) return;
        const plan = planSelect.value;
        if (planPrecioMap[plan]) {
            precioPlanInput.value = normalizarPrecioSelect(planPrecioMap[plan]);
            precioPlanInput.readOnly = true;
        } else {
            precioPlanInput.value = '';
        }
        syncHiddenField('id_precio_plan', precioPlanInput.value);
        updateTipoRenta();
    }

    function filtrarPreciosPorModelo() {
        if (!modeloSelect || !precioVentaSelect) return;
        const modelo = modeloSelect.value;
        const preciosValidos = modeloPreciosMap[modelo];
        const allowedPrices = preciosValidos ? new Set(preciosValidos) : null;
        const mostrarTodos = allowedPrices === null || allowedPrices.size === 0;

        Array.from(precioVentaSelect.options).forEach(option => {
            const valor = parseInt(option.value, 10);
            const isAllowed = mostrarTodos || allowedPrices.has(valor);
            option.disabled = !isAllowed;
            option.style.display = isAllowed ? '' : 'none';
        });

        if (!mostrarTodos && precioVentaSelect.value && !allowedPrices.has(parseInt(precioVentaSelect.value, 10))) {
            precioVentaSelect.value = '';
        }
        syncHiddenField('id_precio_venta', precioVentaSelect.value);
        updateTipoRenta();
    }

    function normalizarPrecioSelect(valor) {
        const numero = Number(valor);
        return Number.isFinite(numero) && Number.isInteger(numero) ? String(numero) : String(valor || '');
    }

    function actualizarPrecioVenta() {
        if (!productoSelect || !precioVentaSelect) return;
        const producto = (productoSelect.value || '').trim();
        const modelo = (modeloSelect ? modeloSelect.value : '').trim();
        const plan = (planSelect ? planSelect.value : '').trim();
        const tipoLinea = (tipoLineaSelect ? tipoLineaSelect.value : '').trim();

        if (producto === 'CHIP') {
            precioVentaSelect.value = '1';
            syncHiddenField('id_precio_venta', '1');
            updateTipoRenta();
            return;
        }

        if (producto === 'PACK') {
            if (!modelo || !tipoLinea) return;
            if (tipoLinea === 'POSTPAGO' && !plan) return;

            const params = new URLSearchParams({
                producto: producto,
                modelo: modelo,
                plan: plan,
                tipo_linea: tipoLinea,
                origen: (origenSelect ? origenSelect.value : '').trim(),
            });

            fetch('/api/ventas/precio-venta/?' + params.toString(), {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.ok) {
                    const precio = normalizarPrecioSelect(data.precio);
                    precioVentaSelect.value = precio;
                    syncHiddenField('id_precio_venta', data.precio);
                } else {
                    precioVentaSelect.value = '';
                    syncHiddenField('id_precio_venta', '');
                    console.warn(data.mensaje || 'Combinación sin precio definido.');
                }
                updateTipoRenta();
            })
            .catch(function() {
                precioVentaSelect.value = '';
                syncHiddenField('id_precio_venta', '');
                updateTipoRenta();
            });
        }
    }

    function updateTipoRenta() {
        if (!productoSelect || !precioVentaSelect || !precioPlanInput || !tipoRentaInput || !origenSelect) return;
        const producto = (productoSelect.value || '').trim();
        const origen = (origenSelect.value || '').trim();
        const valor = producto === 'CHIP' ? parseInt(precioPlanInput.value, 10) : parseInt(precioVentaSelect.value, 10);
        if (!origen || !producto || !valor) {
            tipoRentaInput.value = '';
            return;
        }
        const key = origen + '_' + producto + '_' + valor;
        tipoRentaInput.value = tipoRentaTable[key] || '';
    }

    function limpiarErrorProductoCampo(campo) {
        const ids = {
            origen: 'id_origen_display',
            operador: 'id_operador_display',
            telefono_portar: 'id_telefono_portar_display',
            producto_nombre: 'id_producto_nombre_display',
            modelo_producto: 'id_modelo_producto_display',
            plan_producto: 'id_plan_producto_display',
            tipo_linea: 'id_tipo_linea_display',
            tipo_renta: 'id_tipo_renta'
        };
        const input = document.getElementById(ids[campo] || 'id_producto_validado');
        if (!input) return;
        input.classList.remove('is-invalid');
        const fb = input.parentElement ? input.parentElement.querySelector('.invalid-feedback') : null;
        if (fb) fb.remove();
    }

    function mostrarErrorProductoCampo(campo, texto) {
        const ids = {
            origen: 'id_origen_display',
            operador: 'id_operador_display',
            telefono_portar: 'id_telefono_portar_display',
            producto_nombre: 'id_producto_nombre_display',
            modelo_producto: 'id_modelo_producto_display',
            plan_producto: 'id_plan_producto_display',
            tipo_linea: 'id_tipo_linea_display',
            tipo_renta: 'id_tipo_renta'
        };
        const input = document.getElementById(ids[campo] || 'id_producto_validado');
        if (!input) return;
        input.classList.add('is-invalid');
        let fb = input.parentElement ? input.parentElement.querySelector('.invalid-feedback') : null;
        if (!fb) {
            fb = document.createElement('div');
            fb.className = 'invalid-feedback';
            input.parentElement.appendChild(fb);
        }
        fb.textContent = texto;
    }

    function mostrarProductoMensaje(texto, tipo) {
        if (!productoMensaje) return;
        if (!texto) {
            productoMensaje.className = '';
            productoMensaje.textContent = '';
            productoMensaje.style.display = 'none';
            return;
        }
        productoMensaje.className = 'alert alert-' + (tipo || 'info') + ' mt-2';
        productoMensaje.textContent = texto;
        productoMensaje.style.display = 'block';
    }

    function resetProductoValidacion() {
        if (productoValidado) productoValidado.value = 'false';
        mostrarProductoMensaje('', '');
        ['origen', 'operador', 'telefono_portar', 'producto_nombre', 'modelo_producto', 'plan_producto', 'tipo_linea', 'tipo_renta'].forEach(limpiarErrorProductoCampo);
        actualizarSubmitVenta();
    }

    function actualizarSubmitVenta() {
        const clienteValidado = document.getElementById('id_cliente_validado');
        const productoValidadoActual = document.getElementById('id_producto_validado');
        const clienteOk = !clienteValidado || clienteValidado.value === 'true';
        const productoOk = !productoValidadoActual || productoValidadoActual.value === 'true';
        const submitBtn = document.querySelector('#ventaModalForm button[type="submit"]') ||
                          document.querySelector('#ventaForm button[type="submit"]') ||
                          document.querySelector('#btnGuardarVenta') ||
                          document.querySelector('#btnGuardarVentaFull');
        if (submitBtn) {
            submitBtn.disabled = !(clienteOk && productoOk);
            if (clienteOk && productoOk) {
                submitBtn.classList.add('btn-success');
                submitBtn.classList.remove('btn-primary');
            } else {
                submitBtn.classList.remove('btn-success');
                submitBtn.classList.add('btn-primary');
            }
        }
    }

    function marcarProductoValido(valida) {
        if (productoValidado) productoValidado.value = valida ? 'true' : 'false';
        actualizarSubmitVenta();
    }

    function validarProducto() {
        if (!btnValidarProducto) return;

        const origen = (origenSelect ? origenSelect.value : '').trim();
        const operador = (operadorSelect ? operadorSelect.value : '').trim();
        const telefonoPortar = (telefonoPortarInput ? telefonoPortarInput.value : '').trim();
        const producto = (productoSelect ? productoSelect.value : '').trim();
        const modelo = producto === 'CHIP' ? '' : ((modeloSelect ? modeloSelect.value : '').trim());
        const plan = (planSelect ? planSelect.value : '').trim();
        const tipoLinea = (tipoLineaSelect ? tipoLineaSelect.value : '').trim();

        mostrarProductoMensaje('Validando producto...', 'info');
        const params = new URLSearchParams({
            origen: origen,
            operador: operador,
            telefono_portar: telefonoPortar,
            producto: producto,
            modelo: modelo,
            plan: plan,
            tipo_linea: tipoLinea
        });

        fetch('/api/ventas/validar-producto/?' + params.toString(), {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(response => response.json())
        .then(data => {
            if (data.ok) {
                const precio = normalizarPrecioSelect(data.precio);
                const precioPlan = normalizarPrecioSelect(data.precio_plan || '');
                syncHiddenField('id_precio_venta', data.precio);
                syncHiddenField('id_precio_plan', data.precio_plan || '');
                syncHiddenField('id_tipo_renta', data.tipo_renta || '');
                syncHiddenField('id_tipo_linea', tipoLinea);
                if (precioVentaSelect && data.precio) precioVentaSelect.value = precio;
                if (precioPlanInput && data.precio_plan) precioPlanInput.value = precioPlan;
                if (tipoRentaInput && data.tipo_renta) tipoRentaInput.value = data.tipo_renta;
                marcarProductoValido(true);
                mostrarProductoMensaje(data.mensaje || 'Producto validado correctamente.', 'success');
            } else {
                marcarProductoValido(false);
                mostrarProductoMensaje(data.mensaje || 'No se pudo validar el producto.', 'danger');
                if (data.campo) mostrarErrorProductoCampo(data.campo, data.mensaje || 'Campo inválido.');
            }
        })
        .catch(function() {
            marcarProductoValido(false);
            mostrarProductoMensaje('Error de conexión al validar producto.', 'danger');
        });
    }

    window.actualizarSubmitVenta = actualizarSubmitVenta;
    window.validarProducto = validarProducto;

    if (btnValidarProducto) btnValidarProducto.addEventListener('click', validarProducto);

    if (productoSelect) productoSelect.addEventListener('change', function() {
        syncHiddenField('id_producto_nombre', productoSelect.value);
        updatePorProducto();
        actualizarPrecioVenta();
        resetProductoValidacion();
    });
    if (origenSelect) origenSelect.addEventListener('change', function() {
        syncHiddenField('id_origen', origenSelect.value);
        updatePorOrigen();
        updateTipoRenta();
        resetProductoValidacion();
    });
    if (planSelect) planSelect.addEventListener('change', function() {
        updatePrecioPlan();
        syncHiddenField('id_plan_producto', planSelect.value);
        actualizarPrecioVenta();
        resetProductoValidacion();
    });
    if (modeloSelect) modeloSelect.addEventListener('change', function() {
        filtrarPreciosPorModelo();
        syncHiddenField('id_modelo_producto', modeloSelect.value);
        actualizarPrecioVenta();
        resetProductoValidacion();
    });
    if (precioVentaSelect) precioVentaSelect.addEventListener('change', function() {
        updateTipoRenta();
        syncHiddenField('id_precio_venta', precioVentaSelect.value);
        resetProductoValidacion();
    });
    if (tipoLineaSelect) tipoLineaSelect.addEventListener('change', function() {
        syncHiddenField('id_tipo_linea', tipoLineaSelect.value);
        actualizarPrecioVenta();
        resetProductoValidacion();
    });
    if (operadorSelect) operadorSelect.addEventListener('change', function() {
        syncHiddenField('id_operador', operadorSelect.value);
        resetProductoValidacion();
    });
    if (telefonoPortarInput) telefonoPortarInput.addEventListener('input', function() {
        syncHiddenField('id_telefono_portar', telefonoPortarInput.value);
        resetProductoValidacion();
    });

    const productoNombreInput = document.querySelector('[name="producto_nombre"]');
    if (productoNombreInput && productoSelect && productoNombreInput.value) {
        productoSelect.value = productoNombreInput.value;
        updatePorProducto();
        updateTipoRenta();
    }
    const origenInput = document.querySelector('[name="origen"]');
    if (origenInput && origenSelect && origenInput.value) {
        origenSelect.value = origenInput.value;
        updatePorOrigen();
        updateTipoRenta();
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
    const precioVentaInput = document.querySelector('[name="precio_venta"]');
    if (precioVentaInput && precioVentaSelect && precioVentaInput.value) {
        precioVentaSelect.value = precioVentaInput.value;
        syncHiddenField('id_precio_venta', precioVentaInput.value);
    }
    const tipoLineaInput = document.querySelector('[name="tipo_linea"]');
    if (tipoLineaInput && tipoLineaSelect && tipoLineaInput.value) {
        tipoLineaSelect.value = tipoLineaInput.value;
        syncHiddenField('id_tipo_linea', tipoLineaInput.value);
    }
    const telefonoPortarInputHidden = document.querySelector('[name="telefono_portar"]');
    if (telefonoPortarInputHidden && telefonoPortarInput && telefonoPortarInputHidden.value) {
        telefonoPortarInput.value = telefonoPortarInputHidden.value;
    }

    updatePorProducto();
    updatePorOrigen();
    actualizarPrecioVenta();
    updateTipoRenta();
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
 * Ubigeo - Single source: static/data/ubigeo-peru.json
 * v1.1781212634
 */
window.initUbigeoPeru = function() {
    var d = document.getElementById('id_departamento'), 
        p = document.getElementById('id_provincia'), 
        x = document.getElementById('id_distrito');
    if (!d || !p || !x) return;

    var data = [], load = null;

    function n(s) { return (s||'').toUpperCase().replace(/Á/g,'A').replace(/É/g,'E').replace(/Í/g,'I').replace(/Ó/g,'O').replace(/Ú/g,'U').replace(/Ñ/g,'N'); }

    function fetchUbigeo() {
        if (!load) load = fetch('/static/data/ubigeo-peru.json').then(function(r) { return r.json(); });
        return load;
    }

    function fill(select, items) {
        select.innerHTML = '<option value="">Seleccione</option>';
        items.forEach(function(i) { select.innerHTML += '<option value="'+i[0]+'">'+i[1]+'</option>'; });
    }

    function loadProvs(code) {
        fetchUbigeo().then(function(arr) {
            var items = [];
            for (var i=0;i<arr.length;i++) {
                if (arr[i].departamento===code && arr[i].provincia!=='00' && arr[i].distrito==='00') {
                    items.push([arr[i].provincia, arr[i].nombre]);
                }
            }
            fill(p, items); p.disabled = items.length===0;
            x.innerHTML = '<option value="">Seleccione distrito</option>'; x.disabled = true;
        });
    }

    function loadDists(code, prov) {
        fetchUbigeo().then(function(arr) {
            var items = [];
            for (var i=0;i<arr.length;i++) {
                if (arr[i].departamento===code && arr[i].provincia===prov && arr[i].distrito!=='00') {
                    items.push([arr[i].distrito, arr[i].nombre]);
                }
            }
            fill(x, items); x.disabled = items.length===0;
        });
    }

    d.addEventListener('change', function() { loadProvs(d.value); });
    p.addEventListener('change', function() { loadDists(d.value, p.value); });

    if (d.value) { loadProvs(d.value); if (p.value) loadDists(d.value, p.value); }
};

document.addEventListener('DOMContentLoaded', function() {
    if (typeof initUbigeoPeru==='function') initUbigeoPeru();
});

document.addEventListener('ventaFormLoaded', function() {
    if (typeof initUbigeoPeru==='function') initUbigeoPeru();
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
    const urlRegistrar = baseId ? "/ventas/registrar-cliente/" + baseId + "/" : "";
    const urlRecargar = baseId ? "/ventas/recargar-lead/" + baseId + "/" : "";

    const btnBuscar = document.getElementById('btnBuscarCliente');
    const btnValidar = document.getElementById('btnValidarCliente');
    const btnRecargar = document.getElementById('btnRecargarLead');
    const btnRegistrarCliente = document.getElementById('btnRegistrarCliente');
    const campoDocumento = document.getElementById('id_cliente_documento');
    const campoTipoDocumento = document.getElementById('id_cliente_tipo_documento');
    const mensaje = document.getElementById('clienteMensaje');
    const camposCliente = document.querySelectorAll('.cliente-campos input');

    function setValue(id, valor) {
        const el = document.getElementById(id);
        if (el) el.value = valor;
    }

    function setText(id, valor) {
        const el = document.getElementById(id);
        if (el) el.textContent = valor;
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

    function marcarSeccionValida(valida) {
        const campoValidado = document.getElementById('id_cliente_validado');
        if (campoValidado) {
            campoValidado.value = valida ? 'true' : 'false';
        }
        actualizarSubmitVenta();
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
        fetch(urlBuscar + '?tipo_documento=' + encodeURIComponent(tipo) + '&documento=' + encodeURIComponent(documento), {
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
                bloquearCamposCliente(true);
                limpiarErroresCampos();
                marcarSeccionValida(true);
                mostrarMensaje('Cliente encontrado: ' + c.nombres + ' ' + c.paterno + ' ' + c.materno, 'success');
            } else {
                setValue('id_cliente_nombres', '');
                setValue('id_cliente_paterno', '');
                setValue('id_cliente_materno', '');
                setValue('id_cliente_documento', documento);
                setValue('id_cliente_telefono_1', '');
                setValue('id_cliente_telefono_2', '');
                bloquearCamposCliente(false);
                limpiarErroresCampos();
                marcarSeccionValida(false);
                mostrarMensaje('Cliente no encontrado. Complete los datos y registre.', 'warning');
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
        fetch(urlValidar + '?tipo_documento=' + encodeURIComponent(tipo) + '&documento=' + encodeURIComponent(documento), {
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
                bloquearCamposCliente(true);
                limpiarErroresCampos();
                marcarSeccionValida(true);
                mostrarMensaje('Cliente existente validado. Datos protegidos.', 'success');
            } else {
                const nombres = document.getElementById('id_cliente_nombres');
                const paterno = document.getElementById('id_cliente_paterno');
                const materno = document.getElementById('id_cliente_materno');

                let hayErrores = false;

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
                if (materno && materno.value.trim() && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(materno.value.trim())) {
                    mostrarErrorCampo(materno, 'Materno solo debe contener letras.');
                    hayErrores = true;
                }

                if (!hayErrores) {
                    bloquearCamposCliente(false);
                    limpiarErroresCampos();
                    if (btnRegistrarCliente) {
                        btnRegistrarCliente.style.display = 'inline-block';
                    }
                    mostrarMensaje('Cliente no encontrado. Complete los datos y haga clic en "Registrar Cliente".', 'warning');
                } else {
                    bloquearCamposCliente(false);
                }
            }
        })
        .catch(function() {
            mostrarMensaje('Error al validar cliente.', 'danger');
        });
    }

    function registrarCliente() {
        const tipo = campoTipoDocumento ? campoTipoDocumento.value.trim() : 'DNI';
        const documento = campoDocumento.value.trim();
        const nombres = document.getElementById('id_cliente_nombres');
        const paterno = document.getElementById('id_cliente_paterno');
        const materno = document.getElementById('id_cliente_materno');
        const tel1 = document.getElementById('id_cliente_telefono_1');
        const tel2 = document.getElementById('id_cliente_telefono_2');

        if (!documento) {
            mostrarErrorCampo(campoDocumento, 'Documento es obligatorio.');
            return;
        }
        if (!nombres || !nombres.value.trim()) {
            mostrarErrorCampo(nombres, 'Nombres es obligatorio.');
            return;
        }
        if (!paterno || !paterno.value.trim()) {
            mostrarErrorCampo(paterno, 'Paterno es obligatorio.');
            return;
        }

        mostrarMensaje('Registrando cliente...', 'info');

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        const params = new URLSearchParams();
        params.append('cliente_tipo_documento', tipo);
        params.append('cliente_documento', documento);
        params.append('cliente_nombres', nombres.value.trim());
        params.append('cliente_paterno', paterno.value.trim());
        params.append('cliente_materno', materno ? materno.value.trim() : '');
        params.append('cliente_telefono_1', tel1 ? tel1.value.trim() : '');
        params.append('cliente_telefono_2', tel2 ? tel2.value.trim() : '');
        params.append('csrfmiddlewaretoken', csrfToken);

        fetch(urlRegistrar, {
            method: 'POST',
            headers: {'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded'},
            body: params.toString()
        })
        .then(r => r.json())
        .then(function(data) {
            if (data.ok) {
                bloquearCamposCliente(true);
                limpiarErroresCampos();
                if (btnRegistrarCliente) {
                    btnRegistrarCliente.style.display = 'none';
                }
                marcarSeccionValida(true);
                mostrarMensaje(data.mensaje, 'success');
            } else {
                mostrarMensaje(data.mensaje || 'Error al registrar cliente.', 'danger');
            }
        })
        .catch(function() {
            mostrarMensaje('Error de conexión al registrar cliente.', 'danger');
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
                setText('id_base_telefono', l.telefono || '');
                setText('id_base_nombres', l.nombres || '');
                setText('id_base_paterno', l.paterno || '');
                setText('id_base_materno', l.materno || '');
                setText('id_base_documento', l.documento || '');
                setText('id_base_correo', l.correo || '');
                setText('id_base_observaciones', l.observaciones || '');
                if (campoTipoDocumento) setValue('id_cliente_tipo_documento', l.tipo_documento || 'DNI');
                setValue('id_cliente_documento', l.documento || '');
                setValue('id_cliente_nombres', l.nombres || '');
                setValue('id_cliente_paterno', l.paterno || '');
                setValue('id_cliente_materno', l.materno || '');
                setValue('id_cliente_telefono_1', l.telefono || '');
                setValue('id_cliente_telefono_2', '');
                bloquearCamposCliente(false);
                limpiarErroresCampos();
                marcarSeccionValida(false);
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
    }
    if (btnValidar) {
        btnValidar.addEventListener('click', validarCliente);
    }
    if (btnRecargar) {
        btnRecargar.addEventListener('click', recargarLead);
    }
    if (btnRegistrarCliente) {
        btnRegistrarCliente.addEventListener('click', registrarCliente);
    }

    // Prevenir submit al presionar Enter en campos del cliente
    if (campoDocumento) {
        campoDocumento.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.stopPropagation();
                if (btnBuscar) buscarCliente();
            }
        });
    }

    const btnTelefonoPortar = document.getElementById('btnTelefonoPortar');
    if (btnTelefonoPortar) {
        btnTelefonoPortar.addEventListener('click', function() {
            const campoPortar = document.getElementById('id_telefono_portar_display');
            const tel1 = document.getElementById('id_cliente_telefono_1');
            const tel2 = document.getElementById('id_cliente_telefono_2');
            const leadTel = document.getElementById('id_base_telefono_display');
            let valor = '';
            if (leadTel && leadTel.textContent) {
                valor = leadTel.textContent.trim();
            } else if (tel1 && tel1.value) {
                valor = tel1.value;
            } else if (tel2 && tel2.value) {
                valor = tel2.value;
            }
            if (campoPortar) {
                campoPortar.value = valor;
                campoPortar.dispatchEvent(new Event('input'));
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', function() {
    if (typeof initClienteSearch === 'function') {
        initClienteSearch();
    }
});

// Prevent form submission if cliente section is not validated (for full page form)
document.addEventListener('DOMContentLoaded', function() {
    const ventaForm = document.getElementById('ventaForm');
    if (ventaForm) {
        ventaForm.addEventListener('submit', function(e) {
            const clienteValidado = document.getElementById('id_cliente_validado');
            const productoValidado = document.getElementById('id_producto_validado');
            const clienteOk = !clienteValidado || clienteValidado.value === 'true';
            const productoOk = !productoValidado || productoValidado.value === 'true';

            if (!clienteOk || !productoOk) {
                e.preventDefault();
                const clienteMensaje = document.getElementById('clienteMensaje');
                const productoMensaje = document.getElementById('productoMensaje');
                if (!clienteOk && clienteMensaje) {
                    clienteMensaje.className = 'alert alert-warning';
                    clienteMensaje.textContent = 'Debe validar o registrar al cliente antes de guardar la venta.';
                    clienteMensaje.style.display = 'block';
                }
                if (!productoOk && productoMensaje) {
                    productoMensaje.className = 'alert alert-warning';
                    productoMensaje.textContent = 'Debe validar el producto antes de guardar la venta.';
                    productoMensaje.style.display = 'block';
                }
            }
        });
    }
});