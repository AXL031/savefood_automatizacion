FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
ARG NEXT_PUBLIC_FOODSAVE_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_TIENDA_API_URL=http://localhost:8001
ARG NEXT_PUBLIC_GOOGLE_CLIENT_ID=
ARG NEXT_PUBLIC_TIENDA_MODO=ejemplo
ENV NEXT_PUBLIC_FOODSAVE_API_URL=$NEXT_PUBLIC_FOODSAVE_API_URL NEXT_PUBLIC_TIENDA_API_URL=$NEXT_PUBLIC_TIENDA_API_URL NEXT_PUBLIC_GOOGLE_CLIENT_ID=$NEXT_PUBLIC_GOOGLE_CLIENT_ID NEXT_PUBLIC_TIENDA_MODO=$NEXT_PUBLIC_TIENDA_MODO
RUN npm run build
RUN addgroup -S tienda && adduser -S -G tienda tienda \
    && mkdir -p /app/.next/cache && chown -R tienda:tienda /app/.next/cache
USER tienda
CMD ["npm", "run", "start"]
