"""Supervisor mínimo de la variante remota: una instancia, un Beat y disco local compartido."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def main():
    url=os.environ['DATABASE_URL']
    if url.startswith('postgres://'):url='postgresql+psycopg://'+url[len('postgres://'):]
    elif url.startswith('postgresql://'):url='postgresql+psycopg://'+url[len('postgresql://'):]
    os.environ['DATABASE_URL']=url
    for clave in ['MODEL_ARTIFACT_DIR','TELEGRAM_CONFIG_DIR']:
        p=Path(os.environ[clave]);p.mkdir(parents=True,exist_ok=True)
        if hasattr(os,'geteuid') and os.geteuid()==0:os.chown(p,10001,10001)
    if hasattr(os,'geteuid') and os.geteuid()==0:
        os.setgroups([]);os.setgid(10001);os.setuid(10001)
    subprocess.run([sys.executable,'-m','alembic','upgrade','head'],check=True,cwd='/code')
    if os.getenv('HABILITAR_DATOS_PRUEBA')=='1':
        subprocess.run([sys.executable,'-m','app.modules.operaciones.semilla'],check=True,cwd='/code')
    comandos=[([sys.executable,'-m','uvicorn','app.principal:app','--host','127.0.0.1','--port','8000','--no-access-log'],'/code'),
        ([sys.executable,'-m','celery','-A','app.workers.celery_app:celery_app','worker','--loglevel=warning','--concurrency=1'],'/code'),
        ([sys.executable,'-m','celery','-A','app.workers.celery_app:celery_app','beat','--loglevel=warning','--schedule=/tmp/foodsave-beat'],'/code'),
        (['node','node_modules/next/dist/bin/next','start','-H','0.0.0.0','-p',os.getenv('PORT','10000')],'/app')]
    procesos=[]
    def detener(*_):
        for p in procesos:
            if p.poll() is None:p.terminate()
        for p in procesos:
            try:p.wait(timeout=20)
            except subprocess.TimeoutExpired:p.kill()
    signal.signal(signal.SIGTERM,lambda *_:sys.exit(0))
    signal.signal(signal.SIGINT,lambda *_:sys.exit(0))
    try:
        procesos=[subprocess.Popen(cmd,cwd=cwd) for cmd,cwd in comandos]
        while all(p.poll() is None for p in procesos):time.sleep(1)
        raise RuntimeError('Un proceso terminó; se reinicia la instancia completa para conservar un único Beat.')
    finally:detener()


if __name__=='__main__':main()
