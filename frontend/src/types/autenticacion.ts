export type Perfil = {
  id: number;
  correo: string;
  nombre: string;
  rol: "ADMINISTRADOR" | "OPERADOR";
};

export type Sesion = {
  token_acceso: string;
  tipo: "bearer";
  expira_en: string;
};

export type Negocio = {
  id: number;
  nombre: string;
  zona_horaria: string;
  moneda: string;
};

export type CambioNegocio = Pick<Negocio, "nombre" | "zona_horaria" | "moneda">;
