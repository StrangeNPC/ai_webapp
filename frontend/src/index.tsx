import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './assets/styles.css'

const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error("Failed to find the root element with ID 'root'")
}

// Use createRoot for React 18+
const root = ReactDOM.createRoot(rootElement)

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)