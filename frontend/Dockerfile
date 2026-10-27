FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
ARG NEXT_PUBLIC_API_URL=
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
# ID de cliente OAuth público de Google; la cuenta local requiere habilitación en API.
ARG NEXT_PUBLIC_GOOGLE_CLIENT_ID=
ENV NEXT_PUBLIC_GOOGLE_CLIENT_ID=${NEXT_PUBLIC_GOOGLE_CLIENT_ID}
ARG NEXT_PUBLIC_TIENDA_MODO=api
ENV NEXT_PUBLIC_TIENDA_MODO=${NEXT_PUBLIC_TIENDA_MODO}
ARG API_INTERNAL_URL=http://api:8000
ENV API_INTERNAL_URL=${API_INTERNAL_URL}
RUN npm run build
RUN addgroup -S foodsave && adduser -S -G foodsave foodsave && mkdir -p /app/.next/cache && chown -R foodsave:foodsave /app/.next/cache
USER foodsave
CMD ["npm", "run", "start"]
