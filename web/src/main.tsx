import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ApolloClient, InMemoryCache, ApolloProvider } from "@apollo/client";
import "./index.css";
import App from "./App.tsx";
import { ToastContainer } from "react-toastify";

const client = new ApolloClient({
  uri: `${import.meta.env.VITE_APP_HOST_API}/graphql`,
  cache: new InMemoryCache(),
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ApolloProvider client={client}>
      {/* Toast Alert container */}
      <ToastContainer position="top-right" />
      <App />
    </ApolloProvider>
  </StrictMode>
);
