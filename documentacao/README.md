# Guia do Avaliador Somente Novo Modelo

## Gerar o relatório

Abra `GERAR_RELATORIO_HTML.bat`. Em **Análise**, informe o deck e o Parquet da versão A. Em **Comparação**, informe também o deck e o Parquet da versão B e dê nomes distintos às versões.

O deck contém `system/hydros.json`, `stages.json` e `scenarios/inflow_history.parquet`. Confira os períodos históricos inclusivos em `AAAA-MM`. Cada versão é avaliada contra o recorte do seu próprio histórico.

## Consultar o resultado

Na visão geral do SIN, a aba **Correlação espacial** permite escolher Bacia A e Bacia B. O programa soma as vazões incrementais das UHEs de cada bacia e calcula Pearson por estágio. O sintético pareia os mesmos cenários. O histórico pareia os mesmos anos do mês civil correspondente. Os memoriais mostram a composição das bacias e os totais pareados.

O relatório também inclui testes de médias, variâncias e distribuições, P50 e P90 de sequências e os detalhes por usina. O raio espectral anual aparece no ranking de médias quando os parâmetros necessários estão no Parquet.

Para levar o resultado a outro computador, copie o HTML gerado. Ele incorpora as tabelas, os dados e os recursos de navegação.

## Executar pela linha de comando no Windows

```powershell
.\GERAR_RELATORIO_HTML.bat --deck "C:\estudo\deck_a" --novo "C:\estudo\a.parquet" --sem-abrir
```

Para comparar duas versões, acrescente `--deck-referencia` e `--novo-referencia`. Os nomes podem ser informados com `--rotulo-novo` e `--rotulo-referencia`. O recorte de cada fonte usa `--novo-inicio` e `--novo-fim` ou `--novo-referencia-inicio` e `--novo-referencia-fim`. Use `--help` para listar os argumentos.
