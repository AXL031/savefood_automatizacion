"""Crea el primer administrador local después de aplicar las migraciones."""
from getpass import getpass

from pwdlib import PasswordHash
from sqlalchemy import select

from app.core.base_datos import SessionLocal
from app.modules.autenticacion.modelos import Usuario


def main():
    correo = input("Correo del administrador: ").strip().lower()
    contrasena = getpass("Contraseña nueva (mínimo 12 caracteres): ")
    if not correo or len(contrasena) < 12:
        raise SystemExit("Indica un correo y una contraseña de al menos 12 caracteres")
    with SessionLocal.begin() as sesion:
        if sesion.scalar(select(Usuario.id).where(Usuario.correo == correo)):
            print("El administrador ya existe")
            return
        sesion.add(Usuario(correo=correo, nombre="Administrador", rol="ADMINISTRADOR", activo=True,
                           hash_contrasena=PasswordHash.recommended().hash(contrasena)))
    print("Administrador creado")


if __name__ == "__main__":
    main()
