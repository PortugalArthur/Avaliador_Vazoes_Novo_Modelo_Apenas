# Avaliador de Vazões HTML — Somente Novo Modelo

Versão **1.2.2**. Avalia vazões incrementais de uma ou duas versões do Novo Modelo (COBRE) contra os respectivos históricos, em relatório HTML offline.

## Pacote portátil para Windows x64

1. Baixe o [ZIP portátil](https://github.com/PortugalArthur/Avaliador_Vazoes_Novo_Modelo_Apenas/releases/latest/download/AVALIADOR_VAZOES_NOVO_MODELO_WINDOWS_X64.zip).
2. Extraia todo o ZIP para uma pasta gravável e mantenha `_python` ao lado dos atalhos.
3. Abra `GERAR_RELATORIO_HTML.bat` e selecione o deck e o Parquet de cada versão.

O ZIP inclui CPython, Tcl/Tk e as bibliotecas, incluindo a variante compatível do Polars. O avaliador funciona sem instalar Python, alterar o PATH ou acessar a internet. Selecione separadamente os insumos do estudo.

## Análises

- **Análise** avalia uma versão do Novo Modelo.
- **Comparação** avalia duas versões do Novo Modelo, com deck e período histórico próprios. As duas versões devem cobrir as mesmas usinas e os mesmos meses do horizonte.
- A visão geral do SIN inclui Welch, Levene, KS, correlação espacial entre duas bacias por estágio e análise de sequências. O raio espectral anual aparece no ranking de médias quando os parâmetros do ajuste estão disponíveis.

Os relatórios ficam em `relatorios/` e abrem offline no navegador. [Guia de uso](documentacao/README.md)

## Outros atalhos

- `GERAR_PARQUET_NOVO_MODELO.bat` consolida as saídas de vazão.
- `EXPORTAR_PARQUET_EXCEL.bat` exporta registros selecionados para Excel.
- `EXPORTAR_HISTORICO_EXCEL.bat` exporta o histórico selecionado para Excel.

## Código-fonte

Os atalhos também aceitam uma instalação completa de Python x64 a partir de 3.10 com Tcl/Tk. Execute os comandos abaixo na raiz do repositório.

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s testes -v
python -m infraestrutura.empacotar_portatil --destino outputs/distribuicao --ref HEAD
```

Os testes do cálculo por bacia usam Node.js quando disponível. O ZIP é montado a partir dos arquivos versionados no commit.
