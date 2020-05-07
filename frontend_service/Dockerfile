FROM node:10
WORKDIR /usr/src/frontend

COPY . /usr/src/frontend
RUN npm install

EXPOSE 8000

ENV HOST '0.0.0.0'
ENV PORT 8000

CMD [ "node", "server.js" ]