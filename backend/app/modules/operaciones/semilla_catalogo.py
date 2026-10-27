"""Escenario sintético de pastelería, aditivo y versionado; sin commit ni red."""
import hashlib
import os
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select
from app.modules.ingredientes.modelos import Ingrediente
from app.modules.ingredientes.servicio import crear_ingrediente
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.inventario.modelos import LoteIngrediente, LoteProducto
from app.modules.inventario.operacion import movimiento
from app.modules.recetas.servicio import crear_version, LineaNueva, obtener_receta_activa
from app.modules.ventas.modelos import ImportacionVenta
from app.modules.ventas.servicio import registrar_ventas_diarias
from .modelos import ConfiguracionOperacion, FichaTienda
from .servicio import aviso, nuevo

VERSION = 'demo-pasteleria-v2-2026'
FECHA = date(2026, 9, 29)
# código, nombre, unidad, saldo inicial, vida desde el escenario, proveedor
INSUMOS = [
    ('HARINA','Harina panadera','g','18000',90,'MOLINO'),
    ('AZUCAR','Azúcar blanca','g','6000',120,'MOLINO'),
    ('SAL','Sal fina','g','1500',180,'MOLINO'),
    ('LEVADURA','Levadura seca','g','350',30,'MOLINO'),
    ('MANTEQUILLA','Mantequilla sin sal','g','240',7,'LACTEOS'),
    ('LECHE','Leche entera','ml','5000',5,'LACTEOS'),
    ('HUEVO','Huevo de gallina','unidad','48',10,'LACTEOS'),
    ('CARNE','Carne molida','g','1200',2,'FRESCOS'),
    ('CEBOLLA','Cebolla roja','g','2000',6,'FRESCOS'),
    ('LIMON','Jugo de limón','ml','600',3,'FRESCOS'),
    ('QUESO','Queso crema','g','300',4,'LACTEOS'),
    ('FRESA','Fresas frescas','g','0',1,'FRESCOS'),
    ('CHOCOLATE','Chocolate de cobertura','g','1800',60,'MOLINO'),
    ('CANELA','Canela molida','g','180',90,'MOLINO'),
    ('NARANJA','Jugo de naranja','ml','1800',3,'FRESCOS'),
    ('CREMA','Crema de leche','ml','2500',5,'LACTEOS'),
]

# Una ficha describe una unidad vendible; recetas son cantidades sintéticas, no fichas técnicas comerciales.
PRODUCTOS = [
    dict(codigo='PAN',nombre='Pan francés',categoria='panes',precio='0.50',imagen='baguette',presentacion='50 g · Unidad',base=95,
         descripcion='Corteza dorada y miga ligera, horneado en tandas para el desayuno.',
         receta={'HARINA':'50','SAL':'1','LEVADURA':'0.8'},lotes=[]),
    dict(codigo='CROISSANT',nombre='Croissant',categoria='panes',precio='3.50',imagen='croissant',presentacion='90 g · Unidad',base=38,
         descripcion='Hojaldre laminado con mantequilla, crujiente por fuera y suave al centro.',
         receta={'HARINA':'60','MANTEQUILLA':'24','AZUCAR':'8','LECHE':'20','LEVADURA':'1'},lotes=[]),
    dict(codigo='EMPANADA',nombre='Empanada',categoria='bocados',precio='4.00',imagen='empanada',presentacion='180 g · Unidad',base=42,
         descripcion='Masa artesanal rellena de carne y cebolla, lista para una pausa salada.',
         receta={'HARINA':'70','MANTEQUILLA':'15','CARNE':'65','CEBOLLA':'25','SAL':'1'},lotes=[]),
    dict(codigo='CIABATTA',nombre='Ciabatta artesanal',categoria='panes',precio='2.80',imagen='ciabatta',presentacion='120 g · Unidad',base=65,
         descripcion='Fermentación lenta, corteza crocante y miga aireada para sánguches.',
         receta={'HARINA':'90','LEVADURA':'1','SAL':'2'},lotes=[(48,0)]),
    dict(codigo='BRIOCHE',nombre='Brioche de mantequilla',categoria='panes',precio='12.00',imagen='brioche',presentacion='400 g · Molde',base=14,
         descripcion='Pan suave y ligeramente dulce con leche y mantequilla, ideal para compartir.',
         receta={'HARINA':'220','MANTEQUILLA':'55','LECHE':'70','HUEVO':'1','AZUCAR':'35','LEVADURA':'3'},lotes=[(2,1)]),
    dict(codigo='ROLL-CANELA',nombre='Rollo de canela glaseado',categoria='postres-personales',precio='7.50',imagen='rollo-canela',presentacion='130 g · Unidad',base=32,
         descripcion='Espiral de masa esponjosa, canela y glaseado cremoso de queso.',
         receta={'HARINA':'70','MANTEQUILLA':'18','AZUCAR':'24','LECHE':'25','CANELA':'2','QUESO':'12','LEVADURA':'1'},lotes=[(30,0)]),
    dict(codigo='PIE-LIMON',nombre='Pie de limón individual',categoria='postres-personales',precio='9.50',imagen='pie-limon',presentacion='120 g · Porción',base=26,
         descripcion='Base de mantequilla, crema cítrica y merengue ligero con un toque tostado.',
         receta={'HARINA':'35','MANTEQUILLA':'18','AZUCAR':'30','LIMON':'25','LECHE':'30'},lotes=[(3,0)]),
    dict(codigo='SELVA-NEGRA',nombre='Torta Selva Negra',categoria='tortas',precio='58.00',imagen='selva-negra',presentacion='18 cm · 8 porciones',base=8,
         descripcion='Bizcocho de cacao con capas de crema; una torta de celebración para la familia.',
         receta={'HARINA':'250','AZUCAR':'180','CHOCOLATE':'150','CREMA':'300','HUEVO':'4','MANTEQUILLA':'80'},lotes=[(4,2)]),
    dict(codigo='KEKE-NARANJA',nombre='Keke de naranja glaseado',categoria='kekes',precio='22.00',imagen='keke-naranja',presentacion='550 g · Molde',base=17,
         descripcion='Keke húmedo con jugo de naranja y glaseado cítrico, horneado en molde.',
         receta={'HARINA':'200','AZUCAR':'120','NARANJA':'110','HUEVO':'2','MANTEQUILLA':'65'},lotes=[(18,0),(8,2)]),
    dict(codigo='CHEESECAKE',nombre='Cheesecake horneado',categoria='postres-enteros',precio='64.00',imagen='cheesecake',presentacion='1.2 kg · 10 porciones',base=6,
         descripcion='Relleno cremoso de queso sobre una base crocante de mantequilla.',
         receta={'QUESO':'600','CREMA':'200','AZUCAR':'150','HUEVO':'3','HARINA':'100','MANTEQUILLA':'70'},lotes=[(3,0),(6,1)]),
    dict(codigo='TARTA-FRESA',nombre='Tartaleta de fresas',categoria='postres-enteros',precio='45.00',imagen='tartaleta-fresas',presentacion='22 cm · 8 porciones',base=7,
         descripcion='Masa sablé, crema suave y fresas frescas. Hoy requiere una nueva tanda.',
         receta={'HARINA':'180','MANTEQUILLA':'90','AZUCAR':'80','CREMA':'180','FRESA':'350'},lotes=[(0,0)]),
    dict(codigo='QUICHE',nombre='Quiche de queso',categoria='bocados',precio='11.50',imagen='quiche',presentacion='210 g · Porción',base=19,
         descripcion='Base quebrada con relleno de huevo, queso y crema. El lote anterior ya no está a la venta.',
         receta={'HARINA':'60','MANTEQUILLA':'25','HUEVO':'1','QUESO':'45','CREMA':'35','SAL':'1'},lotes=[(8,-1)]),
]


def unidades_sinteticas(codigo, fecha, base):
    """Patrones reproducibles: semana, tendencia, quincena y campañas ficticias."""
    if codigo=='TARTA-FRESA' and fecha==date(2026,2,24):return None  # ausencia deliberada, no cero
    if codigo=='QUICHE' and fecha.weekday()==6:return 0  # cero explícito
    semana=([1.05,1.0,1.02,1.06,1.18,1.32,1.22] if codigo in {'PAN','CIABATTA','CROISSANT'}
            else [.85,.82,.9,1.0,1.28,1.65,1.48])
    tendencia=1+((fecha-date(2026,1,1)).days/272)*.18
    campana=1.3 if (fecha.month==7 and fecha.day>=24) or fecha.day in {14,15,28,30} else 1
    ruido=int.from_bytes(hashlib.sha256(f'{codigo}:{fecha}'.encode()).digest()[:2],'big')%9-4
    return max(0,round(base*semana[fecha.weekday()]*tendencia*campana+ruido))


def enriquecer(s, *, preparar_modelo):
    from app.modules.autenticacion.modelos import Usuario
    from app.modules.inicializacion.modelos import ConfiguracionInicial
    from app.modules.negocios.modelos import Negocio
    from app.modules.proveedores.servicio import ServicioProveedores
    from app.modules.proveedores.modelos import Proveedor
    from app.modules.proveedores.esquemas import ProveedorCrear, OfertaCrear
    from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
    if os.getenv('HABILITAR_DATOS_PRUEBA')!='1':raise RuntimeError('La ampliación requiere una base de demo explícita.')
    inicial=s.scalar(select(ConfiguracionInicial).where(ConfiguracionInicial.id==1).with_for_update())
    if s.scalar(select(ImportacionVenta.id).where(ImportacionVenta.clave_importacion==VERSION)):return False
    if not s.scalar(select(ImportacionVenta.id).where(ImportacionVenta.clave_importacion=='demo-operacion-2026')):
        raise RuntimeError('No se amplía una base ajena a la demo operativa.')
    if inicial and inicial.estado=='ENTRENANDO':raise RuntimeError('Espera a que termine el entrenamiento antes de ampliar la demo.')
    if any(not p.codigo.startswith('DEMO-') for p in s.scalars(select(Producto))):
        raise RuntimeError('Hay productos ajenos a la demo; no se modificó nada.')
    admin=s.scalar(select(Usuario).where(Usuario.correo=='admin.foodsave@example.com'))
    proveedores=ServicioProveedores(s)
    abastecedores={}
    for codigo,nombre in [('MOLINO','Molinos Andinos · DEMO'),('LACTEOS','Lácteos Valle Verde · DEMO'),('FRESCOS','Mercado La Huerta · DEMO')]:
        p=s.scalar(select(Proveedor).where(Proveedor.codigo==('DEMO-PROV' if codigo=='MOLINO' else 'DEMO-'+codigo)))
        if not p:p=proveedores.crear_proveedor(ProveedorCrear(codigo='DEMO-'+codigo,nombre=nombre))
        elif p.nombre=='Proveedor de prueba sin chat':p.nombre=nombre
        abastecedores[codigo]=p
    insumos={}
    for codigo,nombre,unidad,saldo,vida,proveedor in INSUMOS:
        i=s.scalar(select(Ingrediente).where(Ingrediente.codigo=='DEMO-'+codigo))
        if not i:
            leido=crear_ingrediente(s,'DEMO-'+codigo,nombre,unidad);i=s.get(Ingrediente,leido.id)
        elif i.nombre=='Harina de prueba':i.nombre=nombre
        insumos[codigo]=i
        lote=LoteIngrediente(ingrediente_id=i.id,codigo_lote='DEMO-V2-'+codigo,lote_informado=True,
            saldo_disponible=Decimal(0),fecha_ingreso=FECHA-timedelta(days=1),fecha_caducidad=FECHA+timedelta(days=vida))
        s.add(lote);s.flush()
        if Decimal(saldo):movimiento(s,lote,Decimal(saldo),'APERTURA','demo-v2-insumo-'+codigo,FECHA-timedelta(days=1),admin.id,'Apertura sintética v2; cantidades ficticias')
        if codigo!='HARINA':
            factor=Decimal('30' if unidad=='unidad' else '1000')
            proveedores.crear_oferta(abastecedores[proveedor].id,OfertaCrear(ingrediente_id=i.id,
                descripcion='Bandeja de 30 huevos' if unidad=='unidad' else ('Botella 1 L' if unidad=='ml' else 'Presentación 1 kg'),
                unidad_compra='bandeja' if unidad=='unidad' else ('botella' if unidad=='ml' else 'bolsa'),
                factor_conversion=factor,minimo=1,multiplo=1,preferida=True))
    nuevos=[];ids=[]
    for ficha in PRODUCTOS:
        p=s.scalar(select(Producto).where(Producto.codigo=='DEMO-'+ficha['codigo']))
        if not p:
            p=Producto(codigo='DEMO-'+ficha['codigo'],nombre=ficha['nombre'],demostrar=True,activo=True);s.add(p);s.flush()
            s.add(SkuProducto(producto_id=p.id,origen='bakery',sku_externo=p.codigo,activo=True));nuevos.append((p,ficha))
        ids.append(p.id)
        receta=obtener_receta_activa(s,p.id)
        if not receta or receta.motivo=='Receta sintética de prueba':
            crear_version(s,p.id,[LineaNueva(insumos[c].id,Decimal(n)) for c,n in ficha['receta'].items()],
                'Receta sintética v2 multingrediente; no ficha técnica comercial',admin.id)
        datos={k:ficha[k] for k in ['categoria','descripcion','presentacion']}
        datos.update(publicado=True,imagen=f'/tienda/productos/{ficha["imagen"]}.jpg')
        f=s.get(FichaTienda,p.id)
        if not f:s.add(FichaTienda(producto_id=p.id,precio=Decimal(ficha['precio']),version=1,datos=datos))
        elif f.version==1 and f.datos.get('descripcion')=='Producto del conjunto de prueba':
            registro=nuevo(s,f'demo-v2-ficha-{p.id}','PRECIO',{'origen':VERSION,'producto_id':p.id,'datos':datos},FECHA,admin.id)
            f.datos=datos;f.version+=1;registro.resultado={'producto_id':p.id,'version':f.version,'precio':str(f.precio)}
        for n,(cantidad,dias) in enumerate(ficha['lotes']):
            l=LoteProducto(producto_id=p.id,codigo_lote=f'DEMO-V2-{ficha["codigo"]}-{n}',lote_informado=True,
                fecha_limite_venta=FECHA+timedelta(days=dias),fecha_caducidad=FECHA+timedelta(days=dias),saldo_disponible=0)
            s.add(l);s.flush()
            if cantidad:movimiento(s,l,cantidad,'APERTURA',f'demo-v2-producto-{p.id}-{n}',FECHA-timedelta(days=2),admin.id,'Apertura sintética v2; no representa producción real')
    diarios={}
    for p,ficha in nuevos:
        for n in range(273):
            fecha=date(2026,1,1)+timedelta(days=n)
            cantidad=unidades_sinteticas(ficha['codigo'],fecha,ficha['base'])
            if cantidad is not None:diarios[(p.id,fecha)]=cantidad
    registrar_ventas_diarias(s,diarios,VERSION,hashlib.sha256(VERSION.encode()).hexdigest(),len(diarios),
        'Historial sintético v2 con semana, tendencia y campañas ficticias; no resultados comerciales')
    config=s.get(ConfiguracionOperacion,1)
    config.datos={**config.datos,'producto_ids':list(dict.fromkeys(config.datos['producto_ids']+ids))};config.proxima_revision=None
    negocio=s.get(Negocio,1)
    if negocio.nombre=='Pastelería Maria Juanita · Pruebas':negocio.nombre='Pastelería Maria Juanita · Demo'
    for correo,anterior,nombre in [('admin.foodsave@example.com','Administrador de prueba','Valeria Salazar · Admin demo'),
                                  ('operador.foodsave@example.com','Trabajador de prueba','Luis Quispe · Producción demo')]:
        u=s.scalar(select(Usuario).where(Usuario.correo==correo))
        if u.nombre==anterior:u.nombre=nombre
    aviso(s,'demo-v2:abastecimiento','Demo: insumos para revisar antes de fabricar',
        {'origen':VERSION,'ingredientes':['Mantequilla sin sal: 240 g','Queso crema: 300 g','Fresas frescas: 0 g'],
         'descripcion':'Revisa faltantes en el plan. Proveedores ficticios sin chat: ningún pedido se envió.'})
    aviso(s,'demo-v2:caducidad','Demo: lote de quiche fuera de venta',
        {'origen':VERSION,'descripcion':'El lote inicial de quiche venció el 28/09; la tienda lo excluye aunque conserve saldo físico.'})
    if preparar_modelo and inicial.modelo_id:
        huella=hashlib.sha256(VERSION.encode()).hexdigest()
        tarea=crear_o_recuperar_ejecucion(s,'PREPARAR_MODELO',VERSION+'-modelo',{'version_modelo':VERSION,'huella_inicializacion':huella})
        inicial.estado='DATOS_CARGADOS';inicial.huella_solicitud=huella;inicial.huella_catalogo=huella;inicial.huella_ventas=huella
        inicial.preparacion_ejecucion_id=tarea.id;inicial.preparacion_numero+=1;inicial.mensaje_error=None
    s.flush();return True
