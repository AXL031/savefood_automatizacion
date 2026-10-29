/** Logo de Pastelería Maria Juanita: ilustración circular con fondo transparente. */
export function LogoTienda({ tamano = 44, decorativo = true }: { tamano?: number; decorativo?: boolean }) {
  // eslint-disable-next-line @next/next/no-img-element
  return <img src="/tienda/logo-192.png" width={tamano} height={tamano} alt={decorativo ? "" : "Pastelería Maria Juanita"} aria-hidden={decorativo || undefined} className="t-logo" />;
}
