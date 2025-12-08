# Build Stage
FROM node:22-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Accept build arguments for environment variables
ARG VITE_GOOGLE_MAPS_API_KEY
ARG VITE_ENDPOINT

# Set environment variables for the build
ENV VITE_GOOGLE_MAPS_API_KEY=$VITE_GOOGLE_MAPS_API_KEY
ENV VITE_ENDPOINT=$VITE_ENDPOINT

RUN npm run build

# Production Stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
