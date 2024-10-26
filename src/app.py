import os
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from datetime import datetime
import logging
import tarfile
import time
from croniter import croniter

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_env_variables():
    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "S3_ACCESS_KEY_ID",
        "S3_SECRET_ACCESS_KEY",
        "S3_BUCKET",
        "S3_PREFIX",
        "S3_REGION"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        raise EnvironmentError("Verifique as variáveis de ambiente.")

def create_backup():
    # Validação das variáveis de ambiente
    validate_env_variables()
    
    # Variáveis de ambiente
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    databases = os.getenv("POSTGRES_DATABASE")  # A nova variável opcional

    # Data e hora para nome do arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if databases:
        db_list = databases.split(',')
        for db in db_list:
            db = db.strip()  # Remove espaços em branco
            dump_file = f"backup_{db}_{timestamp}.sql"
            perform_backup(host, port, user, password, dump_file, db)
    else:
        dump_file = f"backup_all_{timestamp}.sql"
        perform_backup(host, port, user, password, dump_file)

def perform_backup(host, port, user, password, dump_file, database=None):
    try:
        if database:
            # Use pg_dump para bancos de dados específicos
            command = f"pg_dump -h {host} -p {port} -U {user} {database} > {dump_file}"
        else:
            # Use pg_dumpall para todos os bancos de dados
            command = f"pg_dumpall -h {host} -p {port} -U {user} > {dump_file}"

        env = os.environ.copy()  # Copia as variáveis de ambiente
        env['PGPASSWORD'] = password  # Define a senha no ambiente
        subprocess.run(command, shell=True, check=True, env=env)
        logging.info(f"Backup do banco de dados '{database if database else 'todos'}' criado: {dump_file}")

        compress_backup(dump_file)
        upload_to_s3(f"{dump_file}.tar.gz")

    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao realizar o backup: {e}")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")
        
def compress_backup(dump_file):
    tar_file = f"{dump_file}.tar.gz"
    
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(dump_file)
        logging.info(f"Backup comprimido em: {tar_file}")

    # Remove o arquivo SQL original após a compressão
    os.remove(dump_file)

def upload_to_s3(file_name):
    s3_access_key = os.getenv("S3_ACCESS_KEY_ID")
    s3_secret_key = os.getenv("S3_SECRET_ACCESS_KEY")
    s3_bucket = os.getenv("S3_BUCKET")
    s3_prefix = os.getenv("S3_PREFIX")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        region_name=os.getenv("S3_REGION"),
    )
    
    s3_file_path = f"{s3_prefix}/{file_name}"

    try:
        s3_client.upload_file(file_name, s3_bucket, s3_file_path)
        logging.info(f"Arquivo {file_name} enviado para S3: {s3_file_path}")
    except FileNotFoundError:
        logging.error("O arquivo de backup não foi encontrado.")
    except NoCredentialsError:
        logging.error("Credenciais do S3 não encontradas.")
    except ClientError as e:
        logging.error(f"Erro ao enviar para S3: {e}")

def run_scheduler():
    schedule = os.getenv("SCHEDULE")
    
    if schedule:
        logging.info(f"Agendando backups com a programação: {schedule}")
        cron = croniter(schedule, datetime.now())

        while True:
            next_run = cron.get_next(datetime)
            sleep_time = (next_run - datetime.now()).total_seconds()
            logging.info(f"Próximo backup agendado para: {next_run}")
            time.sleep(max(0, sleep_time))  # Aguarde até o próximo agendamento
            create_backup()
    else:
        logging.info("Nenhum agendamento encontrado. Executando backup imediatamente.")
        create_backup()

if __name__ == "__main__":
    logging.info("Iniciando o serviço de backup.")
    run_scheduler()