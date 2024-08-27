FROM node:14
COPY . /app
WORKDIR /app
RUN npm install
RUN npm install -g serve
CMD ["npm", "run", "serve"]