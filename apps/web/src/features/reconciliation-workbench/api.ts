export const reconciliation_workbenchEndpoint = "/api/reconciliation-workbench";
export const withCursor = (endpoint: string, cursor?: string) => cursor ? `${endpoint}?cursor=${encodeURIComponent(cursor)}` : endpoint;
