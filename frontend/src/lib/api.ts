import { QueryResponse, StatsResponse, IngestResponse, DeleteResponse } from "@/types/api";

const API_BASE = "http://localhost:8000";

export async function queryKnowledgeBase(question: string, verbose = false): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, verbose }),
  });

  if (!response.ok) {
    throw new Error(`Query failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE}/api/stats`);

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }

  return response.json();
}

export async function ingestDocuments(urls: string[]): Promise<IngestResponse> {
  const response = await fetch(`${API_BASE}/api/documents/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ urls, files: [] }),
  });

  if (!response.ok) {
    throw new Error(`Ingestion failed: ${response.statusText}`);
  }

  return response.json();
}

export async function clearKnowledgeBase(): Promise<DeleteResponse> {
  const response = await fetch(`${API_BASE}/api/documents?confirm=true`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Clear failed: ${response.statusText}`);
  }

  return response.json();
}

export interface ContactFormData {
  name: string;
  email: string;
  message: string;
}

export interface ContactFormResponse {
  id: string;
  name: string;
  email: string;
  message: string;
  timestamp: string;
  email_sent: boolean;
}

export async function submitContactForm(data: ContactFormData): Promise<ContactFormResponse> {
  const response = await fetch(`${API_BASE}/api/contact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Submission failed: ${response.statusText}`);
  }

  return response.json();
}
