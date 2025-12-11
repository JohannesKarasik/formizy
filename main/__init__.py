server {
    listen 80;
    server_name 46.101.170.130;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/clinton/formizy;
    }

    location /media/ {
        root /home/clinton/formizy;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/clinton/formizy/gunicorn.sock;
    }
}