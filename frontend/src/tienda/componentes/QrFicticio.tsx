/** Patrón decorativo con forma de QR. No codifica ningún dato ni cuenta real. */
export function QrFicticio() {
  const n = 21;
  const celdas: [number, number][] = [];
  const enEsquina = (x: number, y: number) => (x < 8 && y < 8) || (x > n - 9 && y < 8) || (x < 8 && y > n - 9);
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      if (!enEsquina(x, y) && ((x * 7 + y * 13 + x * y) % 5 < 2)) celdas.push([x, y]);
    }
  }
  const esquina = (x: number, y: number) => (
    <g key={`${x}-${y}`}>
      <rect x={x} y={y} width="7" height="7" fill="currentColor" />
      <rect x={x + 1} y={y + 1} width="5" height="5" fill="#fff" />
      <rect x={x + 2} y={y + 2} width="3" height="3" fill="currentColor" />
    </g>
  );
  return (
    <svg viewBox={`-1 -1 ${n + 2} ${n + 2}`} width="132" height="132" role="img" aria-label="Código QR de demostración, no válido para pagos" className="t-qr">
      <rect x="-1" y="-1" width={n + 2} height={n + 2} fill="#fff" />
      {esquina(0, 0)}{esquina(n - 7, 0)}{esquina(0, n - 7)}
      {celdas.map(([x, y]) => <rect key={`${x}.${y}`} x={x} y={y} width="1" height="1" fill="currentColor" />)}
      <rect x={n / 2 - 1.5} y={n / 2 - 1.5} width="3" height="3" rx="0.6" fill="#8b5a2b" />
    </svg>
  );
}
