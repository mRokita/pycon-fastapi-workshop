FROM node:19-alpine AS svelte-build

WORKDIR /app

COPY ./package.json ./
COPY ./package-lock.json ./
RUN npm install
COPY ./index.html ./vite.config.js ./jsconfig.json ./
COPY ./src ./src
RUN npm run build


# Stage 2 - the production environment
FROM nginx:1.22.1-alpine
COPY --from=svelte-build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]