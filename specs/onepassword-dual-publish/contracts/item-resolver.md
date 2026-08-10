# Item Resolver Contract

- Input: authenticated user `op` session, vault title, static production inventory, output directory.
- Captured data: vault/item JSON in process memory only; no values are logged.
- Validation: one unique item per title, valid vault/item IDs, no URLs/files, and exact set of non-empty field labels.
- Output: `OnePasswordItem` YAML and Kustomization containing namespace, generated name, Secret type, vault ID, and item ID only.
- Failure: reports only item title and mismatch class/count; never a value or field value.
