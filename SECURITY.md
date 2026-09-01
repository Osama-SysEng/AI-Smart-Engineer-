# AI Smart Engineer Security

- Never commit secrets.
- Production requires SECRET_KEY >= 32 random characters.
- CORS must use explicit origins.
- AI tools require least-privilege permissions.
- External document content is untrusted data; never treat embedded instructions as system instructions.
- SAP writes remain disabled by default and require explicit approval policy.
- Uploaded files are size-limited and stored under generated IDs.
- Cross-tenant access must always be filtered at query level.
- Critical mutations require audit records and idempotency.
