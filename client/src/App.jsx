import { useState, useEffect } from "react";
import { fetchKnowledgeItems, ingestContent } from "./api/knowledge";
import { submitQuery } from "./api/query";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/Chat";
import Modal from "./components/Modal";
import Button, { PrimaryButton } from "./components/Button";

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

export default function App() {
  const [items, setItems] = useState([]);
  const [isLoadingInitial, setIsLoadingInitial] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [itemsError, setItemsError] = useState(null);

  const [isIngestModalOpen, setIsIngestModalOpen] = useState(false);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isQuerying, setIsQuerying] = useState(false);

  // Initialize theme based on system preference if no explicit choice was saved
  const [theme, setTheme] = useState(() => {
    if (
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      return "dark";
    }
    return "light";
  });

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  // Initial load or refresh
  const loadInitialItems = async () => {
    setIsLoadingInitial(true);
    setItemsError(null);
    try {
      const response = await fetchKnowledgeItems(1, 25);
      setItems(response.data || []);
      setPage(1);
      const totalPages = response.pagination?.total_pages || 1;
      setHasMore(1 < totalPages);
    } catch (err) {
      setItemsError(err.message);
    } finally {
      setIsLoadingInitial(false);
    }
  };

  // Load next page on infinite scroll
  const loadMoreItems = async () => {
    if (isLoadingMore || !hasMore) return;
    setIsLoadingMore(true);
    const nextPage = page + 1;
    try {
      const response = await fetchKnowledgeItems(nextPage, 25);
      const newItems = response.data || [];
      setItems((prev) => [...prev, ...newItems]);
      setPage(nextPage);
      const totalPages = response.pagination?.total_pages || nextPage;
      if (nextPage >= totalPages || newItems.length === 0) {
        setHasMore(false);
      }
    } catch (err) {
      setItemsError(err.message);
    } finally {
      setIsLoadingMore(false);
    }
  };

  useEffect(() => {
    loadInitialItems();
  }, []);

  // Poll only if there are pending items
  useEffect(() => {
    const hasPending = items.some((item) =>
      ["pending", "processing", "queued"].includes(
        String(item.status).toLowerCase(),
      ),
    );
    if (!hasPending) return;

    const interval = setInterval(loadInitialItems, 4000);
    return () => clearInterval(interval);
  }, [items]);

  const handleIngestSuccess = (response) => {
    const newItem = response.data || response;
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

  const hasNoSources = !isLoadingInitial && items.length === 0;

  return (
    <div
      className={`bg-background text-text h-screen flex overflow-hidden relative ${theme}`}
    >
      <AddKnowledgeModal
        isOpen={isIngestModalOpen}
        onClose={() => setIsIngestModalOpen(false)}
        onIngestSuccess={handleIngestSuccess}
      />

      <Sidebar
        items={items}
        isLoadingInitial={isLoadingInitial}
        isLoadingMore={isLoadingMore}
        hasMore={hasMore}
        error={itemsError}
        onRefresh={loadInitialItems}
        onOpenAddModal={() => setIsIngestModalOpen(true)}
        onLoadMore={loadMoreItems}
      />

      <ChatArea
        messages={messages}
        isQuerying={isQuerying}
        question={question}
        setQuestion={setQuestion}
        onAsk={handleAsk}
        isDisabled={hasNoSources}
      />

      <Button
        className={
          "absolute top-1 right-1 border border-highlight/50 p-1 rounded-full hover:border-highlight hover:bg-element transition-colors"
        }
        onClick={toggleTheme}
      >
        {theme == "light" ? <>🌙</> : <>☀️</>}
      </Button>
    </div>
  );
}
