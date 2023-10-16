function showModalConfig(element) {
    $("#loading-overlay").show();
        const row = element.closest('tr');
        const cells = row.getElementsByTagName('td');
        const tag = cells[0].textContent;
        const equip = cells[1].textContent;
        const localizacao = cells[3].textContent;
        const responsavel = cells[4].textContent;
        const tipoControle = cells[5].textContent;
        const ult_calibracao = cells[6].textContent;
        const periodicidade = cells[7].textContent;
        const metodo = cells[8].textContent;
        const status = cells[10].textContent;

        $.ajax({
            success: function (response) {
                // Defina o texto do título do modal com base na 'tag'
                var unidades = response.unidades;
                var faixa_nominal = response.faixa_nominal;

                // Atualize o campo de seleção de Unidade
                var selectUnidade = $('#editar_unidade_config');
                $.each(unidades, function (unidade) {
                    selectUnidade.append($('<option>', {
                        value: unidade,
                        text: unidade
                    }));
                });

                // Atualize o campo de seleção de Faixa Nominal
                var selectFaixaNominal = $('#editar_nominal_config');
                $.each(faixa_nominal, function (fn) {
                    selectFaixaNominal.append($('<option>', {
                        value: fn,
                        text: fn
                    }));
                });

                $("#loading-overlay").hide();
                $('.modal-title').text(tag);

                // Defina os valores dos campos de entrada no modal
                $('#editar_equipamento_config').val(equip);
                $('#editar_localizacao_config').val(localizacao);
                $('#editar_responsavel_config').val(responsavel);
                $('#editar_controle_config').val(tipoControle);
                $('#editar_ult_calibracao_config').val(ult_calibracao);
                $('#editar_periodicidade_config').val(periodicidade);
                $('#editar_metodo_config').val(metodo);
                $('#editar_status_config').val(status);
    
                // Exiba o modal
                $('#config').modal('show');
                $('#config').on('show.bs.modal', function () {
                    $('body').addClass('modal-open');
                });

                // Fechar o modal ao clicar no botão de fechar
                $('#config').on('click', '.close', function () {
                    $('#config').modal('hide');
                    $('body').removeClass('modal-open');
                });
            },
            error: function (error) {
                alert('Erro. Atualize a página');
                console.log(error);
            }
        });
    }

    