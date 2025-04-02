import LoanDataTable from "./components/LoanDataTable";
import Dashboard from "./Layouts/Dashboard";

function App() {
  return (
    // Main layout
    <Dashboard> 
      <LoanDataTable />
    </Dashboard>
  );
}

export default App;
