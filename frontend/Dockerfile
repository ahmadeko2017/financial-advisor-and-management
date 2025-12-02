FROM node:20-slim AS base

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build for verification; artifacts in /app/dist
RUN npm run build

# Default command runs dev server (for local compose)
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "--port", "5173"]
