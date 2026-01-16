import { useState } from "react";

export default function CommandBox({ onRun, loading }) {
  const [cmd, setCmd] = useState("");

  const examples = [
    "Search for laptops on Amazon and add first result to cart",
    "Go to Google and search for weather in New York",
    "Search for smartphones under 15000 and open first result",
    "Fill contact form with name John and email john@example.com",
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            What do you want the agent to do?
          </label>
          <textarea
            className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all resize-none"
            placeholder="e.g., Search for laptops on Amazon and add first result to cart"
            rows={3}
            value={cmd}
            onChange={(e) => setCmd(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => cmd.trim() && onRun(cmd)}
            disabled={loading || !cmd.trim()}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
          >
            {loading ? (
              <span className="flex items-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Running...
              </span>
            ) : (
              "🚀 Run Agent"
            )}
          </button>

          <button
            onClick={() => setCmd("")}
            disabled={loading}
            className="px-4 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-all disabled:opacity-50"
          >
            Clear
          </button>
        </div>

        <div>
          <p className="text-xs font-semibold text-gray-500 mb-2">
            TRY THESE EXAMPLES:
          </p>
          <div className="flex flex-wrap gap-2">
            {examples.map((ex, i) => (
              <button
                key={i}
                onClick={() => setCmd(ex)}
                disabled={loading}
                className="text-xs px-3 py-2 bg-indigo-50 text-indigo-700 rounded-full hover:bg-indigo-100 transition-all disabled:opacity-50"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
