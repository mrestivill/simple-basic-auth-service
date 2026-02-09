# simple-basic-auth-service

Simple mock service that requires basic auth authentication

## Docker


```bash
docker run -p 8000:8000 -e USER=xxx, -e PASSWORD=yyy ghcr.io/mrestivill/simple-basic-auth-service:latest
```

open http://localhost:8000 and will require basic auth with the user that your provide.
