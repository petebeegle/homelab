export KUBERNETES_API_SERVER_ADDRESS=https://192.168.3.60
export KUBERNETES_API_SERVER_PORT=6443

helm repo add cilium https://helm.cilium.io/

helm upgrade \
    cilium \
    cilium/cilium \
    --version 1.16.1 \
    --namespace kube-system \
    --set ipam.mode=kubernetes \
    --set kubeProxyReplacement=true \
    --set securityContext.capabilities.ciliumAgent="{CHOWN,KILL,NET_ADMIN,NET_RAW,IPC_LOCK,SYS_ADMIN,SYS_RESOURCE,DAC_OVERRIDE,FOWNER,SETGID,SETUID}" \
    --set securityContext.capabilities.cleanCiliumState="{NET_ADMIN,SYS_ADMIN,SYS_RESOURCE}" \
    --set cgroup.autoMount.enabled=false \
    --set cgroup.hostRoot=/sys/fs/cgroup \
    --set k8sServiceHost=localhost \
    --set k8sServicePort=7445 \
    --set hubble.relay.enabled=true \
    --set hubble.ui.enabled=true \
	--set hostFirewall.enabled=true \

