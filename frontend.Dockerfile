FROM node:20-alpine

WORKDIR /app

COPY app/frontend/package*.json ./

RUN npm install

COPY app/frontend/ ./

RUN npm run build

ENV PORT=3001
EXPOSE 3001

CMD ["npm", "start"]