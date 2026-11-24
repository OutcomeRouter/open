permit(principal, action == Action::"addCapacity", resource)
when {
    resource == context.approvedService &&
    context has cost && context.cost >= 0 && context.cost <= context.limit &&
    context has until && context.until <= context.through
};
