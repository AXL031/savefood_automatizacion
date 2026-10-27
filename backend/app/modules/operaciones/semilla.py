"""Carga de prueba explícita e idempotente; jamás sobrescribe una instalación ajena."""
import hashlib
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from pwdlib import PasswordHash
from sqlalchemy import select, func
from app.core.base_datos import SessionLocal
from app.modules.autenticacion.modelos import Usuario
from app.modules.negocios.modelos import Negocio
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.ingredientes.modelos import Ingrediente
from app.modules.inventario.modelos import LoteIngrediente, LoteProducto
from app.modules.inventario.operacion import movimiento
from app.modules.recetas.servicio import crear_version, LineaNueva
from app.modules.ventas.servicio import registrar_ventas_diarias
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.tienda.modelos import ClienteTienda
from app.modules.promociones.servicio import guardar_regla
from app.modules.promociones.esquemas import ConfigurarRegla
from .modelos import CuentaClienteLocal, FichaTienda, ConfiguracionOperacion
from app.principal import app  # noqa: F401; composición completa de metadatos para este CLI


def cargar():
    if os.getenv('HABILITAR_DATOS_PRUEBA') != '1':
        raise RuntimeError('La carga requiere HABILITAR_DATOS_PRUEBA=1 y una base aislada.')
    nombres=['DEMO_ADMIN_PASSWORD','DEMO_OPERADOR_PASSWORD','DEMO_CLIENTE_PASSWORD']
    if any(len(os.getenv(n,''))<16 for n in nombres):raise RuntimeError('Genera primero las credenciales privadas de prueba (mínimo 16 caracteres).')
    with SessionLocal.begin() as s:
        from app.modules.ventas.modelos import ImportacionVenta
        if s.scalar(select(ImportacionVenta.id).where(ImportacionVenta.clave_importacion=='demo-operacion-2026')):
            print('Datos de prueba ya existentes; no se cambian contraseñas, stock ni historia.');return
        if s.scalar(select(func.count()).select_from(Usuario)) or s.scalar(select(func.count()).select_from(Producto)):
            raise RuntimeError('La base ya contiene datos. Usa el proyecto Docker aislado foodsave_pruebas; no se sobrescribe nada.')
        negocio=s.get(Negocio,1)
        if not negocio:s.add(Negocio(id=1,nombre='Pastelería Maria Juanita · Pruebas',zona_horaria='America/Lima',moneda='PEN'))
        else:negocio.nombre='Pastelería Maria Juanita · Pruebas'
        ph=PasswordHash.recommended()
        for correo,nombre,rol,variable in [('admin.foodsave@example.com','Administrador de prueba','ADMINISTRADOR',nombres[0]),('operador.foodsave@example.com','Trabajador de prueba','OPERADOR',nombres[1])]:
            s.add(Usuario(correo=correo,nombre=nombre,rol=rol,activo=True,hash_contrasena=ph.hash(os.environ[variable])))
        c=ClienteTienda(google_sub='local:foodsave-demo',correo='cliente.foodsave@example.com',nombre='Cliente de prueba',activo=True)
        s.add(c);s.flush()
        s.add(CuentaClienteLocal(cliente_id=c.id,correo=c.correo,hash_contrasena=ph.hash(os.environ[nombres[2]])))
        harina=Ingrediente(codigo='DEMO-HARINA',nombre='Harina de prueba',unidad_base='g',activo=True)
        s.add(harina);s.flush()
        lote=LoteIngrediente(ingrediente_id=harina.id,codigo_lote='DEMO-HARINA-1',lote_informado=True,saldo_disponible=Decimal(0),fecha_ingreso=date(2026,9,1),fecha_caducidad=date(2027,1,1))
        s.add(lote);s.flush();movimiento(s,lote,Decimal('5000'),'APERTURA','demo-apertura-harina',date(2026,9,28),None,'Apertura sintética de prueba')
        productos=[]
        for i,(codigo,nombre,gramos,precio,imagen) in enumerate([('DEMO-PAN','Pan francés',50,'0.50','baguette'),('DEMO-CROISSANT','Croissant',120,'3.50','croissant'),('DEMO-EMPANADA','Empanada',80,'4.00','empanada')]):
            p=Producto(codigo=codigo,nombre=nombre,demostrar=True,activo=True);s.add(p);s.flush()
            s.add(SkuProducto(producto_id=p.id,origen='bakery',sku_externo=codigo,activo=True))
            crear_version(s,p.id,[LineaNueva(harina.id,Decimal(gramos))],'Receta sintética de prueba',None)
            l=LoteProducto(producto_id=p.id,codigo_lote='DEMO-'+codigo,lote_informado=True,fecha_caducidad=date(2026,9,29),fecha_limite_venta=date(2026,9,29),saldo_disponible=0)
            s.add(l);s.flush();movimiento(s,l,12+i,'APERTURA','demo-apertura-'+codigo,date(2026,9,28),None,'Existencias sintéticas para probar ventas/promociones')
            s.add(FichaTienda(producto_id=p.id,precio=Decimal(precio),version=1,datos={'publicado':True,'categoria':'panes','descripcion':'Producto del conjunto de prueba','presentacion':'Unidad','imagen':f'/tienda/productos/{imagen}.jpg'}))
            productos.append(p)
        diarios={}
        for n in range((date(2026,9,30)-date(2026,1,1)).days+1):
            d=date(2026,1,1)+timedelta(days=n)
            for i,p in enumerate(productos):diarios[(p.id,d)]=max(0,25+i*5+(n%7)*2+(n%11)-5)
        registrar_ventas_diarias(s,diarios,'demo-operacion-2026',hashlib.sha256(b'demo-operacion-2026').hexdigest(),len(diarios),'Ventas sintéticas deterministas; no son resultados comerciales')
        admin_id=s.scalar(select(Usuario.id).where(Usuario.correo=='admin.foodsave@example.com'))
        guardar_regla(s,ConfigurarRegla(habilitada=True,stock_umbral=5),admin_id)
        config=s.get(ConfiguracionOperacion,1)
        if not config:config=ConfiguracionOperacion(id=1);s.add(config)
        config.datos={'reloj':'ESCENARIO','fecha_escenario':'2026-09-29','hora_escenario':'17:15','habilitada':True,'producto_ids':[p.id for p in productos]}
        config.proxima_revision=None
        from app.modules.proveedores.servicio import ServicioProveedores
        from app.modules.proveedores.esquemas import ProveedorCrear,OfertaCrear
        proveedores=ServicioProveedores(s)
        proveedor=proveedores.crear_proveedor(ProveedorCrear(codigo='DEMO-PROV',nombre='Proveedor de prueba sin chat'))
        proveedores.crear_oferta(proveedor.id,OfertaCrear(ingrediente_id=harina.id,descripcion='Bolsa 1 kg',unidad_compra='bolsa',factor_conversion=Decimal('1000'),preferida=True))
        from app.modules.inicializacion.modelos import ConfiguracionInicial
        huella=hashlib.sha256(b'demo-operacion-inicializacion-2026').hexdigest()
        tarea=crear_o_recuperar_ejecucion(s,'PREPARAR_MODELO','demo-operacion-modelo-2026',{'version_modelo':'demo-operacion-2026','huella_inicializacion':huella})
        inicial=s.get(ConfiguracionInicial,1)
        if not inicial:inicial=ConfiguracionInicial(id=1);s.add(inicial)
        inicial.estado='DATOS_CARGADOS';inicial.huella_solicitud=huella;inicial.huella_ventas=huella;inicial.huella_catalogo=huella
        inicial.fecha_objetivo_demo=date(2026,9,29);inicial.fecha_referencia_stock=date(2026,9,28)
        inicial.preparacion_ejecucion_id=tarea.id;inicial.preparacion_numero=1
    print('Cuentas, catálogo, recetas, lotes y ventas de prueba creados. Preparación CatBoost reservada para el worker. No se envió Telegram.')


if __name__=='__main__':cargar()
