# Data Model: onepassword-dual-publish

## Inventory Entry

- Namespace and legacy Secret name
- Generated Secret/`OnePasswordItem` name with `-onepassword`
- Unique item title `k8s--<namespace>--<legacy-name>`
- Secret type
- Sorted exact expected key labels

No value, vault ID, or item ID is stored in the inventory.

## Resolved Resource

- Same namespace/generated name/type
- Labels linking the legacy identity
- `spec.itemPath` containing only production vault ID and item ID

The generated Secret is owned by the `OnePasswordItem`; deletion cascades.

## Parity State

- `OnePasswordItem Ready=True`
- Legacy and generated Secret types equal inventory type
- Both key sets equal inventory key set
- Decoded value bytes compare equal for every key
