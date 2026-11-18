import { useRef, useEffect } from "react";
import { PrimaryButton } from "./Button";

export default function ChatArea({ messages, isQuerying, question, setQuestion, onAsk, isDisabled }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isQuerying]);

  return (
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

                const answerText = msg.rawResult?.answer || (typeof msg.rawResult === "string" ? msg.rawResult : null);
                const sources = msg.rawResult?.sources || [];

                return (
                  <div
                    key={msg.id}
                    className="p-4 rounded-2xl bg-foreground/50 border border-highlight/30 text-sm flex flex-col gap-3"
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">
                      {answerText || JSON.stringify(msg.rawResult, null, 2)}
                    </p>

                    {sources.length > 0 && (
                      <div className="border-t border-highlight/30 pt-2.5 flex flex-col gap-1.5">
                        <span className="text-[10px] font-semibold uppercase tracking-wider opacity-60">
                          Sources
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="text-xs bg-background/80 border border-highlight/40 rounded-lg px-2.5 py-1 flex items-center gap-1.5"
                              title={source.snippet}
                            >
                              <span className="font-semibold opacity-70">
                                [{idx + 1}]
                              </span>
                              <span className="truncate font-medium">
                                {source.title || `Content #${source.content_id}`}
                              </span>
                              <span className="opacity-40 text-[10px]">
                                ({Math.round((source.relevance_score || 0) * 100)}%)
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
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

      {/* Sticky Input Bar */}
      <div className="p-4 bg-background/80 backdrop-blur-sm">
        <form
          onSubmit={onAsk}
          className="p-2 px-3 flex items-center gap-2 border border-highlight bg-foreground w-full max-w-xl m-auto rounded-full sticky bottom-0 left-0 right-0"
        >
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={isQuerying || isDisabled}
            className="outline-none flex-1 bg-transparent text-sm px-2 disabled:opacity-50"
            placeholder="Ask..."
          />
          <PrimaryButton
            type="submit"
            disabled={isQuerying || !question.trim() || isDisabled}
            className="font-medium text-sm py-1 px-3.5"
          >
            {isQuerying ? "..." : "Ask"}
          </PrimaryButton>
        </form>
      </div>
    </main>
  );
}
