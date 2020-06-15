FROM node:10-alpine
WORKDIR /usr/src/frontend

COPY . /usr/src/frontend
RUN yarn

EXPOSE 8000

ENV DATABASE_API_PORT 5000
ENV DATABASE_API_HOST '0.0.0.0'

CMD ["yarn", "start"]