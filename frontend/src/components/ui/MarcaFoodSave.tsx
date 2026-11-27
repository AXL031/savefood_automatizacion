/** Logotipo de FoodSave: brote con los cuatro colores de la marca. Decorativo; el nombre va siempre como texto al lado. */
export function MarcaFoodSave() {
  return <svg className="brand-logo" viewBox="0 0 44 44" aria-hidden="true" focusable="false">
    <defs>
      <linearGradient id="fs-marca-fondo" x1="0" y1="0" x2="44" y2="44" gradientUnits="userSpaceOnUse">
        <stop offset="0" stopColor="#4285F4" /><stop offset="1" stopColor="#1A73E8" />
      </linearGradient>
    </defs>
    <rect width="44" height="44" rx="12" fill="url(#fs-marca-fondo)" />
    <path d="M22 33V21" stroke="#FFFFFF" strokeWidth="2.6" strokeLinecap="round" />
    <path d="M22 23c0-6 4-9 10-9 0 6-4 9-10 9Z" fill="#FBBC05" />
    <path d="M22 26c0-5-3.5-7.5-8.5-7.5 0 5 3.5 7.5 8.5 7.5Z" fill="#34A853" />
    <circle cx="33" cy="32" r="3" fill="#EA4335" />
  </svg>;
}
