# Notebook Google Colab

<p align="center">ELT utilizando GCP e Databricks </p>

# Sobre

O projeto foi desenvolvido com GCP e Databricks, utilizando Pyspark para manipulação dos arquivos.
Nesse projeto, estamos realizando um ETL, obtendo informações sobre alimentos de todo o mundo. Eles fornecem uma API gratuita que permite acessar dados sobre produtos alimentícios, ingredientes, informações nutricionais, rótulos, certificações e muito mais.

Até então, não é ideial utilizar spark para a pequena quantidade de dados, o ideial é acima de GB (Giga Bytes), mas é um projeto, visa trazer aprendizados da vida real, com conteúdo técnico.

---

## Pré-requisitos

Saber sobre a linguagem Python, conhecimentos em Apache Spark/Pyspark, SQL, Databricks e GCP.

---

## Executar Projeto

Você pode realizar o clone, e executar o jupyter notebook, mas não vai funcionar como é o verdadeiro objetivo (Utilizar o GCP para execução juntamente com o Databricks).

Para executar o meu projeto, recomendo criar uma conta no google cloud platform, caso não tenha.

---
# Configurando GCP

Depois que criamos nossa conta, ele já cria um projeto automaticamente, para termos controle de qual projeto estamos mexendo, vamos renomear.

No canto superior direito, ao lado esquerdo da sua foto de perfil da conta do google, temos um menu, iremos clicar nele e ir até **Configuração do projeto**, conforme imagem abaixo. Eu coloquei o nome de **Databricks with GCP**, fique a vontade para escolher o seu.

imagem 1 - Acessando configurações

imagem 2 - Alterando nome do projeto e salvando

## Ativando Databricks

No canto superior esquerdo, temos um menu bar, acessando ele, vamos atrás do **Databricks**, o GCP te trás opção de fixar para aparecer logo em cima. Eu fixei para encontra-lo com maior facilidade.

imagem 3 - Databricks fixado

Depois que acessar o databricks, clique em Assinar e concorde com os termos e condições.

Faça login sempre com a conta que utiliza o GCP, depois que selecionar o plano que eles indicam pra você, volte novamente na interface do GCP do Databricks e clique nele, ele vai te redirecionar para um link para você criar o seu **workspace**.

Aqui nesse passo é bem simples. Basta colocar o nome do workspace que deseja, você vai copiar do GCP o ID do projeto e colar lá, e na região SEMPRE busque utilizar `us-central1` porque esse é uma das regiões gratuitas.

Feito isso, você vai finalizar e vai receber um **email**, lá vai ter o link que está apto a mexer no databricks.

Acessando o link, vamos criar um cluster, ele já aparece logo no inicio bem grande.

## Informações recomendas para aplicar na criação do cluster

- Sempre utilize a versão estavel recomendada pelo databricks.
- **Worker type**, costumo colocar `n1-standard-4` sendo `15GB Memoria e 4 Cores`
- **Min workers** eu deixo: `1`
- **Max workers** eu deixo: `8`

Depois disso é só sucesso. Eu escolho esse n1 standart porque ele abrange tanto memoria otimizada quanto computação otimizada. Mas dependendo do projeto na vida real, é legal entender a quantidade de dados que o cluster vai tratar, para escolher um meio termo ou configuração mais especifica.

## Criando um notebook

Feito tudo acima, agora conseguimos utilizar do nosso cluster.

No canto superior esquerdo vamos em **Data science e engineering**, clique no `+` para criar um notebook.

## Onde está meus notebooks?

No canto superior esquerdo vamos em **Data science e engineering**, clique em `Workspace` para ver todos os notebooks, pastas criadas dentro do databricks.

## Como criar um Job com Schedule?

No canto superior esquerdo vamos em **Data science e engineering**, clique em `Workflows` para ver todos os jobs criados, e para criar um novo, você vai no canto superior direito em `Create Job`.

## Gratuidade

Informação bem importante, o GCP é gratuito por 90 dias para novos usuários e o Databricks por 14 dias
Fique sempre atento a esse prazo, para que não tenha eventuais cobranças futuramente.

O próprio google alega que depois de 90 dias caso não tenha o upgrade, ele exclui todos os seus projetos, mas faça isso antes..."O seguro morreu de velho" - Como diz meus pais.

---

### Referências

- [Open Food Facts](https://world.openfoodfacts.org/data)

---

## Autor

- **Anna Karoliny (@annakaroliny.tech)** - _Mentora, Desenvolvedora e Engenheira de Dados_