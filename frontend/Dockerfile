## this is dockerfile for my frontend directory
## stage 1 build
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

## stage 2 runtime ## this is dockerfile for my frontend directory
FROM node:18-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=frontend-build /app/public ./public
COPY --from=frontend-build /app/.next ./.next
COPY --from=frontend-build /app/node_modules ./node_modules
COPY --from=frontend-build /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
