FROM nginx:1.21-alpine

# Supprimer la configuration par défaut
RUN rm /etc/nginx/conf.d/default.conf

# Copier notre configuration personnalisée
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
