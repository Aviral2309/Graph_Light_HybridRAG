import {
  useEffect,
  useRef,
  useState,
} from "react";


/* ------------------------------------------------------------------ */
/* Chat Panel Component                                               */
/* ------------------------------------------------------------------ */

export default function ChatPanel({
  onQueryResult,
}) {

  /* ---------------------------------------------------------------- */
  /* State                                                            */
  /* ---------------------------------------------------------------- */

  // Chat history
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Knowledge graph loaded. Ask me anything about the documents you ingested.",
    },
  ]);

  // Current textarea value
  const [input, setInput] = useState("");

  // API loading state
  const [loading, setLoading] = useState(false);

  // Auto-scroll reference
  const messagesEndRef = useRef(null);


  /* ---------------------------------------------------------------- */
  /* Auto Scroll on New Message                                       */
  /* ---------------------------------------------------------------- */

  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages]);


  /* ---------------------------------------------------------------- */
  /* Send Message                                                     */
  /* ---------------------------------------------------------------- */

  async function sendMessage() {

    const question = input.trim();

    // Prevent empty requests
    if (!question || loading) {
      return;
    }

    // --------------------------------------------------------------
    // Add user message immediately
    // --------------------------------------------------------------
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: question,
      },
    ]);

    setInput("");

    setLoading(true);

    try {

      // ------------------------------------------------------------
      // Query backend
      // ------------------------------------------------------------
      const response = await fetch(
        "/api/query",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            question,
          }),
        }
      );

      // ------------------------------------------------------------
      // Handle API errors
      // ------------------------------------------------------------
      if (!response.ok) {

        const errorData = await response.json();

        throw new Error(
          errorData.detail || "Query failed"
        );
      }

      const data = await response.json();

      // ------------------------------------------------------------
      // Add assistant response
      // ------------------------------------------------------------
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);

      // ------------------------------------------------------------
      // Send subgraph to parent component
      // Used for highlighting graph nodes
      // ------------------------------------------------------------
      if (onQueryResult && data.subgraph) {

        onQueryResult(data.subgraph);
      }

    } catch (error) {

      // ------------------------------------------------------------
      // Error message in chat
      // ------------------------------------------------------------
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${error.message}`,
        },
      ]);

    } finally {

      setLoading(false);
    }
  }


  /* ---------------------------------------------------------------- */
  /* Handle Enter Key                                                 */
  /* ---------------------------------------------------------------- */

  function handleKeyDown(event) {

    // Enter = send
    // Shift + Enter = newline
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendMessage();
    }
  }


  /* ---------------------------------------------------------------- */
  /* Render                                                           */
  /* ---------------------------------------------------------------- */

  return (
    <div style={styles.panel}>

      {/* ------------------------------------------------------------ */}
      {/* Header                                                       */}
      {/* ------------------------------------------------------------ */}

      <div style={styles.header}>

        <h2 style={styles.title}>
          Chat with Your Graph
        </h2>

      </div>


      {/* ------------------------------------------------------------ */}
      {/* Messages                                                     */}
      {/* ------------------------------------------------------------ */}

      <div style={styles.messageList}>

        {messages.map((message, index) => (

          <div
            key={index}
            style={{
              ...styles.message,

              ...(message.role === "user"
                ? styles.userMessage
                : styles.assistantMessage),
            }}
          >

            <div style={styles.roleBadge}>

              {message.role === "user"
                ? "You"
                : "Graph"}

            </div>

            <p style={styles.messageContent}>
              {message.content}
            </p>

          </div>
        ))}


        {/* ---------------------------------------------------------- */}
        {/* Loading Message                                            */}
        {/* ---------------------------------------------------------- */}

        {loading && (

          <div
            style={{
              ...styles.message,
              ...styles.assistantMessage,
            }}
          >

            <div style={styles.roleBadge}>
              Graph
            </div>

            <p
              style={{
                ...styles.messageContent,
                color: "#94a3b8",
              }}
            >
              Searching knowledge graph...
            </p>

          </div>
        )}


        {/* ---------------------------------------------------------- */}
        {/* Auto Scroll Anchor                                         */}
        {/* ---------------------------------------------------------- */}

        <div ref={messagesEndRef} />

      </div>


      {/* ------------------------------------------------------------ */}
      {/* Input Area                                                   */}
      {/* ------------------------------------------------------------ */}

      <div style={styles.inputRow}>

        <textarea
          style={styles.input}
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          rows={2}
          disabled={loading}
        />

        <button
          style={{
            ...styles.sendButton,

            opacity:
              loading || !input.trim()
                ? 0.5
                : 1,

            cursor:
              loading || !input.trim()
                ? "not-allowed"
                : "pointer",
          }}
          onClick={sendMessage}
          disabled={
            loading || !input.trim()
          }
        >
          Send
        </button>

      </div>

    </div>
  );
}


/* ------------------------------------------------------------------ */
/* Styles                                                             */
/* ------------------------------------------------------------------ */

const styles = {

  panel: {
    display: "flex",
    flexDirection: "column",
    height: "100%",
    background: "#1e293b",
    borderRadius: "8px",
    overflow: "hidden",
  },

  header: {
    padding: "16px 20px",
    borderBottom: "1px solid #334155",
  },

  title: {
    margin: 0,
    fontSize: 16,
    fontWeight: 600,
    color: "#f1f5f9",
  },

  messageList: {
    flex: 1,
    overflowY: "auto",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },

  message: {
    borderRadius: "8px",
    padding: "12px 14px",
    maxWidth: "90%",
  },

  userMessage: {
    background: "#3b82f6",
    alignSelf: "flex-end",
  },

  assistantMessage: {
    background: "#0f172a",
    border: "1px solid #334155",
    alignSelf: "flex-start",
  },

  roleBadge: {
    fontSize: 11,
    fontWeight: 600,
    color: "#94a3b8",
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },

  messageContent: {
    margin: 0,
    color: "#e2e8f0",
    fontSize: 14,
    lineHeight: 1.6,
    whiteSpace: "pre-wrap",
  },

  inputRow: {
    display: "flex",
    gap: 8,
    padding: "12px 16px",
    borderTop: "1px solid #334155",
  },

  input: {
    flex: 1,
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "6px",
    color: "#f1f5f9",
    padding: "10px 12px",
    fontSize: 14,
    resize: "none",
    outline: "none",
    fontFamily: "inherit",
  },

  sendButton: {
    background: "#3b82f6",
    color: "white",
    border: "none",
    borderRadius: "6px",
    padding: "0 20px",
    fontSize: 14,
    fontWeight: 600,
    alignSelf: "flex-end",
    height: 40,
  },
};