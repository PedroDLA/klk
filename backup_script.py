from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import os
from datetime import datetime
from pygit2 import Keypair, RemoteCallbacks, UserPass, Repository, Signature 



# Inicializar Nornir
nr = InitNornir(config_file= "config.yaml" )
GITHUB_REPO_PATH = "/root/Automatizacion/FINAL/klk"

# Crear el directorio
#backup_dir = "backups"
#os.makedirs(backup_dir, exist_ok=True)
# Crear el directorio dentro del repositorio local de GitHub
repo_path = "/root/Automatizacion/FINAL/klk"
backup_dir = os.path.join(repo_path, "backups")  # Ruta completa al directorio de backups
os.makedirs(backup_dir, exist_ok=True)

def backup_configurations(task):
    #print(nr.inventory.hosts)
    # Conectar y obtener la configuración
    task.run(task=netmiko_send_command, command_string="enable", enable=True)
    result = task.run(task=napalm_get, getters=["config"])
    config = result.result["config"]["running"]
    
    # Fecha y hora actual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Guardar la configuración
    filename = os.path.join(backup_dir, f"{timestamp}{task.host.name}_config.txt")
    with open(filename, "w") as f:
        f.write(config)
    print(f"Backup de {task.host.name} guardado en {filename}")

def git_commit_push(repo_path, commit_message="Backup automático"):
    """Realiza un commit y un push al repositorio de GitHub."""
    repo = Repository(repo_path) # Realizar un pull antes de cualquier operación
    
    try:
        remote = repo.remotes["origin"]
        remote.fetch()  # Traer los cambios remotos
        repo.merge(repo.lookup_reference("refs/remotes/origin/main").target)  # Fusionar los cambios
    except Exception as e:
        print(f"Error al sincronizar con el repositorio remoto: {e}")
        return
   
    index = repo.index
    index.add_all()  # Añadir todos los cambios
    index.write()
    
    # Realizar el commit
    author = Signature("Backup Bot", "backupbot@example.com")
    committer = Signature("Backup Bot", "backupbot@example.com")
    tree = index.write_tree()
    repo.create_commit(
        "origin/main",  # Rama donde se hará el commit
        author,
        committer,
        commit_message,
        tree,
        [repo.head.target],
    )
    #token = os.getenv("GITHUB_TOKEN")  # Asegúrate de exportar esta variable en tu terminal
   # if not token:
   #   raise ValueError("El token de GitHub no está configurado. Usa export GITHUB_TOKEN=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")
    #keypair = Keypair("git", "/ruta/a/clave_privada", "/ruta/a/clave_publica", "")
    #callbacks = RemoteCallbacks(credentials=keypair)
    #remote = repo.remotes["origin"]
    #callbacks = RemoteCallbacks(credentials=UserPass(token, ""))
    #remote.push(["refs/heads/main"], callbacks=callbacks)
    print("Backup subido a GitHub con éxito")

# Ejecutar el backup en todos los hosts
nr.run(task=backup_configurations)
git_commit_push(GITHUB_REPO_PATH)





