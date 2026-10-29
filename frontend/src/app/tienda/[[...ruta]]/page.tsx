import { redirect } from "next/navigation";

/** Compatibilidad con enlaces anteriores: la tienda se despliega como proyecto aparte. */
export default async function TiendaExterna({ params }: { params: Promise<{ ruta?: string[] }> }) {
  const { ruta = [] } = await params;
  const base = (process.env.TIENDA_WEB_URL ?? "http://localhost:3101").replace(/\/$/, "");
  redirect(`${base}/tienda${ruta.length ? `/${ruta.map(encodeURIComponent).join("/")}` : ""}`);
}
