``` 
- sh build-nifi.sh 1.16.3
- docker image ls
- docker run --platform=linux/arm64 --name nifi -p 8443:8443 -e SINGLE_USER_CREDENTIALS_USERNAME=admin -e SINGLE_USER_CREDENTIALS_PASSWORD=ctsBtRBKHRAx69EqUghvvgEvjnaLjFEB -d apache/nifi:1.16.3-arm64
```

- To run via Docker Compose
```
- docker-compose up -d
```