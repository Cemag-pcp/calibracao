function showModal(tag, equip, unidade, localizacao, responsavel, tipoControle, ult_calibracao, periodicidade, metodo, faixaNominal, status) {
    $("#loading-overlay").show();

    $.ajax({
        success: function () {
            // Defina o texto do título do modal com base na 'tag'

            $('.modal-title').text(tag);

            // Defina os valores dos campos de entrada no modal
            $('#editar_nome').val(equip);
            $('#editar_matricula').val(faixaNominal);
            $('#editar_unidade').val(unidade);
            $('#editar_localizacao').val(localizacao);
            $('#editar_responsavel').val(responsavel);
            $('#editar_controle').val(tipoControle);
            $('#editar_periodicidade').val(periodicidade);
            $('#editar_metodo').val(metodo);
            $('#editar_ult_calibracao').val(ult_calibracao);
            $('#editar_status').val(status);

            // Exiba o modal

            // Espera 3 segundos (3000 milissegundos) e então abre o modal
            setTimeout(function () {
                $("#loading-overlay").hide();
                $('#modalGanhar').modal('show');
                $('#modalGanhar').on('show.bs.modal', function () {
                    $('body').addClass('modal-open');
                });
            }, 1000);

            // Fechar o modal ao clicar no botão de fechar
            $('#modalGanhar').on('click', '.close', function () {
                $('#modalGanhar').modal('hide');
                $('body').removeClass('modal-open');
            });
        },
        error: function (error) {
            alert('Essa Ordem de Serviço não contém imagem ou vídeo');
            console.log(error);
        }
    });
}
