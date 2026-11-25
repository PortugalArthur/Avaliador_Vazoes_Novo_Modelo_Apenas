# Avaliador de Vazões HTML — Somente Novo Modelo

Versão **1.2.2**. Avalia as vazões incrementais de uma ou duas versões do Novo Modelo (COBRE) contra os respectivos históricos, em um relatório HTML offline.

## Pacote portátil para Windows x64

1. Baixe o [ZIP portátil](https://github.com/PortugalArthur/Avaliador_Vazoes_Novo_Modelo_Apenas/releases/latest/download/AVALIADOR_VAZOES_NOVO_MODELO_WINDOWS_X64.zip).
2. Extraia todo o ZIP para uma pasta gravável e mantenha `_python` ao lado dos atalhos.
3. Abra `GERAR_RELATORIO_HTML.bat` e selecione o deck e o Parquet de cada versão.

O ZIP inclui CPython, Tcl/Tk e as dependências, incluindo a edição compatível do Polars. O programa funciona sem instalar Python, alterar o PATH ou acessar a internet. O deck e os Parquets do estudo são selecionados separadamente.

## Análises

- **Análise** avalia uma versão do Novo Modelo.
- **Comparação** avalia duas versões do Novo Modelo, com um deck e um período histórico para cada fonte. As duas versões devem cobrir as mesmas usinas e os mesmos meses do horizonte.
- A visão geral do SIN exibe Welch, Levene, KS, correlação espacial entre duas bacias por estágio e análise de sequências. O raio espectral anual aparece no ranking do teste de médias quando os parâmetros do ajuste estão disponíveis.

Os relatórios ficam em `relatorios/` e abrem offline no navegador. [Guia de uso](documentacao/README.md)

## Atalhos auxiliares

- `GERAR_PARQUET_NOVO_MODELO.bat` consolida as saídas de vazão do Novo Modelo.
- `EXPORTAR_PARQUET_EXCEL.bat` exporta os registros selecionados para Excel.
- `EXPORTAR_HISTORICO_EXCEL.bat` exporta o histórico selecionado para Excel.

## Código-fonte

Os atalhos também aceitam uma instalação completa de Python x64 a partir de 3.10 com Tcl/Tk. Para instalar dependências, gerar o ZIP ou rodar os testes no Windows, execute na raiz do repositório.

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s testes -v
python -m infraestrutura.empacotar_portatil --destino outputs/distribuicao --ref HEAD
```

A verificação JavaScript do cálculo por bacia usa Node.js quando disponível. Os testes usam casos gerados e o pacote é montado a partir dos arquivos versionados no commit.
