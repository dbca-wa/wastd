# Turtles Database Kubernetes Kustomize overlay configuration

Declarative management of Kubernetes objects using Kustomize.

# How to use

Within an overlay directory, create a `.env` file to contain required secret
values in the format KEY=value (i.e. `overlays/uat/.env`). Required values (some have defaults):

    DATABASE_URL
    SECRET_KEY
    ALLOWED_HOSTS
    CSRF_COOKIE_SECURE
    SESSION_COOKIE_SECURE
    ALLOWED_HOSTS
    CSRF_TRUSTED_ORIGINS
    ADMIN_EMAILS
    EMAIL_HOST
    SITE_CODE
    SITE_NAME
    SITE_TITLE
    GEOSERVER_URL
    MAPBOX_TOKEN
    AZURE_CONTAINER
    AZURE_ACCOUNT_NAME
    AZURE_ACCOUNT_KEY
    ODK_API_PROJECTID
    ODK_API_URL
    ODK_API_EMAIL
    ODK_API_PASSWORD
    DB_HOST
    DB_NAME
    DB_PORT
    DB_USERNAME
    DB_PASSWORD
    DB_DRIVER
    DB_EXTRA_PARAMS

Review the built resource output using `kustomize`:

```bash
kustomize build kustomize/overlays/uat/ | less
```

Run `kubectl` with the `-k` flag to generate resources for a given overlay:

```bash
kubectl apply -k kustomize/overlays/uat --namespace ibms --dry-run=client
```

# References:

- https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
- https://github.com/kubernetes-sigs/kustomize
- https://github.com/kubernetes-sigs/kustomize/tree/master/examples
