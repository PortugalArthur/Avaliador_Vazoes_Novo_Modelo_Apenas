# Contexto para continuar — Avaliador de Vazões HTML — Somente Novo Modelo

Atualizado em **25/11/2026**.

## Estado publicado

- Código de trabalho na branch `main`. A release **v1.2.2** foi empacotada a partir do commit `c21c474`. [Código da release](https://github.com/PortugalArthur/Avaliador_Vazoes_Novo_Modelo_Apenas/tree/v1.2.2)
- O pacote portátil é para **Windows x64** e inclui CPython, Tcl/Tk e dependências, com a variante compatível do Polars. [Baixar o ZIP](https://github.com/PortugalArthur/Avaliador_Vazoes_Novo_Modelo_Apenas/releases/download/v1.2.2/AVALIADOR_VAZOES_NOVO_MODELO_WINDOWS_X64.zip) · [SHA-256](https://github.com/PortugalArthur/Avaliador_Vazoes_Novo_Modelo_Apenas/releases/download/v1.2.2/AVALIADOR_VAZOES_NOVO_MODELO_WINDOWS_X64.sha256)
- A outra edição fica em um repositório separado. [edição completa com NEWAVE](https://github.com/PortugalArthur/avaliador-vazoes-html)

## O que foi feito

Esta edição recebeu um repositório próprio. O relatório usa o mesmo motor estatístico da edição completa v1.2.2 e a janela da variante Somente Novo Modelo. A geração de relatórios, pela janela e pela linha de comando, foi dedicada ao COBRE. A comparação usa a opção `--novo-referencia` para o Parquet B, junto com `--deck-referencia`.

A v1.2.2 deste repositório foi a primeira release portátil da edição. O pacote inclui os quatro atalhos de relatório, consolidação do Novo Modelo e exportação para Excel.

Nesta edição, é possível:

- Analisar uma versão do Novo Modelo (COBRE).
- Comparar duas versões do Novo Modelo, com nomes distintos e um deck e um período histórico para cada fonte.

Na **Visão geral do SIN → Correlação espacial**, escolha **Bacia A** e **Bacia B**. Para cada estágio, o sintético calcula Pearson sobre as somas das vazões incrementais, pareadas pelo mesmo cenário. O histórico pareia os totais do mesmo mês civil pelo mesmo ano. O relatório inclui a composição das bacias, os totais pareados e as contagens do memorial. [Interface](recursos/interacao.js) · [Cálculo por bacia](recursos/correlacao_bacias.js)

## Rodar em outro computador

1. Baixe o ZIP portátil na release e extraia todo o conteúdo em uma pasta gravável.
2. Mantenha a pasta `_python` junto aos atalhos e execute `GERAR_RELATORIO_HTML.bat`.
3. Selecione o deck, o Parquet de cenários e o período histórico de cada fonte. Os arquivos de estudo devem ser levados separadamente. O deck fornece `system/hydros.json`, `stages.json` e `scenarios/inflow_history.parquet`.
4. Gere um HTML novo para ver a interface desta release. Cada relatório já gerado incorpora os recursos da versão que o criou.

`GERAR_PARQUET_NOVO_MODELO.bat` consolida as saídas de cada versão COBRE. Os atalhos `EXPORTAR_PARQUET_EXCEL.bat` e `EXPORTAR_HISTORICO_EXCEL.bat` ajudam a conferir os insumos. [Guia de uso](documentacao/README.md)

## Continuar o desenvolvimento

Clone o repositório e abra a pasta no VS Code. Para os comandos de desenvolvimento no Windows, use Python x64 completo com Tcl/Tk e pip. Os testes JavaScript usam Node.js quando disponível.

```powershell
git clone https://github.com/PortugalArthur/Avaliador_Vazoes_Novo_Modelo_Apenas.git
cd Avaliador_Vazoes_Novo_Modelo_Apenas
python -m pip install -r requirements.txt
python -m unittest discover -s testes -v
```

- [Entradas e geração](aplicacao/executar.py) · [Carregamento de fontes e histórico](aplicacao/fontes.py) · [Motor do relatório](relatorio/motor.py).
- [Inicializador dos atalhos](iniciar_avaliador.bat) · [Empacotador Windows](infraestrutura/empacotar_portatil.py) · [Workflow de release](.github/workflows/distribuir-windows.yml).

Para preparar um ZIP local a partir de um commit, execute o empacotador. Ele arquiva os arquivos versionados, inclui o Python e testa os atalhos com o PATH restrito.

```powershell
python -m infraestrutura.empacotar_portatil --destino outputs/distribuicao --ref HEAD
```

Para publicar outra versão, atualize `VERSAO` em `aplicacao/executar.py` e acompanhe o workflow em `main`. Ele verifica o pacote antes de publicar o ZIP e o SHA-256. Uma release existente é preservada.

## Validação registrada

- **61 testes automatizados** passaram, incluindo a comparação entre dois decks com IDs distintos e a rejeição de Parquets NEWAVE para geração de relatórios.
- A linha de comando gerou HTML com uma e com duas versões COBRE.
- O GitHub Actions verificou os quatro atalhos e publicou o ZIP com seu SHA-256.

A comparação entre as edições locais e o código da v1.2.2 completa usou os mesmos decks, Parquets e períodos históricos. Os blocos de resultados nos modos em comum foram idênticos. [Execução do empacotamento](https://github.com/PortugalArthur/Avaliador_Vazoes_Novo_Modelo_Apenas/actions/runs/45677161014)

## Diagnóstico dos atalhos

Na pasta extraída em que `_python` está ao lado das `.bat`, rode o atalho com a opção de diagnóstico para conferir a inicialização.

```cmd
cmd /d /c "GERAR_RELATORIO_HTML.bat --verificar-ambiente"
```

Se houver falha, registre o nome do ZIP, o caminho completo da pasta extraída e a saída do comando. O relato conhecido de erro de sintaxe ocorreu na outra edição e está registrado no contexto daquele repositório. [Diagnóstico da edição completa](https://github.com/PortugalArthur/avaliador-vazoes-html/blob/main/CONTEXTO_CONTINUIDADE.md)
