# Data Model: Helm Action Mode

- **Upgrade**: `serverSideApply=disabled`, `force=false/absent`.
- **Rollback**: `serverSideApply=disabled`, `force=false/absent`.
- **Strategy intent**: `type=Recreate`, `rollingUpdate=null` remains explicit.
- **Result**: live strategy contains only Recreate after API processing.
