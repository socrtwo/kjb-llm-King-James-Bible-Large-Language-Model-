/**
 * API client for the KJB-LLM backend.
 *
 * In development the server runs at http://localhost:8000.
 * For a physical device, replace with your machine's LAN IP or a tunnel URL.
 */

const API_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  "http://localhost:8000";

/**
 * Ask the KJB-LLM a question.
 * @param {string} question  Plain-English question.
 * @returns {Promise<{answer: string, verses: Array<{reference: string, text: string}>}>}
 */
export async function askQuestion(question) {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Server error ${res.status}: ${detail}`);
  }
  return res.json();
}

/**
 * Health check.
 * @returns {Promise<{status: string}>}
 */
export async function healthCheck() {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}
