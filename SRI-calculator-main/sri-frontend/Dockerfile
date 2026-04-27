# syntax=docker/dockerfile:1

# Stage 1: Build the React application
FROM node:22.13.1-slim AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json for dependency installation
COPY --link package.json package-lock.json ./

# Install dependencies
RUN --mount=type=cache,target=/root/.npm npm ci

# Copy the application source code
COPY --link . .

# Copy the environment file
COPY .env.production .env

# Build the application for production
RUN npm run build

# Stage 2: Serve the built application using a lightweight server
FROM node:22.13.1-slim AS production

# Set the working directory
WORKDIR /app

# Copy the built application from the builder stage
COPY --from=builder /app/build ./build

# Install a lightweight server to serve the application
RUN npm install -g serve

# Expose the port the application will run on
EXPOSE 3000

# Set the default command to serve the application
CMD ["serve", "-s", "build"]
