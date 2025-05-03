import React from 'react';
import { useState, useRef, FormEvent } from 'react';
import { clsx } from 'clsx'; // For conditional classes
import { twMerge } from 'tailwind-merge'; // For merging tailwind classes
function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

// Define the structure of the API response
interface AnalysisResult {
  filename: string | null;
  summary: string;
  nationalities: string[];
}

function App() {
  const [textContent, setTextContent] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null); // Ref to clear file input

  // --- Environment Variable Access ---
  // Get the base URL from the environment variable provided by Vite/Vercel
  const backendBaseUrl = import.meta.env.VITE_API_BASE_URL;
  // --- End Environment Variable Access ---


  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type === 'text/plain' || file.name.toLowerCase().endsWith('.docx')) {
        setSelectedFile(file);
        setTextContent(''); // Clear text area if file is selected
        setError(null); // Clear previous errors
      } else {
        setError('Invalid file type. Please upload a .txt or .docx file.');
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = ''; // Reset file input visually
        }
      }
    } else {
      setSelectedFile(null);
    }
  };

  const handleTextChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTextContent(event.target.value);
    setSelectedFile(null); // Clear file if text is entered
    if (fileInputRef.current) {
      fileInputRef.current.value = ''; // Reset file input visually
    }
    setError(null); // Clear previous errors
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!textContent && !selectedFile) {
      setError('Please enter text or upload a file.');
      return;
    }

    // --- Check if the environment variable is set ---
    if (!backendBaseUrl) {
        const errorMsg = "Configuration error: The backend API URL (VITE_API_BASE_URL) is not set.";
        console.error(errorMsg);
        setError(errorMsg + " Please contact the administrator.");
        setIsLoading(false); // Ensure loading stops
        return; // Stop execution
    }
    // --- End Check ---

    // --- Construct the full URL ---
    // Append the specific endpoint to the base URL from the environment variable
    const analyzeEndpoint = `${backendBaseUrl}/analyze`;
    // console.log(`Submitting to: ${analyzeEndpoint}`); // Optional: for debugging
    // --- End Construct URL ---


    setIsLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    if (selectedFile) {
      formData.append('file_upload', selectedFile);
    } else if (textContent) {
      formData.append('text_content', textContent);
    }

    try {
      // Use the dynamically constructed endpoint URL
      const response = await fetch(analyzeEndpoint, {
        method: 'POST',
        body: formData,
        // No 'Content-Type' header needed for FormData
      });
      // --- End Use URL ---

      // Check for non-2xx status codes first
      if (!response.ok) {
        // Try parsing JSON error, fallback to status text
        const errorText = await response.text(); // Get raw response text
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
            const errorData = JSON.parse(errorText);
            // Use detail field if available (common in FastAPI/backend errors)
            errorMessage = errorData.detail || `Backend Error (${response.status}): ${errorText}`;
        } catch (parseError) {
             // If JSON parsing fails, use the raw text if it's not too long, or the status text
            errorMessage = errorText.length < 300 ? `Backend Error (${response.status}): ${errorText}` : errorMessage;
        }
        throw new Error(errorMessage);
      }

      const data: AnalysisResult = await response.json();
      setResult(data);

    } catch (err: any) {
      console.error('Analysis fetch/processing error:', err);
      // Display a more user-friendly message for network errors vs backend errors
      if (err instanceof TypeError && err.message === 'Failed to fetch') {
           setError('Network error: Could not reach the analysis service. Please check your connection or contact support.');
      } else {
           setError(err.message || 'Failed to analyze the article. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // --- JSX for the component ---
  // (Keep the existing return statement with the form and results display)
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-3xl space-y-8">
        {/* Heading */}
        <div>
          <h1 className="text-center text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            AI News Analyzer
          </h1>
          <p className="mt-4 text-center text-lg text-gray-600">
            Get a summary and mentioned nationalities from your news article.
          </p>
        </div>

        {/* Form */}
        <form className="mt-8 space-y-6 rounded-lg bg-white p-8 shadow-lg" onSubmit={handleSubmit}>
          {/* Input Area */}
          <div className="space-y-4">
            <div>
              <label htmlFor="text-content" className="block text-sm font-medium text-gray-700">
                Paste Article Text:
              </label>
              <textarea
                id="text-content"
                rows={10}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm disabled:bg-gray-50 disabled:cursor-not-allowed"
                placeholder="Enter your news article content here..."
                value={textContent}
                onChange={handleTextChange}
                disabled={isLoading}
              />
            </div>

            <div className="relative flex items-center">
              <div className="flex-grow border-t border-gray-300"></div>
              <span className="mx-4 flex-shrink text-sm text-gray-500">OR</span>
              <div className="flex-grow border-t border-gray-300"></div>
            </div>

            <div>
              <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700">
                Upload a File (.txt or .docx):
              </label>
              <input
                id="file-upload"
                ref={fileInputRef}
                type="file"
                accept=".txt,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:rounded-md file:border-0 file:bg-primary-50 file:py-2 file:px-4 file:text-sm file:font-semibold file:text-primary-700 hover:file:bg-primary-100 disabled:opacity-50 disabled:cursor-not-allowed"
                onChange={handleFileChange}
                disabled={isLoading}
              />
              {selectedFile && (
                <p className="mt-1 text-xs text-gray-600">Selected: {selectedFile.name}</p>
              )}
            </div>
          </div>

          {/* Submit Button & Loading/Error */}
          <div>
            <button
              type="submit"
              disabled={isLoading || (!textContent && !selectedFile)}
              className={cn(
                'group relative flex w-full justify-center rounded-md border border-transparent bg-primary-600 py-2 px-4 text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors duration-150 ease-in-out',
                isLoading
                  ? 'cursor-wait bg-primary-400' // Use cursor-wait for loading
                  : 'hover:bg-primary-700',
                !isLoading && (!textContent && !selectedFile) // Only apply disabled style if not loading
                  ? 'cursor-not-allowed bg-gray-300 hover:bg-gray-300 text-gray-500'
                  : ''
              )}
            >
              {isLoading ? (
                <>
                  <svg
                    className="-ml-1 mr-3 h-5 w-5 animate-spin text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                'Analyze Article'
              )}
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    {/* Break long error messages */}
                    <p className="break-words">{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </form>

        {/* Results Area */}
        {result && !isLoading && (
          <div className="mt-8 space-y-6 rounded-lg bg-white p-8 shadow-lg animate-fade-in"> {/* Optional: Add a fade-in animation */}
            <h2 className="text-2xl font-semibold text-gray-900">Analysis Results</h2>
            {result.filename && (
              <p className="text-sm text-gray-500">Analysis for file: {result.filename}</p>
            )}

            <div>
              <h3 className="text-lg font-medium text-gray-800">Summary:</h3>
              <p className="mt-2 text-base text-gray-600">{result.summary}</p>
            </div>

            <div>
              <h3 className="text-lg font-medium text-gray-800">Mentioned Nationalities/Countries:</h3>
              {result.nationalities.length > 0 ? (
                <ul className="mt-2 list-disc space-y-1 pl-5 text-base text-gray-600">
                  {result.nationalities.map((nat, index) => (
                    <li key={index}>{nat}</li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-base text-gray-600">None found.</p>
              )}
            </div>
          </div>
        )}
      </div>
       {/* Simple Footer Example */}
       <footer className="mt-12 text-center text-sm text-gray-500">
            Powered by AI | HTX {new Date().getFullYear()}
       </footer>
    </div>
  );
}

export default App;
