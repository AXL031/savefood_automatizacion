"""Evita publicar el token temporal en los logs de acceso de Uvicorn."""
import logging


class OcultarTokenProveedor(logging.Filter):
    def filter(self, record):
        if isinstance(record.args, tuple) and len(record.args) == 5:
            cliente, metodo, ruta, version, estado = record.args
            if isinstance(ruta, str) and ruta.startswith('/api/v1/proveedor/pedidos/'):
                record.args = (cliente, metodo, '/api/v1/proveedor/pedidos/[oculto]', version, estado)
        return True


logging.getLogger('uvicorn.access').addFilter(OcultarTokenProveedor())
