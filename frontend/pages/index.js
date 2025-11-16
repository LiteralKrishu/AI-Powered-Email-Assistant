// Frontend UI removed in favor of Streamlit dashboard

export default function Home() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Frontend deprecated</h1>
      <p>The React/Next frontend has been deprecated in favor of the Streamlit dashboard.
      Please run the FastAPI backend and then start the dashboard with:</p>
      <pre style={{ background: '#f5f5f5', padding: '1rem' }}>streamlit run streamlit_app.py</pre>
    </div>
  )
}
