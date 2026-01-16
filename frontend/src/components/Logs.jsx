export default function Logs({ logs, loading }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4 flex items-center">
        <span className="mr-2">📊</span> Execution Logs
      </h2>
      <div className="bg-gray-900 text-green-400 p-4 rounded-lg h-96 overflow-auto font-mono text-sm">
        {logs.length === 0 && !loading ? (
          <div className="text-gray-500 text-center mt-20">
            No logs yet. Run a command to see the execution logs.
          </div>
        ) : (
          logs.map((l, i) => (
            <div key={i} className="mb-2 flex items-start">
              <span className="text-gray-500 mr-3">
                [{String(i + 1).padStart(2, "0")}]
              </span>
              <span className="flex-1">{l}</span>
            </div>
          ))
        )}
        {loading && (
          <div className="text-yellow-400 animate-pulse">⏳ Processing...</div>
        )}
      </div>
    </div>
  );
}
