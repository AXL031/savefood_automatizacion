export function formatearMoneda(valor: number, moneda = "PEN"): string {
  if (!Number.isFinite(valor)) return "Sin dato";
  try {
    return new Intl.NumberFormat("es-PE", { style: "currency", currency: moneda }).format(valor);
  } catch {
    return `${valor.toFixed(2)} ${moneda}`;
  }
}

export function formatearCantidad(valor: number, unidad: string, decimales = 2): string {
  if (!Number.isFinite(valor)) return "Sin dato";
  const cantidad = new Intl.NumberFormat("es-PE", { maximumFractionDigits: decimales }).format(valor);
  return `${cantidad} ${unidad}`;
}
