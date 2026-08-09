# 1Password Monitoring Contract

- kube-state-metrics reads only `OnePasswordItem` resource metadata/status through list/watch/get.
- `onepassword_item_info` contains item name, namespace, and Ready condition only.
- Operator-unavailable detects both missing Deployment and desired-minus-available replicas greater than zero.
- Item-unready counts all item metrics whose Ready value is not exactly `True`, including a missing Ready label.
- Both alerts use `for: 10m`, `execErrState: Error`, and actionable metadata-only runbooks.
