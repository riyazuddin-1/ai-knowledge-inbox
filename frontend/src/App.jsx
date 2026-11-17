import { useState, useEffect, useRef } from "react";
import Modal from "./components/modal";
import Button, { PrimaryButton } from "./components/button";
import { fetchKnowledgeItems, ingestContent } from "./api/knowledge";
import { submitQuery } from "./api/query";

function AddKnowledgeModal({ isOpen, onClose, onIngestSuccess }) {
  const [ingestType, setIngestType] = useState("url");
  const [ingestData, setIngestData] = useState("");
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestError, setIngestError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ingestData.trim() || isIngesting) return;

    setIsIngesting(true);
    setIngestError(null);

    try {
      const newItem = await ingestContent(ingestType, ingestData.trim());
      onIngestSuccess(newItem);
      setIngestData("");
      onClose();
    } catch (err) {
      setIngestError(err.message);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <Modal title="Add Knowledge" onClose={onClose}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
        <div className="flex flex-col gap-1.5">
          <label className="text-xs uppercase tracking-wider opacity-70 font-medium">
            Content Type
          </label>
          <select
            value={ingestType}
            onChange={(e) => setIngestType(e.target.value)}
            className="bg-background border border-highlight rounded-lg px-3 py-2 text-sm outline-none"
          >
            <option value="url">URL</option>
            <option value="text">Text</option>
            <option value="youtube">YouTube</option>
            <option value="pdf">PDF</option>
          </select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs uppercase tracking-wider opacity-70 font-medium">
            {ingestType === "text" ? "Content" : "Source"}
          </label>
          {ingestType === "text" ? (
            <textarea
              rows={5}
              autoFocus
              value={ingestData}
              onChange={(e) => setIngestData(e.target.value)}
              placeholder="Paste text content..."
              className="bg-background border border-highlight rounded-lg px-3 py-2 text-sm outline-none resize-none"
            />
          ) : (
            <input
              type="text"
              autoFocus
              value={ingestData}
              onChange={(e) => setIngestData(e.target.value)}
              placeholder={`Enter ${ingestType}...`}
              className="bg-background border border-highlight rounded-lg px-3 py-2 text-sm outline-none"
            />
          )}
        </div>

        {ingestError && (
          <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">
            {ingestError}
          </p>
        )}

        <div className="flex items-center justify-end gap-2 pt-2">
          <Button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-full text-sm border border-highlight/60 opacity-80 hover:opacity-100 hover:border-highlight"
          >
            Cancel
          </Button>
          <PrimaryButton
            type="submit"
            disabled={isIngesting || !ingestData.trim()}
            className="text-sm font-medium py-1.5 px-4"
          >
            {isIngesting ? "Ingesting..." : "Ingest"}
          </PrimaryButton>
        </div>
      </form>
    </Modal>
  );
}

function App() {
  const [items, setItems] = useState([]);
  const [isLoadingItems, setIsLoadingItems] = useState(true);
  const [itemsError, setItemsError] = useState(null);

  const [isIngestModalOpen, setIsIngestModalOpen] = useState(false);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isQuerying, setIsQuerying] = useState(false);

  const messagesEndRef = useRef(null);

  const loadItems = async (pageNumber = 1) => {
    setIsLoadingItems(true);
    setItemsError(null);
    try {
      const response = await fetchKnowledgeItems(pageNumber, 25);
      setItems(response.data || response);
    } catch (err) {
      setItemsError(err.message);
    } finally {
      setIsLoadingItems(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  useEffect(() => {
    const hasPending = items.some((item) =>
      ["pending", "processing", "queued"].includes(
        String(item.status).toLowerCase(),
      ),
    );
    if (!hasPending) return;

    const interval = setInterval(loadItems, 4000);
    return () => clearInterval(interval);
  }, [items]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isQuerying]);

  const handleIngestSuccess = (newItem) => {
    setItems((prev) => [newItem, ...prev]);
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || isQuerying) return;

    const userMsg = { id: Date.now(), role: "user", content: trimmedQuestion };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setIsQuerying(true);

    try {
      const result = await submitQuery(trimmedQuestion);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "assistant", rawResult: result },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "error", content: err.message },
      ]);
    } finally {
      setIsQuerying(false);
    }
  };

  const getStatusBadgeStyle = (status) => {
    const s = String(status).toLowerCase();
    if (s === "completed" || s === "ready" || s === "indexed") {
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    }
    if (s === "failed" || s === "error") {
      return "bg-red-500/15 text-red-400 border-red-500/30";
    }
    return "bg-amber-500/15 text-amber-400 border-amber-500/30";
  };

  const hasNoSources = !isLoadingItems && items.length === 0;

  return (
    <div className="bg-background text-text h-screen flex overflow-hidden relative light">
      <AddKnowledgeModal
        isOpen={isIngestModalOpen}
        onClose={() => setIsIngestModalOpen(false)}
        onIngestSuccess={handleIngestSuccess}
      />

      {/* Full-Page Idle Cover when No Data Exists */}
      {hasNoSources && (
        <div className="absolute inset-0 z-40 bg-foreground backdrop-blur-md flex items-center justify-center p-6">
          <div className="text-center max-w-lg p-8 rounded-3xl flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-contrast/10 flex items-center justify-center mb-4 text-contrast font-bold text-xl">
              +
            </div>
            <h2 className="text-xl font-bold mb-2">
              No Knowledge Base Sources
            </h2>
            <p className="text-sm opacity-65 mb-6 leading-relaxed">
              Your knowledge base is currently empty. Ingest your first URL,
              document, or text snippet to start chatting and querying your
              data.
            </p>
            <PrimaryButton
              onClick={() => setIsIngestModalOpen(true)}
              className="font-medium text-sm py-2.5 px-6 shadow-lg"
            >
              Add Your First Source
            </PrimaryButton>
          </div>
        </div>
      )}

      {/* Sidebar: Knowledge Base Items */}
      <aside className="w-80 bg-foreground border-r border-highlight/30 flex flex-col shrink-0">
        <div className="p-4 border-b border-highlight/30 flex items-center justify-between gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wider opacity-80">
            Sources ({items.length})
          </h2>
          <div className="flex items-center gap-2">
            <Button
              onClick={loadItems}
              disabled={isLoadingItems}
              ariaLabel="Refresh list"
              className="text-xs opacity-60 hover:opacity-100"
            >
              {isLoadingItems ? "..." : "↻"}
            </Button>
            <PrimaryButton
              onClick={() => setIsIngestModalOpen(true)}
              className="font-medium text-xs py-1 px-2.5"
            >
              + Add
            </PrimaryButton>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {itemsError && (
            <p className="text-xs text-red-400 mb-2">{itemsError}</p>
          )}

          {items.map((item) => (
            <div
              key={item.id}
              className="p-2.5 rounded-lg bg-background/60 border border-highlight/40 flex flex-col gap-1"
            >
              <div className="flex items-start justify-between gap-2">
                <span
                  className="text-sm font-medium truncate"
                  title={item.title || item.source || `Item #${item.id}`}
                >
                  {item.title || item.source || `Untitled #${item.id}`}
                </span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded border shrink-0 uppercase font-semibold ${getStatusBadgeStyle(
                    item.status,
                  )}`}
                >
                  {item.status}
                </span>
              </div>
              <div className="flex items-center justify-between text-[11px] opacity-60">
                <span className="uppercase">{item.type}</span>
                <span>{new Date(item.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex flex-col w-full h-full relative">
        <div className="result flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto h-full flex flex-col">
            {messages.length === 0 ? (
              <div className="flex-1 flex items-center justify-center">
                <p className="opacity-40 text-sm">
                  Ask a question about your ingested content
                </p>
              </div>
            ) : (
              <div className="space-y-4 pb-6">
                {messages.map((msg) => {
                  if (msg.role === "user") {
                    return (
                      <div key={msg.id} className="flex justify-end">
                        <div className="bg-foreground border border-highlight/50 px-4 py-2.5 rounded-2xl max-w-xl text-sm">
                          {msg.content}
                        </div>
                      </div>
                    );
                  }

                  if (msg.role === "error") {
                    return (
                      <div
                        key={msg.id}
                        className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm"
                      >
                        {msg.content}
                      </div>
                    );
                  }

                  return (
                    <div
                      key={msg.id}
                      className="p-4 rounded-2xl bg-foreground/50 border border-highlight/30 text-sm"
                    >
                      {typeof msg.rawResult === "string" ? (
                        <p className="whitespace-pre-wrap">{msg.rawResult}</p>
                      ) : (
                        <pre className="text-xs overflow-x-auto whitespace-pre-wrap font-mono opacity-90">
                          {JSON.stringify(msg.rawResult, null, 2)}
                        </pre>
                      )}
                    </div>
                  );
                })}

                {isQuerying && (
                  <div className="p-4 rounded-2xl bg-foreground/30 border border-highlight/20 text-sm opacity-70 animate-pulse w-fit">
                    Searching knowledge base...
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Sticky Ask Input Bar */}
        <div className="p-4 bg-background/80 backdrop-blur-sm">
          <form
            onSubmit={handleAsk}
            className="p-2 px-3 flex items-center gap-2 border border-highlight bg-foreground w-full max-w-xl m-auto rounded-full sticky bottom-0 left-0 right-0"
          >
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={isQuerying || hasNoSources}
              className="outline-none flex-1 bg-transparent text-sm px-2 disabled:opacity-50"
              placeholder="Ask..."
            />
            <PrimaryButton
              type="submit"
              disabled={isQuerying || !question.trim() || hasNoSources}
              className="font-medium text-sm py-1 px-3.5"
            >
              {isQuerying ? "..." : "Ask"}
            </PrimaryButton>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
