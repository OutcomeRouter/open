package acme

default allow = false

allow if {
    input.request.service == input.grant.service
    input.request.cost >= 0
    input.request.cost <= input.grant.limit
    input.request.until <= input.grant.through
}
