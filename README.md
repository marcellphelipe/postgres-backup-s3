# Aplicativo de Backup PostgreSQL

Este aplicativo é projetado para realizar backups de bancos de dados PostgreSQL, comprimi-los e enviá-los para o Amazon S3. Ele pode fazer o backup de todos os bancos de dados ou de bancos específicos conforme a configuração.

## Pré-requisitos

- **Docker**: Certifique-se de ter o Docker instalado em seu sistema.
- **Acesso a um servidor PostgreSQL**: Você deve ter acesso ao servidor PostgreSQL onde os bancos de dados estão hospedados.
- **Credenciais válidas do Amazon S3**: Você precisará de uma conta na AWS e de credenciais válidas para enviar arquivos para o S3.

## Variáveis de Ambiente

### 1. `POSTGRES_HOST`
- **Descrição**: O endereço do host do servidor PostgreSQL.
- **Exemplo**: `seu_host_postgres`

### 2. `POSTGRES_PORT`
- **Descrição**: A porta do servidor PostgreSQL. O padrão é 5432.
- **Exemplo**: `5432`

### 3. `POSTGRES_USER`
- **Descrição**: O nome do usuário que tem permissões para acessar o banco de dados.
- **Exemplo**: `seu_usuario_postgres`

### 4. `POSTGRES_PASSWORD`
- **Descrição**: A senha do usuário do banco de dados.
- **Exemplo**: `sua_senha_secreta`

### 5. `POSTGRES_DATABASE` (Opcional)
- **Descrição**: Uma lista de nomes de bancos de dados que devem ser incluídos no backup, separados por vírgula. Se não for especificado, o aplicativo fará o backup de todos os bancos de dados.
- **Exemplo**: `db1,db2`

### 6. `S3_ACCESS_KEY_ID`
- **Descrição**: A chave de acesso da sua conta AWS para autenticação no S3.
- **Exemplo**: `sua_chave_de_acesso`

### 7. `S3_SECRET_ACCESS_KEY`
- **Descrição**: A chave secreta da sua conta AWS, usada em conjunto com a chave de acesso para autenticação no S3.
- **Exemplo**: `sua_chave_secreta`

### 8. `S3_BUCKET`
- **Descrição**: O nome do bucket S3 onde os arquivos de backup serão armazenados.
- **Exemplo**: `seu_bucket_backup`

### 9. `S3_PREFIX`
- **Descrição**: O prefixo ou caminho no bucket S3 onde os backups serão armazenados.
- **Exemplo**: `seu/prefixo/para/backups`

### 10. `S3_REGION`
- **Descrição**: A região onde seu bucket S3 está localizado.
- **Exemplo**: `sua_regiao_s3`

### 11. `SCHEDULE` (Opcional)
- **Descrição**: Um cronograma para executar o backup automaticamente. No formato cron padrão. Se não for especificado, o backup será executado imediatamente ao iniciar o aplicativo.
- **Exemplo**: `1 0 */3 * *` (executa a cada 3 dias às 00:01)

## Passo a Passo

### 1. Baixar o Código

Clone o repositório ou baixe os arquivos necessários para o seu ambiente local.

### 2. Criar a Imagem Docker

Navegue até o diretório onde o `Dockerfile` está localizado e execute:

```bash
docker build -t postgres_backup .
