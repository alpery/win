# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application
COPY . .

# Build the application
RUN pnpm build

# Runtime stage
FROM nginx:alpine

# Copy the built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY --from=build /app/public/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Run nginx
CMD ["nginx", "-g", "daemon off;"]