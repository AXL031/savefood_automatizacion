"""Datos de prueba autorizados para la aplicación actual, con respaldo previo.

Los datos añadidos son sintéticos, no ventas medidas ni cierre automático.
El modelo usa una partición manual declarada para probar el día objetivo.
"""
import csv
import hashlib
import json
import os
import statistics
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import select, text
from sqlalchemy.engine import make_url

if os.getenv('PREPARAR_JORNADA_AUTORIZADA')!='2026-10-28' or make_url(os.environ['DATABASE_URL']).database!='foodsave':
    raise RuntimeError('Requiere preparación expresa del 28/10 en la instalación actual y respaldo previo.')

from app.principal import app  # noqa: registra los modelos de la aplicación existente.
from app.core.base_datos import SessionLocal
from app.modules.autenticacion.modelos import Usuario
from app.modules.negocios.modelos import Negocio
from app.modules.productos.modelos import Producto
from app.modules.ventas.modelos import VentaDiaria
from app.modules.ventas.servicio import registrar_ventas_diarias, leer_historial
from app.modules.ventas import caja
from app.modules.ventas.esquemas_caja import CotizarVenta, RegistrarVenta
from app.modules.inventario.entradas import registrar as registrar_entrada, EntradaCrear
from app.modules.inventario.modelos import LoteIngrediente
from app.modules.inventario.servicio import registrar_ajuste, ServicioInventarioV01
from app.modules.ingredientes.modelos import Ingrediente
from app.modules.recetas.servicio import recetas_activas
from app.modules.automatizaciones.modelos import ProgramacionDemo, EjecucionAutomatizacion
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.automatizaciones.flujo import guardar_configuracion, comprobar, programar_flujo, gestionar
from app.modules.automatizaciones.esquemas import ConfigurarFlujo, ProgramarFlujo
from app.modules.pronosticos.modelos import ArtefactoModelo
from app.modules.pronosticos.ml_runtime import preparar_ruta_ml
from app.modules.comercio.catalogo import guardar_ficha
from app.modules.comercio.esquemas import Ficha
from app.modules.comercio.modelos import ConfiguracionComercio, EventoPublicacion, PublicacionProducto, ReservaTienda
from app.modules.comercio.publicaciones import preparar
from app.modules.operaciones.servicio import configuracion
from app.modules.operaciones.monitoreo import revisar
from app.modules.promociones.servicio import guardar_regla
from app.modules.promociones.esquemas import ConfigurarRegla
from pwdlib import PasswordHash

HOY=date.fromisoformat(os.environ['PREPARAR_JORNADA_AUTORIZADA']);AYER=HOY-timedelta(days=1)
MARCA=f'prueba-jornada-{HOY.isoformat()}'
EVIDENCIA=Path('/evidencia');EVIDENCIA.mkdir(exist_ok=True)
CODIGOS=['baguette','croissant','brioche','pain_au_chocolat','briochette','brownies','cookie','eclair','tartelette','tartelette_fraise','pain_de_mie','sand_jb_emmental']
REMANENTES=[18,12,9,0,4,8,3,0,10,6,0,5]


def entrenar(s,ids):
    version=MARCA+'-particion-manual'
    existente=s.scalar(select(ArtefactoModelo).where(ArtefactoModelo.version_modelo==version))
    if existente:return existente
    preparar_ruta_ml()
    from particion import Particion
    from artefacto import entrenar_y_exportar
    from metadata import verificar_artefacto_completo
    # Entrenar hasta agosto y validar septiembre; octubre queda fuera de ambos.
    inicio_mes=HOY.replace(day=1);fin_val=inicio_mes-timedelta(days=1)
    inicio_val=fin_val.replace(day=1);fin_train=inicio_val-timedelta(days=1)
    principio=s.scalar(select(VentaDiaria.fecha_local).order_by(VentaDiaria.fecha_local).limit(1))
    p=Particion(str(principio),str(fin_train),str(inicio_val),str(fin_val),str(inicio_mes),str(HOY),20,1,1)
    ventas=leer_historial(s,ids,principio,HOY)
    h=hashlib.sha256(json.dumps([(v.producto_id,str(v.fecha_local),v.unidades_vendidas,v.revision_venta_id) for v in ventas]).encode()).hexdigest()
    carpeta=Path(os.environ['MODEL_ARTIFACT_DIR'])/version;carpeta.mkdir(exist_ok=True)
    archivo=EVIDENCIA/'ventas-modelo-demo.csv'
    with archivo.open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(['comercio_id','sucursal_id','fecha_local','producto_id','unidades_vendidas'])
        w.writerows(('piloto','principal',v.fecha_local,v.sku_externo,v.unidades_vendidas) for v in ventas)
    entrenar_y_exportar(archivo,'piloto','principal',p,carpeta,version)
    meta=json.loads((carpeta/'metadata.json').read_text())
    meta['particion']['version_politica']='ESCENARIO_MANUAL_JORNADA_v1'
    meta['nota']='Partición manual para exposición del 28/10; octubre reservado. Historia añadida sintética. No evaluar como evidencia comercial.'
    meta['huella_datos_entrenamiento']=h
    (carpeta/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    verificar_artefacto_completo(carpeta,'piloto','principal')
    modelo=ArtefactoModelo(version_modelo=version,ruta_local=version,sha256=meta['sha256_artefacto'],
        huella_datos_entrenamiento=h,fecha_corte_entrenamiento=fin_val,particion_json=meta['particion'],estado='LISTO_DEMO')
    s.add(modelo);s.flush();return modelo


def preparar_datos():
    with SessionLocal.begin() as s:
        assert s.execute(text('SELECT current_database()')).scalar_one()=='foodsave'
        anterior=s.scalar(select(EjecucionAutomatizacion).where(EjecucionAutomatizacion.clave_idempotencia==MARCA+'-lista'))
        if anterior:
            archivo=EVIDENCIA/'escenario.json'
            if archivo.exists():
                from app.modules.automatizaciones.modelos import ConfiguracionFlujo
                resumen=json.loads(archivo.read_text())
                resumen['diagnostico']=comprobar(s,ConfigurarFlujo(**s.get(ConfiguracionFlujo,1).parametros))
                archivo.write_text(json.dumps(resumen,ensure_ascii=False,indent=2,default=str)+'\n')
            print('Escenario ya preparado; conservar avances y datos de la demostración.');return
        u=s.scalar(select(Usuario).where(Usuario.rol=='ADMINISTRADOR',Usuario.activo.is_(True)).order_by(Usuario.id))
        assert u,'Se conserva el administrador existente; no se crean cuentas ni contraseñas.'
        productos={p.codigo:p for p in s.scalars(select(Producto).where(Producto.codigo.in_(CODIGOS)))}
        assert set(productos)==set(CODIGOS)
        ids=[productos[c].id for c in CODIGOS]
        recetas=recetas_activas(s,ids);assert len(recetas)==len(ids)
        # Procedencia sintética explícita. Solo se completan pares ausentes posteriores al histórico.
        ultimo=s.scalar(select(VentaDiaria.fecha_local).order_by(VentaDiaria.fecha_local.desc()).limit(1))
        origen_hist=leer_historial(s,ids,ultimo-timedelta(days=56),ultimo+timedelta(days=1))
        diarios={};dia=ultimo+timedelta(days=1)
        while dia<=AYER:
            for id_ in ids:
                muestras=[v.unidades_vendidas for v in origen_hist if v.producto_id==id_ and v.fecha_local.weekday()==dia.weekday()]
                if not muestras:muestras=[v.unidades_vendidas for v in origen_hist if v.producto_id==id_]
                assert muestras,f'Sin base para producto {id_}'
                base=statistics.median(muestras)
                factor=Decimal(90+int(hashlib.sha256(f'{id_}:{dia}'.encode()).hexdigest()[:4],16)%21)/100
                diarios[id_,dia]=max(8,min(80,int(Decimal(str(base))*factor)))
            dia+=timedelta(days=1)
        if diarios:
            huella=hashlib.sha256(json.dumps([(i,str(d),v) for (i,d),v in sorted(diarios.items())]).encode()).hexdigest()
            registrar_ventas_diarias(s,diarios,MARCA,huella,len(diarios),
                'SIMULACIÓN explícita: continuidad basada en mediana del mismo día de semana; no son ventas observadas.',origen='ESCENARIO_DEMO')
        ayer={id_:s.scalar(select(VentaDiaria.unidades_vendidas).where(VentaDiaria.producto_id==id_,VentaDiaria.fecha_local==AYER)) for id_ in ids}
        assert all(v is not None for v in ayer.values())
        lineas=[]
        for i,id_ in enumerate(ids):
            fin=HOY if i<3 or i==7 else HOY+timedelta(days=2)
            lineas.append({'producto_id':id_,'codigo_lote':f'DEMO-{AYER}-{id_}','cantidad':ayer[id_]+REMANENTES[i],
                'fecha_elaboracion':str(AYER),'fecha_limite_venta':str(fin),'fecha_caducidad':str(fin)})
        registrar_entrada(s,EntradaCrear(clave_operacion=MARCA+'-entrada-ayer',fecha_entrada=AYER,
            motivo='SIMULACIÓN: producción disponible del día anterior y remanente para hoy.',lineas=lineas),u)
        reloj=caja.ahora
        try:
            for turno in range(4):
                caja.ahora=lambda t=turno:datetime.combine(AYER,datetime.min.time(),ZoneInfo('America/Lima')).astimezone(timezone.utc)+timedelta(hours=9+t*2)
                ls=[{'producto_id':id_,'cantidad':ayer[id_]//4+(turno<ayer[id_]%4)} for id_ in ids]
                q,_=caja.cotizar(s,CotizarVenta(clave_idempotencia=f'{MARCA}-cot-ayer-{turno}',lineas=ls),u)
                caja.registrar_ticket(s,RegistrarVenta(clave_idempotencia=f'{MARCA}-ticket-ayer-{turno}',cotizacion_id=q.id,
                    total_revisado=f'{q.total:.2f}',cobro_presencial={'medio':'EFECTIVO','importe_recibido':f'{q.total:.2f}'}),u)
        finally:caja.ahora=reloj
        frescos=[{'producto_id':ids[i],'codigo_lote':f'DEMO-{HOY}-{ids[i]}','cantidad':cantidad,
            'fecha_elaboracion':str(HOY),'fecha_limite_venta':str(HOY+timedelta(days=2)),
            'fecha_caducidad':str(HOY+timedelta(days=2))} for i,cantidad in [(3,10),(7,7),(10,6)]]
        registrar_entrada(s,EntradaCrear(clave_operacion=MARCA+'-entrada-hoy',fecha_entrada=HOY,
            motivo='SIMULACIÓN: lotes frescos de apertura de hoy.',lineas=frescos),u)
        ingredientes={l.ingrediente_id for r in recetas.values() for l in r.lineas}
        # Saldos pequeños autorizados para provocar faltantes, con ajustes auditados y respaldo.
        for l in s.scalars(select(LoteIngrediente).where(LoteIngrediente.ingrediente_id.in_(ingredientes),LoteIngrediente.saldo_disponible>0)):
            if (l.fecha_ingreso and l.fecha_ingreso>HOY) or (l.fecha_caducidad and l.fecha_caducidad<HOY):continue
            registrar_ajuste(s,SimpleNamespace(tipo_item='ingrediente',lote_id=l.id,delta=-l.saldo_disponible,
                motivo='SIMULACIÓN: saldo anterior reemplazado por apertura pequeña del escenario.',clave_operacion=f'{MARCA}-saldo-insumo-{l.id}',
                efectivo_en_demo=datetime.combine(HOY,datetime.min.time())),u.id)
        filas=[SimpleNamespace(tipo='ingrediente',codigo=i.codigo,codigo_lote=f'DEMO-{AYER}-{i.id}',cantidad=Decimal(2 if i.unidad_base=='unidad' else 100),
            fecha_caducidad=HOY+timedelta(days=10),fecha_limite_venta=None) for i in s.scalars(select(Ingrediente).where(Ingrediente.id.in_(ingredientes)))]
        ServicioInventarioV01().registrar_apertura(s,filas,{},
            {i.codigo:i.id for i in s.scalars(select(Ingrediente).where(Ingrediente.id.in_(ingredientes)))},AYER,MARCA+'-insumos')
        for l in s.scalars(select(LoteIngrediente).where(LoteIngrediente.codigo_lote.like(f'DEMO-{AYER}-%'))):l.fecha_ingreso=AYER
        modelo=entrenar(s,ids)
        fotos={'baguette':'baguette','croissant':'croissant','brioche':'brioche','eclair':'eclair','tartelette_fraise':'tartaleta-fresas'}
        for codigo in CODIGOS:
            p=productos[codigo];f=s.get(PublicacionProducto,p.id)
            categoria='panes' if codigo in CODIGOS[:5] or codigo=='pain_de_mie' else 'bocados' if codigo=='sand_jb_emmental' else 'postres-personales'
            guardar_ficha(s,p.id,Ficha(version_actual=f.version if f else 0,publicado=True,categoria=categoria,
                descripcion='Producto del escenario de demostración del 28/10.',presentacion='Unidad',
                imagen=f'/tienda/productos/{fotos[codigo]}.jpg' if codigo in fotos else ''),u)
        guardar_regla(s,ConfigurarRegla(habilitada=True,hora_revision='00:00',hora_cierre='23:59',stock_umbral=5,descuento_pct=25,descuento_maximo_pct=30),u.id)
        c=configuracion(s);c.datos={'reloj':'ACTUAL','fecha_escenario':None,'hora_escenario':'17:15:00','producto_ids':ids,'habilitada':True};c.proxima_revision=None
        revisar(s,forzar=True);preparar(s)
        local=(datetime.now(ZoneInfo('America/Lima'))+timedelta(minutes=3)).replace(tzinfo=None)
        datos=ConfigurarFlujo(producto_ids=ids,modelo_id=modelo.id,fecha_objetivo_demo=HOY,hora_simulada='08:00',
            primera_ejecucion_local=local,dias=1,modo_envio_pedidos='REQUIERE_APROBACION',prueba_repetible=True)
        guardar_configuracion(s,datos,u.id);diagnostico=comprobar(s,datos)
        assert diagnostico['listo'],diagnostico
        ps=programar_flujo(s,ProgramarFlujo(**datos.model_dump(),clave_idempotencia=MARCA+'-flujo'),u.id)
        for p in ps:gestionar(s,p.id,u.id,'Escenario listo: ejecutar manualmente durante la demostración.',accion='PAUSAR')
        marca=crear_o_recuperar_ejecucion(s,'PREPARAR_MODELO',MARCA+'-lista',{'escenario':MARCA,'sintetico':True})
        marca.estado='COMPLETADA';marca.fin_en=datetime.now(timezone.utc)
        marca.datos_salida_json={'modelo_id':modelo.id,'producto_ids':ids,'programacion_id':ps[0].id,'ventas_sinteticas':len(diarios)}
        resumen={'fecha':str(HOY),'ayer':str(AYER),'modelo_id':modelo.id,'producto_ids':ids,'programacion_id':ps[0].id,
            'ventas_ayer':ayer,'stock_apertura':{ids[i]:REMANENTES[i]+({3:10,7:7,10:6}.get(i,0)) for i in range(len(ids))},
            'sintetico':True,'particion_manual':modelo.particion_json,'diagnostico':diagnostico}
        (EVIDENCIA/'escenario.json').write_text(json.dumps(resumen,ensure_ascii=False,indent=2,default=str)+'\n')
        print('Datos preparados: 12 productos, cuatro ventas del día anterior, lotes recientes y programación PAUSADA.')


if __name__=='__main__':preparar_datos()
