FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build
RUN addgroup -S foodsave && adduser -S -G foodsave foodsave && chown -R foodsave:foodsave /app
USER foodsave
CMD ["npm", "run", "start"]
