---
status: current
scope:
  - jellyfin
  - hardware-transcoding
  - intel-gpu
last_verified: 2026-05-24
---

# Jellyfin Hardware Transcoding

Jellyfin uses Intel Quick Sync Video through the Intel GPU Device Plugin. The base dependency is the Intel Device Plugins Operator, and the GPU plugin is reconciled only after the operator is ready. Both Helm releases are pinned to chart `0.35.0` from `https://intel.github.io/helm-charts`.

The GPU plugin intentionally does not use Node Feature Discovery. It sets `nodeFeatureRule=false` and targets only nodes labeled `homelab.petebeegle.com/jellyfin-igpu=true`. The matching node label and iGPU passthrough are provided by the separate `jellyfin-gpu-nodes` implementation; without that prerequisite, Jellyfin pods should remain unscheduled instead of falling back to CPU-only placement.

Jellyfin scheduling hard-requires the same node label and requests `gpu.intel.com/i915: 1` with matching limits. Do not add privileged mode, supplemental host groups, or `/dev/dri` hostPath mounts for Jellyfin. Device access should come from the Intel GPU Device Plugin allocation.

The Jellyfin init bootstrap enforces `/config/config/encoding.xml` on each pod start:

- `<HardwareAccelerationType>qsv</HardwareAccelerationType>`
- `<VaapiDevice>/dev/dri/renderD128</VaapiDevice>` and `<QsvDevice>/dev/dri/renderD128</QsvDevice>`
- `<EnableHardwareEncoding>true</EnableHardwareEncoding>`
- hardware decoding codecs `h264`, `hevc`, `mpeg2video`, `vc1`, `vp8`, and `vp9`
- HEVC and VP9 10-bit decode toggles enabled, with native VA-API decoder preference enabled for QSV pipelines

After reconcile, acceptance should confirm:

1. The node intended for Jellyfin has label `homelab.petebeegle.com/jellyfin-igpu=true`.
2. `kubectl describe node <node>` advertises allocatable `gpu.intel.com/i915`.
3. `flux -n flux-system get kustomization intel-device-plugins-operator intel-gpu-device-plugin app-jellyfin` reports Ready.
4. The Jellyfin pod is scheduled on the labeled node and has `gpu.intel.com/i915: 1` in requests and limits.
5. `kubectl -n jellyfin exec deploy/jellyfin -- /usr/lib/jellyfin-ffmpeg/vainfo` reports the Intel media driver and render device.
6. A 4K HEVC or HEVC Main10 playback test shows QSV decode/encode in the Jellyfin transcode log.

For branch validation, use the Jellyfin development verifier with `--include-cluster-base` once the `jellyfin-gpu-nodes` prerequisite is present. If the development cluster does not yet expose the label and `gpu.intel.com/i915` resource, record the smoke as blocked by that prerequisite and substitute local render checks plus bootstrap tests.
