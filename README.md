# Waste Data Analyzer

Pipeline Python para normalizar registros de pesagem, calcular indicadores de coleta e gerar relatórios operacionais auditáveis.

O repositório é uma implementação pública e sanitizada inspirada em rotinas de análise de limpeza urbana. Os exemplos são fictícios; placas, tickets, documentos e dados operacionais reais não são publicados.

## O que demonstra

- leitura de CSV com cabeçalhos em português ou inglês;
- tratamento de números nos formatos `12.450,50` e `12450.50`;
- validação de pesos ausentes, inválidos ou negativos;
- totais, médias e agrupamentos por veículo e data;
- extração de campos de tickets PDF baseados em texto;
- relatório HTML responsivo e pronto para impressão;
- JSON intermediário para integração com dashboards;
- testes automatizados no GitHub Actions.

## Executar

```bash
python -m pip install -r requirements.txt
python AnalyticalCore.py examples/weighing_records.csv --output summary.json
python -m unittest discover -s tests -v
```

Para gerar o relatório completo:

```python
from VisualReportWorkflow import generate_html_report

generate_html_report(
    "examples/weighing_records.csv",
    "summary.json",
    "report.html",
)
```

## Arquitetura

```text
PDFExtractionEngine.py  # extração e normalização de tickets
AnalyticalCore.py       # validação e indicadores
VisualReportWorkflow.py # relatório HTML autocontido
examples/               # dados completamente fictícios
tests/                  # testes do pipeline
```

## Privacidade

O fluxo público trabalha apenas com ticket, placa fictícia, peso e data. Nomes de trabalhadores, coordenadas, credenciais e documentos reais ficam fora do repositório.

Desenvolvido por [Marx Bruno](https://github.com/marxb50).
