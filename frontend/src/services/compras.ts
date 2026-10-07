import { solicitar } from "./http";
import type { EntradaConciliacion, EntradaRecuperacion, EstadoTelegram, VerificacionDestino, NuevaOferta, Oferta, Pedido, PropuestaCompra, Proveedor } from "@/types/compras";
export function consultarTelegram(token: string, signal?: AbortSignal) { return solicitar<EstadoTelegram>("/proveedores/telegram/configuracion", { token, signal }); }
export function guardarTelegram(token: string, credencial: string) { return solicitar<EstadoTelegram>("/proveedores/telegram/configuracion", { token, method: "POST", body: { token: credencial } }); }
export function comprobarTelegram(token: string) { return solicitar<EstadoTelegram>("/proveedores/telegram/comprobar", { token, method: "POST" }); }
export function buscarChatsTelegram(token: string) { return solicitar<{ chat_id: string; tipo: string }[]>("/proveedores/telegram/chats-pruebas", { token, method: "POST" }); }
export function deshabilitarTelegram(token: string) { return solicitar<EstadoTelegram>("/proveedores/telegram/configuracion", { token, method: "DELETE" }); }
export function verificarDestino(token: string, id: number) { return solicitar<VerificacionDestino>(`/proveedores/${id}/verificar-destino`, { token, method: "POST" }); }
export function listarProveedores(token: string, signal?: AbortSignal) { return solicitar<Proveedor[]>("/proveedores", { token, signal }); }
export function crearProveedor(token: string, entrada: { codigo: string; nombre: string }) { return solicitar<Proveedor>("/proveedores", { token, method: "POST", body: entrada }); }
export function cambiarEstadoProveedor(token: string, id: number, activo: boolean) { return solicitar<Proveedor>(`/proveedores/${id}/estado?activo=${activo}`, { token, method: "PATCH" }); }
export function listarOfertas(token: string, id: number, signal?: AbortSignal) { return solicitar<Oferta[]>(`/proveedores/${id}/ofertas`, { token, signal }); }
export function crearOferta(token: string, id: number, entrada: NuevaOferta) { return solicitar<Oferta>(`/proveedores/${id}/ofertas`, { token, method: "POST", body: entrada }); }
export function marcarPreferida(token: string, id: number) { return solicitar<Oferta>(`/proveedores/ofertas/${id}/preferida`, { token, method: "POST" }); }
export function desactivarOferta(token: string, id: number) { return solicitar<Oferta>(`/proveedores/ofertas/${id}/desactivar`, { token, method: "PATCH" }); }
export function vincularChat(token: string, id: number, chat: string) { return solicitar<Proveedor>(`/proveedores/${id}/chat?chat_id=${encodeURIComponent(chat)}`, { token, method: "PUT" }); }
export function listarPropuestas(token: string, signal?: AbortSignal) { return solicitar<PropuestaCompra[]>("/compras/propuestas", { token, signal }); }
export function generarPedidos(token: string, planId: number) { return solicitar<PropuestaCompra>("/pedidos/generar", { token, method: "POST", body: { plan_id: planId } }); }
export function cancelarPropuesta(token: string, id: number, motivo: string) { return solicitar<PropuestaCompra>(`/compras/propuestas/${id}/cancelar`, { token, method: "POST", body: { motivo } }); }
export function aprobarPedido(token: string, id: number, clave: string, chat: string) { return solicitar<Pedido>(`/pedidos/${id}/aprobar`, { token, method: "POST", body: { clave_idempotencia: clave, chat_id_revisado: chat } }); }
export function rechazarPedido(token: string, id: number, clave: string, motivo: string) { return solicitar<Pedido>(`/pedidos/${id}/rechazar`, { token, method: "POST", body: { clave_idempotencia: clave, motivo } }); }
export function verificarDestinosPropuesta(token: string, id: number) { return solicitar<PropuestaCompra>(`/compras/propuestas/${id}/verificar-destinos`, { token, method: "POST" }); }
export function conciliarPedido(token: string, id: number, entrada: EntradaConciliacion) { return solicitar<Pedido>(`/pedidos/${id}/conciliar`, { token, method: "POST", body: entrada }); }
export function reintentarPedido(token: string, id: number, entrada: EntradaRecuperacion) { return solicitar<Pedido>(`/pedidos/${id}/reintentar`, { token, method: "POST", body: entrada }); }
