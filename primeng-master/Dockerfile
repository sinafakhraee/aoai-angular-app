# Use Node.js image
FROM node:14
WORKDIR /app
# Install http-server
# RUN npm install -g http-server
RUN npm install -g serve
# Copy the built application
COPY ./dist/primeng/browser .
# Expose the port
EXPOSE 8080
# Start the server
# CMD [ "http-server", "-p", "8080" ]
CMD [ "serve", "-p", "8080", "-s", "." ]