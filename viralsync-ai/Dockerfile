# ViralSync AI — 멀티 스테이지 빌드 (Next.js standalone 출력)
FROM node:22-bookworm-slim AS base
RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

# 의존성 설치 + 빌드 (DB 초기화용 'setup' 서비스도 이 단계를 사용)
FROM base AS build
COPY package.json package-lock.json ./
COPY prisma ./prisma
RUN npm ci
COPY . .
ENV NEXT_OUTPUT=standalone
RUN npx prisma generate && npm run build

# 실행 이미지
FROM base AS runner
ENV NODE_ENV=production PORT=3100 HOSTNAME=0.0.0.0
RUN useradd --system --uid 1001 nextjs
COPY --from=build --chown=nextjs /app/.next/standalone ./
COPY --from=build --chown=nextjs /app/.next/static ./.next/static
COPY --from=build --chown=nextjs /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=build --chown=nextjs /app/node_modules/@prisma/client ./node_modules/@prisma/client
USER nextjs
EXPOSE 3100
CMD ["node", "server.js"]
