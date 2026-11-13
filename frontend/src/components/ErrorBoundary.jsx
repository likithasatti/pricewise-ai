import React from "react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  handleReload = () => {
    window.location.href = "/";
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#0B0F19",
          color: "#F3F4F6",
          fontFamily: "system-ui, -apple-system, sans-serif",
          padding: "20px",
          textAlign: "center"
        }}>
          <div style={{
            maxWidth: "480px",
            backgroundColor: "#111827",
            padding: "32px",
            borderRadius: "16px",
            border: "1px solid #1F2937",
            boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5)"
          }}>
            <h1 style={{ fontSize: "24px", fontWeight: "700", marginBottom: "12px", color: "#F9FAFB" }}>
              PriceWise AI
            </h1>
            <p style={{ color: "#9CA3AF", fontSize: "14px", marginBottom: "24px", lineHeight: "1.5" }}>
              Something unexpected happened while rendering the page. Click below to refresh and return home.
            </p>
            <button
              onClick={this.handleReload}
              style={{
                backgroundColor: "#2563EB",
                color: "#FFFFFF",
                fontWeight: "600",
                fontSize: "14px",
                padding: "10px 24px",
                borderRadius: "8px",
                border: "none",
                cursor: "pointer",
                transition: "background 0.2s ease"
              }}
              onMouseOver={(e) => (e.target.style.backgroundColor = "#1D4ED8")}
              onMouseOut={(e) => (e.target.style.backgroundColor = "#2563EB")}
            >
              Refresh Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
