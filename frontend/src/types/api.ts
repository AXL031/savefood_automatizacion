export type ApiEnvelope<T> = {
  datos: T;
  metadatos?: Record<string, unknown>;
};

export type ApiErrorBody = {
  detail?: string | { msg?: string }[];
  error?: { codigo?: string; mensaje?: string };
};
