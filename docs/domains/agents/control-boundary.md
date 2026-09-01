# Agent: control boundary

## Responsibility

The Agent context owns bounded AI interpretation and model-routing control. Tenant scope, actor accountability, correlation identifiers, and policy checks are explicit in its contracts.

## Control boundary

AI may interpret retained evidence but cannot directly override deterministic values, cross a tenant boundary, or execute a sensitive external change without the relevant approval.

## Acceptance signal

A feature is accepted only when domain tests, contract checks, and operational evidence agree.
