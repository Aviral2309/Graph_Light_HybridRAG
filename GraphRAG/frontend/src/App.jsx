import { useState } from "react";

import ChatPanel from "./ChatPanel";
import GraphView from "./GraphView";


/* ------------------------------------------------------------------ */
/* Main App Component                                                 */
/* ------------------------------------------------------------------ */

export default function App() {

  /* ---------------------------------------------------------------- */
  /* State                                                            */
  /* ---------------------------------------------------------------- */

  // Nodes highlighted from the latest query
  const [highlightNodes, setHighlightNodes] =
    useState([]);

  // Document ingestion loading state
  const [ingesting, setIngesting] =
    useState(false);

  // Ingestion status message
  const [ingestStatus, setIngestStatus] =
    useState("");


  /* ---------------------------------------------------------------- */
  /* Run Document Ingestion                                           */
  /* ---------------------------------------------------------------- */

  async function runIngestion() {

    setIngesting(true);

    setIngestStatus(
      "Processing documents..."
    );

    try {

      // ------------------------------------------------------------
      // Call backend ingestion API
      // ------------------------------------------------------------
      const response = await fetch(
        "/api/ingest",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            folder_path: "documents",
            clear_first: true,
          }),
        }
      );

      const data =
        await response.json();

      // ------------------------------------------------------------
      // Handle API errors
      // ------------------------------------------------------------
      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Ingestion failed"
        );
      }

      // ------------------------------------------------------------
      // Success message
      // ------------------------------------------------------------
      setIngestStatus(
        `✅ Ingested ${data.entities_count} entities, ` +
        `${data.relationships_count} relationships`
      );

    } catch (error) {

      // ------------------------------------------------------------
      // Failure message
      // ------------------------------------------------------------
      setIngestStatus(
        `❌ ${error.message}`
      );

    } finally {

      setIngesting(false);
    }
  }


  /* ---------------------------------------------------------------- */
  /* Handle Query Result                                              */
  /* ---------------------------------------------------------------- */

  function handleQueryResult(subgraph) {

    // Highlight returned nodes in GraphView
    setHighlightNodes(
      subgraph.nodes || []
    );
  }


  /* ---------------------------------------------------------------- */
  /* Render                                                           */
  /* ---------------------------------------------------------------- */

  return (
    <div style={styles.app}>

      {/* ------------------------------------------------------------ */}
      {/* Top Navigation Bar                                           */}
      {/* ------------------------------------------------------------ */}

      <div style={styles.topBar}>

        {/* Brand */}
        <div style={styles.brand}>

          <span style={styles.brandIcon}>
            ◈
          </span>

          <span style={styles.brandName}>
            GraphRAG Explorer
          </span>

        </div>


        {/* Ingestion Controls */}
        <div style={styles.ingestSection}>

          {ingestStatus && (

            <span style={styles.ingestStatus}>
              {ingestStatus}
            </span>
          )}

          <button
            style={{
              ...styles.ingestButton,

              opacity: ingesting
                ? 0.6
                : 1,

              cursor: ingesting
                ? "not-allowed"
                : "pointer",
            }}
            onClick={runIngestion}
            disabled={ingesting}
          >

            {ingesting
              ? "Ingesting..."
              : "⬆ Ingest Documents"}

          </button>

        </div>

      </div>


      {/* ------------------------------------------------------------ */}
      {/* Main Content Area                                            */}
      {/* ------------------------------------------------------------ */}

      <div style={styles.content}>

        {/* Graph Panel */}
        <div style={styles.graphPane}>

          <GraphView
            highlightNodes={
              highlightNodes
            }
          />

        </div>


        {/* Chat Panel */}
        <div style={styles.chatPane}>

          <ChatPanel
            onQueryResult={
              handleQueryResult
            }
          />

        </div>

      </div>

    </div>
  );
}


/* ------------------------------------------------------------------ */
/* Styles                                                             */
/* ------------------------------------------------------------------ */

const styles = {

  app: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    background: "#0f172a",
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },

  topBar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "12px 20px",
    borderBottom: "1px solid #334155",
    background: "#1e293b",
    flexShrink: 0,
  },

  brand: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },

  brandIcon: {
    fontSize: 20,
    color: "#60a5fa",
  },

  brandName: {
    fontSize: 16,
    fontWeight: 700,
    color: "#f1f5f9",
  },

  ingestSection: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },

  ingestStatus: {
    fontSize: 13,
    color: "#94a3b8",
  },

  ingestButton: {
    background: "#3b82f6",
    color: "white",
    border: "none",
    borderRadius: "6px",
    padding: "8px 16px",
    fontSize: 13,
    fontWeight: 600,
  },

  content: {
    display: "flex",
    flex: 1,
    overflow: "hidden",
    padding: 16,
    gap: 16,
  },

  graphPane: {
    flex: 2,

    // Graph takes ~2/3 width
    minHeight: 0,
  },

  chatPane: {
    flex: 1,

    // Chat takes ~1/3 width
    minHeight: 0,
  },
};
