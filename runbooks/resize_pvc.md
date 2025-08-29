# Resize a PVC like an idiot

Example below:
```sh
kubectl -n monitoring patch pvc ${PVC_NAME} -p '{"spec": {"resources": {"requests": {"storage": "10Gi"}}}}'
```
> [!IMPORTANT]
> Ensure that the storage-class supports expanding the size
