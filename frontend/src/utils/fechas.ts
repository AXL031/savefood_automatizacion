export function formatearFechaHora(valor: string | null | undefined, zonaHoraria = "America/Lima"): string {
  if (!valor) return "Sin fecha";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return "Fecha inválida";
  try {
    return new Intl.DateTimeFormat("es-PE", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: zonaHoraria,
    }).format(fecha);
  } catch {
    return new Intl.DateTimeFormat("es-PE", { dateStyle: "medium", timeStyle: "short" }).format(fecha);
  }
}

export function formatearDuracion(inicio: string | null, fin: string | null): string {
  if (!inicio || !fin) return "En curso";
  const segundos = Math.round((new Date(fin).getTime() - new Date(inicio).getTime()) / 1000);
  if (!Number.isFinite(segundos) || segundos < 0) return "Sin dato";
  return segundos < 60 ? `${segundos} s` : `${Math.floor(segundos / 60)} min ${segundos % 60} s`;
}
