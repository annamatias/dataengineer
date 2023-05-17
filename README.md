# Data Engineer - Google Cloud Platform
<p align="center">Aprenda tudo sobre Engenharia de Dados, utilizando ferramentas mais atuais e muito mais.</p>

# Case: Indicador de Custo do Crédito

Esse projeto visa trazer informações do [Banco Central do Brasil](https://dadosabertos.bcb.gov.br/), e realizar estudos em cima disso.

- [Indicador de Custo do Crédito - ICC - Crédito direcionado](https://dadosabertos.bcb.gov.br/dataset/25357-indicador-de-custo-do-credito---icc---credito-direcionado)

  Conceito: Custo médio das operações de crédito que integram a carteira de empréstimos, financiamentos e arrendamento mercantil das instituições financeiras integrantes do Sistema Financeiro Nacional. Inclui todas as operações em aberto classificadas no ativo circulante, independente da data de contratação do crédito.

 **Fonte: Banco Central do Brasil – Departamento de Estatísticas**

---
## Motivação

<p> A maior motivação para esse projeto é poder deixar aqui tudo que eu sei e aprendi na área de dados para outras pessoas, isso vai ajudar quem está aprendendo, e também é um lugar colaborativo. Onde você também pode melhorar o que já tem.

Neste projeto estou utilizando o Google Colab, GCP para armazenar dados de Big Data e o DataBricks para visualizar e manipular via SQL.

---
## Pré-requisitos
Antes de começar a utilizar deste projeto, confira se atende os seguintes requisitos:
- Tenha uma conta na Google e no DataBricks
- Saiba programar em `Python`
- Noções básicas sobre `Apache Spark, GCP, Data Lake, DataBricks`

---
## Configurando Spark no Google Colab

### Instalar as dependências:
Aqui é necessário instalarmos o Java antes, porque o Spark utiliza do Java.

`!apt-get update -qq`

`!apt-get install openjdk-8-jdk-headless -qq > /dev/null`

`!wget -q https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop2.7.tgz`

`!tar xf spark-3.1.2-bin-hadoop2.7.tgz`

`!pip install -q findspark`

### Declarar variáveis de ambiente:
Para o nosso notebook funcionar da forma correta, temos que declarar o Java e Spark como variável de ambiente, assim ele não vai dar erro ao executar por não encontrar dependências.

`import os`

`os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"`

`os.environ["SPARK_HOME"] = "/content/spark-3.1.2-bin-hadoop2.7"`

### Para encontrar o Spark

`import findspark`

`findspark.init()`

---
## Data Source - Drive

Nesse projeto, estou utilizando do Google Drive, para colocar o arquivo CSV em uma pasta e realizar a leitura.

Você pode baixar o arquivo CSV do Banco Central que está sendo utilizado, [clicando aqui](https://api.bcb.gov.br/dados/serie/bcdata.sgs.25357/dados?formato=csv).
Eu acabei renomeando o arquivo para `indicador_custo.csv`, mas fica ao seu críterio, só fique atento, porque o nome de arquivo pode estar diferente e isso ser um erro no seu código.

Depois de ter criado uma pasta e colocado o arquivo.csv no seu drive, vamos importar ele para o nosso Google Colab.
Iremos em 🗂️`Arquivos`, no seu canto superior esquerdo, e iremos na pasta do Drive, realizaremos a conexão, e é importante depois disso ter em uma célula o código abaixo para funcionar.

`from google.colab import drive`

`drive.mount('/content/drive')`

---
## Criando uma Sessão Spark

`from pyspark.sql import SparkSession `

`spark = SparkSession.builder
  .master('local [*]') \
  .appName ("Iniciando com Spark") \
  .getorCreate ()`

Temos aqui um exemplo que podemos colocar o nome na nossa sessão, utilizando o appName()

O master com o local[*] serve para pegar todas as CPU’s disponíveis, posso deixar vazio que ele vai entender ou então colocar uma quantidade, ele vai funcionar também.

---
## Leitura CSV em Spark
O caminho relativo você pode copiar, clicando com o botão direito no próprio arquivo.

`path = '/content/drive/MyDrive/data_sources/banco_central/credito_direcionado/indicador_custo.csv'`

`df = spark.read.csv(path, sep=';', inferSchema=True)`

---
## Transformações em Spark

Abrindo o arquivo do notebook no colab, você vai conseguir conferir todas as transformações desse projeto.
Incluindo:

- Select's
- Rename de colunas
- Count
- Transformações de dataTypes
- Transformação de data, exemplo: yyyy-mm-dd
- Cálculos

---
### Referências

[build-a-data-lake-on-gcp](https://cloud.google.com/architecture/build-a-data-lake-on-gcp?hl=pt-br#cloud-storage-as-data-lake)

---
## Autor

- **Anna Karoliny (@annakaroliny.tech)** - _Mentora, Desenvolvedora e Engenheira de Dados_
