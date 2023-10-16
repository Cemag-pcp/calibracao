function showModal2(event) {
    $("#loading-overlay").show();
    const tag = event.currentTarget.querySelector('td').textContent;
    const data_chegada = $('#editar_data_calib').val();
    $.ajax({
        url: '/',
        method: 'POST',
        data: { 
                tag: tag, 
                data_chegada: data_chegada 
              },
        dataType: 'json',
        success: function (lista_historico) { // Adicione o parâmetro 'data' aqui
            // Defina o texto do título do modal com base na 'tag'
            
            console.log(lista_historico)

            $("#loading-overlay").hide();
            $('.modal-title').text("Histórico: " + tag);

            // Exiba o modal
            $('#modalGanhar2').on('show.bs.modal', function () {
                $('body').addClass('modal-open');
            });
            $('#modalGanhar2').modal('show');

            // Fechar o modal ao clicar no botão de fechar
            $('#modalGanhar2').on('click', '.close', function () {
                $('#modalGanhar2').modal('hide');
                $('body').removeClass('modal-open');
            });

            const historicoTable = $('<table></table>').addClass('responsive-table');

            // Crie cabeçalhos da tabela
            historicoTable.append(`
                <thead>
                    <tr>
                    <th class="cabecalho" style="display:None">ID</th>
                    <th class="cabecalho">N° Calibração</th>
                    <th class="cabecalho">Data</th>
                    <th class="cabecalho">EMA</th>
                    <th class="cabecalho">EMT</th>
                    <th class="cabecalho">Links Certificados</th>
                    <th class="cabecalho">Editar</th>
                    </tr>
                </thead>
            `);
            // Crie o corpo da tabela
            const historicoTableBody = $('<tbody></tbody>');

            let valoresOriginais = [];

            // Itere pela lista_historico e crie linhas da tabela
            lista_historico.forEach(function (item) {
                const row = $('<tr style="cursor: default;">');
                const colunas = []; // Array para armazenar os valores originais de cada coluna

                colunas.push(item[0]); // ID
                colunas.push(item[5]); // N° Calibração
                colunas.push(item[1]); // Data
                colunas.push(item[3]); // EMA
                colunas.push(item[4]); // EMT
                colunas.push(item[2]); // Links Certificados

                valoresOriginais.push(colunas); // Armazena os valores originais desta linha

                row.append($('<td data-label="ID" style="display:None"></td>').text(item[0])); // ID
                row.append($('<td data-label="N° Calib."></td>').text(item[5])); // N° Calibração
                row.append($('<td data-label="Data"></td>').text(item[1])); // Data
                row.append($('<td data-label="EMA"></td>').text(item[3])); // EMA
                row.append($('<td data-label="EMT"></td>').text(item[4])); // EMT

                const downloadLink = $('<td data-label="Link Certificado"></td>');
                if (item[2]) {
                    const link = $(`<a href="${item[2]}"><i class="fa-solid fa-download" style="color: black;"></i></a>`);
                    downloadLink.append(link);
                } else {
                    const redIcon = $('<i class="fa-solid fa-download" style="color: red;"></i>');
                    downloadLink.append(redIcon);
                    redIcon.on('click', function () {
                        alert('Não possui certificado.');
                    });
                }
                
                // Botão de edição
                const editButton = $('<button class="botão_modal_tag">Editar</button>');
                editButton.on('click', function () {
                    // Ao clicar no botão de edição, transforme os itens da tabela em inputs
                    transformarEmInputs(item, row);
                });

                row.append(downloadLink);
                row.append($('<td></td>').append(editButton));
                historicoTableBody.append(row);
            });
            function transformarEmInputs(item, row) {
                // Itere pelos elementos td na linha
                row.find('td').each(function (index, td) {
                    const valorOriginal = $(td).text();
                    let input;
            
                    if (index === 0) { // N° Calibração (não editável, mantenha como texto)
                        input = $('<span class="id">' + valorOriginal + '</span>');
                    } else if(index === 1){
                        input = $('<span>' + valorOriginal + '</span>');
                    } else if (index === 2) { // Data (assumindo que é uma data no formato yyyy-mm-dd)
                        input = $('<input type="date" class="formulario_modal data-input">');
                        input.val(valorOriginal);
                    } else if (index === 3 || index === 4) { // EMA ou EMT (assumindo que são números)
                        input = $('<input type="number" class="formulario_modal">');
                    } else if (index === 5) { // Coluna de "Links Certificados" (mantenha como texto)
                        input = $('<input type="url" class="formulario_modal">');
                        input.val(valorOriginal); // Defina o valor do input como o valor original
                        $(td).html(input);
                    } else { // Coluna "Editar"
                        input = $('<input type="text" class="formulario_modal">');
                    }
            
                    if (index !== 0 || index !== 0) { // Adicione um botão "Salvar" apenas para colunas editáveis
                        input.val(valorOriginal);
                        $(td).html(input);
                    }
            
                    if (index === 6) { // Coluna de "Editar"
                        const editarButton = $('<button class="botão_modal_tag">Salvar</button>');
                        editarButton.on('click', function () {
                            
                            // Crie um objeto para armazenar os valores antigos e novos
                            const valores = {
                                valor_antigo_data: null,
                                valor_novo_data: null,
                                valor_antigo_emt: null,
                                valor_novo_emt: null,
                                valor_antigo_ema: null,
                                valor_novo_ema: null,
                                link_certificado: null,
                                numero_calibracao:null
                            };
                            const id = $('span.id').val();
                            const dataInput = $('input.data-input').val();

                            // Obtenha os valores antigos antes de atualizar a linha
                            const valoresAntigos = [];
                            row.find('td:not(:first-child)').each(function (index, td) {
                                const valorAntigo = $(td).text();
                                valoresAntigos.push(valorAntigo);
                                // Atribua os valores antigos ao objeto
                                switch (index) {
                                    case 1: // Data
                                        valores.id = item[0];
                                        break;
                                    case 2: // EMA
                                        valores.link_certificado = item[2];
                                        break;
                                    case 3: // EMT
                                        valores.valor_antigo_ema = item[3];
                                        break;
                                    case 4: // Link Certificado
                                        valores.data_antiga = item[1];
                                        break;
                                    case 5: // Link Certificado
                                        valores.valor_antigo_emt = item[4];
                                        break;
                                }
                            });

                            // Atualize os valores na linha com os novos valores dos inputs
                            row.find('input').each(function (index, input) {
                                
                                const novoValor = $(input).val();
                                $(row.find('td:not(:first-child)')[index]).text(novoValor);
                                
                                // Atribua os novos valores ao objeto
                                switch (index) {
                                    case 1: // EMA
                                        valores.valor_novo_ema = novoValor;
                                        break;
                                    case 2: // EMA
                                        valores.valor_novo_emt = novoValor;
                                        break;
                                    case 3: // EMT
                                        valores.link_novo_certificado = novoValor;
                                        break;
                                    case 4: // EMT
                                        valores.data_novo = novoValor;
                                        break;
                                }
                            });

                            // Restaure o botão de "Editar" como "Salvar" após a edição
                            $("#loading-overlay").show();
                            $(this).text('Editar');
                            $(this).removeClass('btn-success');
                            $(this).removeClass('btn-primary');
                            $(this).addClass('botão_modal_tag');
                            const loadingOverlay = $("#loading-overlay");
                            // Envie os valores para a rota '/editar_modal_historico'
                            const dados = {
                                valoresNovos: valores,
                                dataInput:dataInput,
                                tag:tag,
                                id:id
                            };

                            $.ajax({
                                url: '/editar_modal_historico',
                                method: 'POST',
                                contentType: 'application/json', // Defina o Content-Type como JSON
                                data: JSON.stringify(dados), // Converta o objeto para uma string JSON
                                dataType: 'json',
                                success: function (resposta) {
                                    //pass
                                },
                                error: function (error) {
                                    console.log(error);
                                    $("#loading-overlay").hide();
                                }
                            });
                        
                            window.location.reload();
                        
                            $("#loading-overlay").hide();
                            
                        });
            
                        $(td).html(editarButton);
                    }
                });
            }

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

// Obtém todos os elementos 'tr' na tabela
const trElements2 = document.querySelectorAll('.modal-trigger2');

// Adiciona um ouvinte de eventos de clique a cada 'tr'
trElements2.forEach(function(tr) {
    tr.addEventListener('click', showModal2);
});