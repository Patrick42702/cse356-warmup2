FROM node:18

WORKDIR /app

COPY package*.json .

RUN npm i next@latest react@latest react-dom@latest

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

