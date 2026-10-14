/** Logotipo de FoodSave: brote sobre fondo hoja. Decorativo; el nombre va siempre como texto al lado. */
export function MarcaFoodSave({ fondo = "#17604E" }: { fondo?: string }) {
  return <svg className="brand-logo" viewBox="0 0 44 44" aria-hidden="true" focusable="false">
    <rect width="44" height="44" rx="12" fill={fondo} />
    <path d="M22 33V21" stroke="#F2B544" strokeWidth="2.6" strokeLinecap="round" />
    <path d="M22 23c0-6 4-9 10-9 0 6-4 9-10 9Z" fill="#F2B544" />
    <path d="M22 26c0-5-3.5-7.5-8.5-7.5 0 5 3.5 7.5 8.5 7.5Z" fill="#9FD3B8" />
  </svg>;
}
