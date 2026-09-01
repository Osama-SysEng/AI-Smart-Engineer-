export const approval_centerEndpoint = "/api/approval-center";
export const withCursor = (endpoint: string, cursor?: string) => cursor ? `${endpoint}?cursor=${encodeURIComponent(cursor)}` : endpoint;
