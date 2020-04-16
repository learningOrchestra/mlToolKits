# database
O banco de dados tem 2 serviços, o serviço de banco de dados (mongodb), que usa uma imagem do mongo no DockerHub para hospedar o banco de dados, e o serviço da API do banco de dados (mongo_api), em que é criado um nível de abstração atrávés de uma REST API para uso do serviço de banco de dados.


# mongo_api
Os documentos são manipulados em formato json, sendo que a chave primária de cada documento é o campo filename contido no arquivo json enviado.
## POST /add
Insere um json no banco de dados através do path /add pelo método POST, o json deve estar contido no body da requisição http.
## GET /files
Retorna todos os arquivos inseridos no banco de dados.
## GET /file/<filename>
Uma requisição com o filename do arquivo, retornando o arquivo caso exista um com dado valor.
## DELETE /file/<filename>
Requisição do tipo DELETE, informando o filename do arquivo, excluindo o arquivo do banco de dados, caso exista um com dado valor.
