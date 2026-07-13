import { useState, useEffect } from "react";
import CommandBox from "./components/CommandBox";
import Logs from "./components/Logs";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export default function App() {
  const [logs, setLogs] = useState([]);
  const [plan, setPlan] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) {
        setBackendStatus(`offline (${res.status})`);
        return;
      }

      const data = await res.json();
      setBackendStatus(data.groq_configured ? "ready" : "no-api-key");
    } catch (error) {
      setBackendStatus("unreachable");
      console.error("Health check failed:", error);
    }
  };

  const runAgent = async (command) => {
    setLoading(true);
    setLogs(["🧠 Planning task..."]);
    setPlan(null);
    setResults([]);

    try {
      const res = await fetch(`${BACKEND_URL}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });

      // Check if response is ok
      if (!res.ok) {
        throw new Error(`Backend returned ${res.status}: ${res.statusText}`);
      }

      // Get the response text first to debug
      const text = await res.text();

      // Try to parse as JSON
      let data;
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        console.error("Response text:", text.substring(0, 200));
        throw new Error(
          `Backend returned invalid JSON: ${text.substring(0, 100)}`,
        );
      }

      setLogs((data.logs || []).filter((log) => log));
      if (data.plan) setPlan(data.plan);
      if (data.results) setResults(data.results);

      if (!data.success && data.error) {
        setLogs((prev) => [...prev, `❌ ${data.error}`]);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      console.error("Frontend error:", errorMsg);
      setLogs([
        "❌ Frontend Error: " + errorMsg,
        `Backend URL: ${BACKEND_URL}`,
        `Backend Status: ${backendStatus}`,
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            🤖 AI Action Agent
          </h1>
          <p className="text-gray-600">
            Autonomous browser automation powered by AI
          </p>
        </div>

        <CommandBox onRun={runAgent} loading={loading} />

        {results.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <span className="mr-2">🎯</span> Extracted Results
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((result, i) => (
                <div
                  key={i}
                  className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-indigo-200"
                >
                  <div className="text-sm font-semibold text-gray-600 mb-1">
                    {result.label}
                  </div>
                  <div className="text-2xl font-bold text-indigo-700">
                    {result.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {plan && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <span className="mr-2">📋</span> Execution Plan
              </h2>
              <div className="space-y-2">
                {plan.steps.map((step, i) => (
                  <div
                    key={i}
                    className="flex items-start p-3 bg-gray-50 rounded border border-gray-200"
                  >
                    <span className="font-bold text-indigo-600 mr-3">
                      {i + 1}.
                    </span>
                    <div className="flex-1">
                      <span className="font-semibold text-gray-700">
                        {step.action}
                      </span>
                      <div className="text-sm text-gray-500 mt-1">
                        {step.url && <div>URL: {step.url}</div>}
                        {step.selector && <div>Selector: {step.selector}</div>}
                        {step.text && <div>Text: {step.text}</div>}
                        {step.ms && <div>Wait: {step.ms}ms</div>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <Logs logs={logs} loading={loading} />
        </div>
      </div>
    </div>
  );
}
