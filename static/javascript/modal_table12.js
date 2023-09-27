function showModal(event) {
    $("#loading-overlay").show();
    const isTable1 = event.currentTarget.closest('.table-1') !== null;
    const isTable2 = event.currentTarget.closest('.table-2') !== null;
    if (isTable1) {
        // Código para a Tabela 1
        const tag = event.currentTarget.querySelector('td').textContent;
        const equip = event.currentTarget.querySelector('td[data-label="Equip"]').textContent;
        const unidade = event.currentTarget.querySelector('td[data-label="Unidade"]').textContent;
        const localizacao = event.currentTarget.querySelector('td[data-label="Localizacao"]').textContent;
        const responsavel = event.currentTarget.querySelector('td[data-label="Responsavel"]').textContent;
        const tipoControle = event.currentTarget.querySelector('td[data-label="Tipo de Controle"]').textContent;
        const ult_calibracao = event.currentTarget.querySelector('td[data-label="Ult.Calib"]').textContent;
        const periodicidade = event.currentTarget.querySelector('td[data-label="Periodicidade"]').textContent;
        const metodo = event.currentTarget.querySelector('td[data-label="Metodo"]').textContent;
        const faixaNominal = event.currentTarget.querySelector('td[data-label="Faixa Nominal"]').textContent;
        const status = event.currentTarget.querySelector('td[data-label="Status"]').textContent;

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
        } else if (isTable2) {
            // Código para a Tabela 1
            const tag = event.currentTarget.querySelector('td').textContent;
            $.ajax({
                url: '/',
                method: 'POST',
                data: { tag: tag },
                dataType: 'json',
                success: function (serialized_data) { // Adicione o parâmetro 'data' aqui
                    // Defina o texto do título do modal com base na 'tag'
                    
                    console.log(serialized_data)

                    $("#loading-overlay").hide();
                    $('.modal-title').text("Histórico: " + tag);
            
                    // Exiba o modal
                    $('#modalGanhar2').on('show.bs.modal', function () {
                        $('body').addClass('modal-open');
                    });
                    $('#modalGanhar2').modal('show');
            
                    setTimeout(function() {
                        modal.style.display = 'block';
                    }, 1000);
                    // Fechar o modal ao clicar no botão de fechar
                    $('#modalGanhar2').on('click', '.close', function () {
                        $('#modalGanhar2').modal('hide');
                        $('body').removeClass('modal-open');
                    });
            
                    const historicoTable = $('<table></table>').addClass('responsive-table');
            
                    // Crie cabeçalhos da tabela
                    historicoTable.append('<thead><tr><th>N° Calibração</th><th>Data</th><th>Download</th></tr></thead>');
            
                    // Crie o corpo da tabela
                    const historicoTableBody = $('<tbody></tbody>');
            
                    // Itere pela serialized_data e crie linhas da tabela
                    serialized_data.forEach(function (item) {
                        const row = $('<tr style="cursor: default;">');
                        row.append($('<td></td>').text(item[2])); // N° Calibração
                        row.append($('<td></td>').text(item[0])); // Data
                        row.append($('<td></td>').html(`<a href="${item[1]}"></a>`)); // Download
                        historicoTableBody.append(row);
                    });
            
                    historicoTable.append(historicoTableBody);
            
                    // Adicione a tabela ao elemento #historico-table no seu HTML
                    $('#historico-table').html(historicoTable);
            
                    // Resto do código para exibir o modal
                },
                error: function (error) {
                    alert('Erro');
                    console.log(error);
                }
            });
        }
    }
// Obtém todos os elementos 'tr' na tabela
const trElements = document.querySelectorAll('.modal-trigger');

// Adiciona um ouvinte de eventos de clique a cada 'tr'
trElements.forEach(function(tr) {
    tr.addEventListener('click', showModal);
});