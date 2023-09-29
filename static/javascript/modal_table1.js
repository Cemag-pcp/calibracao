// Adicione um ouvinte de eventos de clique aos botões com a classe 'btn-trigger-modal'
const btnElements = document.querySelectorAll('.btn-trigger-modal');

btnElements.forEach(function(btn) {
    btn.addEventListener('click', function(event) {
        const tag = event.currentTarget.getAttribute('data-tag');
        showModal(tag);
    });
});

function showModal(tag) {
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
                $('#modalGanhar').modal('show');
                $('#modalGanhar').on('show.bs.modal', function () {
                    $('body').addClass('modal-open');
                });

                setTimeout(function () {
                    modal.style.display = 'block';
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
