FROM node:18-alpine

RUN npm install -g @tdurieux/bash-command-extractor@0.2.3

EXPOSE 8080

USER node

CMD ["bash-command-extractor", "--server"]
