function showModalConfig(tag) {
    $("#loading-overlay").show();
        // Código para a Tabela 1

        // Seletor para cada elemento 'td' com um atributo 'data-label'
        const equip = document.querySelector('td[data-label="Equip"]').textContent;
        const unidade = document.querySelector('td[data-label="Unidade"]').textContent;
        const localizacao = document.querySelector('td[data-label="Localizacao"]').textContent;
        const responsavel = document.querySelector('td[data-label="Responsavel"]').textContent;
        const tipoControle = document.querySelector('td[data-label="Tipo de Controle"]').textContent;
        const ult_calibracao = document.querySelector('td[data-label="Ult.Calib"]').textContent;
        const periodicidade = document.querySelector('td[data-label="Periodicidade"]').textContent;
        const metodo = document.querySelector('td[data-label="Metodo"]').textContent;
        const faixaNominal = document.querySelector('td[data-label="Faixa Nominal"]').textContent;
        const status = document.querySelector('td[data-label="Status"]').textContent;

        $.ajax({
            success: function () {
                // Defina o texto do título do modal com base na 'tag'
                $("#loading-overlay").hide();
                $('.modal-title').text(tag);

                // Defina os valores dos campos de entrada no modal
                $('#editar_equipamento_config').val(equip);
                $('#editar_nominal_config').val(faixaNominal);
                $('#editar_unidade_config').val(unidade);
                $('#editar_localizacao_config').val(localizacao);
                $('#editar_responsavel_config').val(responsavel);
                $('#editar_controle_config').val(tipoControle);
                $('#editar_periodicidade_config').val(periodicidade);
                $('#editar_metodo_config').val(metodo);
                $('#editar_ult_calibracao_config').val(ult_calibracao);
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