FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Configure npm for corporate proxy (disable strict SSL)
RUN npm config set strict-ssl false

# Install dependencies
RUN npm ci

# Copy EventCatalog content
COPY . .

# Expose port
EXPOSE 3002

# Set PORT environment variable
ENV PORT=3002

# Run dev server
CMD ["npm", "run", "dev"]
