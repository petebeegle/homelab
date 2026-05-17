"""Foundry blue/green manifest generation helpers."""

from __future__ import annotations

import re
from pathlib import Path

from .config import APP_DIR
from .errors import FoundryBlueGreenError
from .state import ensure_kustomization_resource, write


def validate_image(image: str) -> str:
    if not re.fullmatch(r"felddy/foundryvtt:[A-Za-z0-9._-]+", image):
        raise FoundryBlueGreenError("prepare requires --image in the form felddy/foundryvtt:<tag>")
    return image


def green_deployment(image: str) -> str:
    return f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  namespace: foundryvtt
  name: foundryvtt-green
  labels:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: green
spec:
  replicas: 1
  selector:
    matchLabels:
      app: foundryvtt
      foundryvtt.petebeegle.com/color: green
  template:
    metadata:
      labels:
        app: foundryvtt
        foundryvtt.petebeegle.com/color: green
    spec:
      securityContext:
        runAsUser: 421
        runAsGroup: 421
        fsGroup: 421
      containers:
        - name: foundryvtt
          image: {image}
          imagePullPolicy: IfNotPresent
          env:
            - name: FOUNDRY_ADMIN_KEY
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_ADMIN_KEY
            - name: FOUNDRY_USERNAME
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_USERNAME
            - name: FOUNDRY_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_PASSWORD
            - name: FOUNDRY_LICENSE_KEY
              valueFrom:
                secretKeyRef:
                  name: foundryvtt-secret
                  key: FOUNDRY_LICENSE_KEY
          ports:
            - name: web
              containerPort: 30000
          volumeMounts:
            - name: foundryvtt-data-persistent-storage
              mountPath: /data
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "4Gi"
              cpu: "1"
      volumes:
        - name: foundryvtt-data-persistent-storage
          persistentVolumeClaim:
            claimName: foundryvtt-data-green-pvc
"""


def green_pvc() -> str:
    return """---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: foundryvtt-data-green-pvc
  namespace: foundryvtt
  labels:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: green
spec:
  storageClassName: nfs-csi-storage
  accessModes:
    - ReadWriteOnce
  dataSource:
    apiGroup: snapshot.storage.k8s.io
    kind: VolumeSnapshot
    name: foundryvtt-blue-pre-upgrade
  resources:
    requests:
      storage: 40G
"""


def blue_snapshot() -> str:
    return """---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: foundryvtt-blue-pre-upgrade
  namespace: foundryvtt
  labels:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: blue
spec:
  volumeSnapshotClassName: nfs-csi-snapshot
  source:
    persistentVolumeClaimName: foundryvtt-data-pvc
"""


def green_preview_service() -> str:
    return """---
apiVersion: v1
kind: Service
metadata:
  name: foundryvtt-green
  labels:
    name: foundryvtt-green
    foundryvtt.petebeegle.com/color: green
  namespace: foundryvtt
spec:
  selector:
    app: foundryvtt
    foundryvtt.petebeegle.com/color: green
  ports:
    - name: web
      port: 80
      targetPort: 30000
"""


def green_preview_route() -> str:
    return """---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: foundryvtt-green-preview
  namespace: foundryvtt
spec:
  parentRefs:
    - name: internal
      namespace: gateway
      sectionName: https-gateway
  hostnames:
    - foundry-green.${cluster_domain}
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: foundryvtt-green
          port: 80
          weight: 1
"""


def write_green_resources(root: Path, image: str) -> None:
    app = root / APP_DIR
    resources = {
        "snapshot-blue.yaml": blue_snapshot(),
        "pvc-green.yaml": green_pvc(),
        "deployment-green.yaml": green_deployment(image),
        "service-green-preview.yaml": green_preview_service(),
        "httproute-green-preview.yaml": green_preview_route(),
    }
    for name, text in resources.items():
        write(app / name, text)
        ensure_kustomization_resource(app / "kustomization.yaml", name)


def ensure_green_prepared(root: Path) -> None:
    required = ["deployment-green.yaml", "pvc-green.yaml", "service-green-preview.yaml", "httproute-green-preview.yaml"]
    missing = [name for name in required if not (root / APP_DIR / name).exists()]
    if missing:
        raise FoundryBlueGreenError(f"green is not prepared; missing {', '.join(missing)}")
