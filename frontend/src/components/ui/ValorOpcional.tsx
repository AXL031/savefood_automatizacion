/**
 * Muestra un valor que puede ser desconocido.
 *
 * En FoodSave la ausencia de dato **no** es cero: un día sin venta es desconocido
 * y un lote sin fecha tiene vigencia desconocida. Este componente evita que cada
 * pantalla resuelva `?? 0` por su cuenta y borre esa diferencia.
 */
export function ValorOpcional({ valor, textoAusente = "Sin dato" }: { valor: string | number | null | undefined; textoAusente?: string }) {
  if (valor === null || valor === undefined || valor === "") {
    return <span className="helper-text">{textoAusente}</span>;
  }
  return <>{valor}</>;
}
