export function EstadoCarga({ error, alReintentar }: { error?: string; alReintentar?: () => void }) {
  if (error) {
    return (
      <div className="t-contenedor t-estado" role="alert">
        <h1>No pudimos abrir la tienda</h1>
        <p>{error}</p>
        {alReintentar ? <button type="button" className="t-boton-primario" onClick={alReintentar}>Reintentar</button> : null}
      </div>
    );
  }
  return <div className="t-contenedor t-estado" role="status"><span className="t-cargando" aria-hidden="true" />Preparando la vitrina…</div>;
}
