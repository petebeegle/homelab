# Resize A PVC

Patch the PVC request to the new size:

```sh
kubectl -n monitoring patch pvc "${PVC_NAME}" -p '{"spec": {"resources": {"requests": {"storage": "10Gi"}}}}'
```

Before patching, confirm the StorageClass supports volume expansion.
