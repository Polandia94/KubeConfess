from kubernetes.client.rest import ApiException

DANGEROUS_ROLES = [
    "cluster-admin",
    "admin",
    "edit",
]

DANGEROUS_VERBS = ["*", "create", "delete", "patch", "update"]
DANGEROUS_RESOURCES = ["*", "secrets", "pods", "rolebindings",
                       "clusterrolebindings", "serviceaccounts"]


def list_rolebindings(k8s_rbac, namespace: str = "all") -> str:
    try:
        # ClusterRoleBindings — always cluster scoped
        crbs = k8s_rbac.list_cluster_role_binding().items

        # RoleBindings
        if namespace == "all":
            rbs = k8s_rbac.list_role_binding_for_all_namespaces().items
        else:
            rbs = k8s_rbac.list_namespaced_role_binding(namespace=namespace).items

        lines = []

        # ── ClusterRoleBindings ───────────────────────────────────────────────
        lines.append(f"ClusterRoleBindings ({len(crbs)}):\n")
        for crb in crbs:
            role = crb.role_ref.name
            subjects = crb.subjects or []
            is_dangerous = role in DANGEROUS_ROLES

            flag = " ⚠ CRITICAL" if role == "cluster-admin" else " ⚠" if is_dangerous else ""
            lines.append(f"  {crb.metadata.name} → {role}{flag}")

            for s in subjects:
                ns_str = f"/{s.namespace}" if hasattr(s, "namespace") and s.namespace else ""
                lines.append(f"    subject: {s.kind}{ns_str}/{s.name}")
            lines.append("")

        # ── RoleBindings ──────────────────────────────────────────────────────
        lines.append(f"RoleBindings ({len(rbs)}):\n")
        for rb in rbs:
            role = rb.role_ref.name
            subjects = rb.subjects or []
            is_dangerous = role in DANGEROUS_ROLES

            flag = " ⚠" if is_dangerous else ""
            lines.append(f"  {rb.metadata.namespace}/{rb.metadata.name} → {role}{flag}")

            for s in subjects:
                ns_str = f"/{s.namespace}" if hasattr(s, "namespace") and s.namespace else ""
                lines.append(f"    subject: {s.kind}{ns_str}/{s.name}")
            lines.append("")

        return "\n".join(lines)

    except ApiException as e:
        return f"Kubernetes API error: {e.status} {e.reason}"


definition = {
    "type": "function",
    "function": {
        "name": "list_rolebindings",
        "description": (
            "List all RoleBindings and ClusterRoleBindings. "
            "Shows what role each binding grants and who it grants it to (users, groups, ServiceAccounts). "
            "Flags cluster-admin bindings as CRITICAL and other dangerous roles. "
            "Use this to map who has what access cluster-wide, "
            "or to find which ServiceAccounts are over-privileged."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "description": "Namespace to list RoleBindings from, or 'all' for cluster-wide."
                }
            },
            "required": []
        }
    }
}