# Financial Data Pipeline

> Plataforma analítica para processamento e modelagem de dados financeiros utilizando práticas modernas de Engenharia de Dados.

## Sobre o projeto

Este projeto nasceu com um objetivo simples: transformar dados financeiros brutos em informações confiáveis para análise.

Ao longo da evolução do projeto, ele deixou de ser apenas um conjunto de scripts em Python e passou a incorporar conceitos utilizados em ambientes corporativos, como arquitetura Medallion, modelagem dimensional e transformação de dados com dbt.

O foco não é apenas produzir tabelas, mas demonstrar como estruturar um pipeline analítico utilizando boas práticas de engenharia, versionamento e organização de dados.

---

## Arquitetura

O pipeline segue a arquitetura **Medallion**, dividindo o processamento em três camadas.

```
Origem dos Dados
        │
        ▼
   Bronze Layer
(Dados brutos)
        │
        ▼
   Silver Layer
(Dados tratados,
padronizados e enriquecidos)
        │
        ▼
    Gold Layer
(Modelagem analítica
e métricas de negócio)
```

Cada camada possui responsabilidades bem definidas, reduzindo o acoplamento entre ingestão, tratamento e consumo dos dados.

---

## Tecnologias utilizadas

* Python
* DuckDB
* dbt
* SQL
* Git / GitHub
* Arquitetura Medallion
* Modelagem Dimensional
* Ambiente virtual (`venv`)

---

## Estrutura do projeto

```
financial-data-pipeline/

├── data_lake/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── dbt/
│   ├── models/
│   ├── macros/
│   ├── tests/
│   └── seeds/
│
├── src/
│
├── notebooks/
│
├── docs/
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

## Fluxo do pipeline

O processamento ocorre em etapas independentes.

### 1. Ingestão

Os dados são coletados e armazenados na camada Bronze preservando sua estrutura original.

### 2. Tratamento

Na camada Silver são realizadas padronizações, validações, limpeza e enriquecimento dos dados.

### 3. Modelagem

Com o dbt, os dados são organizados em modelos analíticos reutilizáveis seguindo boas práticas de transformação.

### 4. Consumo

A camada Gold disponibiliza datasets preparados para dashboards, análises e indicadores.

---

## Boas práticas adotadas

* Arquitetura em camadas (Medallion)
* Separação entre ingestão e transformação
* Versionamento com Git
* Organização modular do código
* Transformações declarativas utilizando dbt
* Modelagem analítica orientada ao consumo
* Controle de dependências
* Dados locais protegidos pelo `.gitignore`
* Estrutura preparada para evolução futura

---

## Próximas evoluções

O projeto foi concebido para evoluir continuamente. Entre os próximos passos estão:

* Orquestração do pipeline
* Testes automatizados de qualidade dos dados
* Integração com ambiente em nuvem
* Processamento distribuído com Spark
* Camada de monitoramento
* CI/CD para validação automática das transformações

---

## Objetivo

Mais do que reproduzir tutoriais, este projeto busca demonstrar a evolução de um pipeline de dados utilizando ferramentas amplamente empregadas em Engenharia de Dados.

Cada nova tecnologia incorporada representa uma etapa dessa evolução, aproximando a solução de um ambiente encontrado em projetos reais.

---

## Autor

**Rodrigo Monteiro**

MBA em Engenharia de Software

Projeto desenvolvido como parte da evolução prática em Engenharia de Dados, explorando arquitetura de dados, modelagem analítica, processamento de dados e boas práticas de desenvolvimento.
