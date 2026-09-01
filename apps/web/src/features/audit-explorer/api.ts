export const audit_explorerEndpoint = "/api/audit-explorer";
export const withCursor = (endpoint: string, cursor?: string) => cursor ? `${endpoint}?cursor=${encodeURIComponent(cursor)}` : endpoint;
