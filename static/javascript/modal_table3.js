function showModalEnvio(Tag) {
    $("#loading-overlay").show();
        // Código para a Tabela 1

        $.ajax({
            success: function () {
                // Defina o texto do título do modal com base na 'tag'
                $("#loading-overlay").hide();

                $('.modal-title').text(Tag + ": " + "Envio de equipamento para calibração");
                // Exiba o modal
                $('#modalGanhar3').modal('show');
                $('#modalGanhar3').on('show.bs.modal', function () {
                    $('body').addClass('modal-open');
                });

                // Fechar o modal ao clicar no botão de fechar
                $('#modalGanhar3').on('click', '.close', function () {
                    $('#modalGanhar3').modal('hide');
                    $('body').removeClass('modal-open');
                });
            },
            error: function (error) {
                alert('Essa Ordem de Serviço não contém imagem ou vídeo');
                console.log(error);
            }
        });
    }
