import os
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import logging
import time
from croniter import croniter

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_backup():
    # Variáveis de ambiente
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    backup_all = os.getenv("POSTGRES_BACKUP_ALL").lower() == 'true'
    
    # Data e hora para nome do arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dump_file = f"backup_{timestamp}.sql"
    
    try:
        if backup_all:
            # Backup de todos os bancos de dados
            command = f"pg_dumpall -h {host} -p {port} -U {user} > {dump_file}"
            env = os.environ.copy()  # Copia as variáveis de ambiente
            env['PGPASSWORD'] = password  # Define a senha no ambiente
            subprocess.run(command, shell=True, check=True, env=env)
            logging.info(f"Backup de todos os bancos de dados criado: {dump_file}")
        else:
            logging.info("Backup de todos os bancos de dados não está habilitado.")
            return

        upload_to_s3(dump_file)

    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao realizar o backup: {e}")

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
    