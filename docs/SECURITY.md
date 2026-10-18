# Security considerations

The offline MVP requires no secrets, credentials, or user accounts. Do not add tokens directly to source files. If an external API is integrated, store credentials in environment variables or Streamlit secrets, set request timeouts, and respect provider rate limits.

Do not collect personally identifiable information without a clear need and privacy plan.
