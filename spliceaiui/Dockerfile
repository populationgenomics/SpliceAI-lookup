FROM node:lts-alpine AS build-stage
ARG BUILDENV=production

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Refer to this post https://stackoverflow.com/questions/50772662/npm-run-build-mode-env-mode-not-working-as-expected
# on why double dashes are required
RUN npm run build -- --mode "$BUILDENV"

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html/
COPY --from=build-stage /app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]