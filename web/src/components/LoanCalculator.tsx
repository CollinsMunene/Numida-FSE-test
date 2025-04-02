import { useEffect, useState } from "react";
import { getMonthsUntilDue } from "../utilities/utility";

// Added this prop defination to ensure data is passed in a specific data type
interface LoanCalculatorProps {
  principal: number;
  rate: number;
  dueDate: string;
}

// SECTION 4 Debugging & Code Refactoring
export const LoanCalculator: React.FC<LoanCalculatorProps> = ({
  principal,
  rate,
  dueDate,
}) => {
  // Because we have due date, let's use it to get the months
  const months = getMonthsUntilDue(dueDate);

  const [interest, setInterest] = useState(0);

  useEffect(() => {
    setInterest((principal * rate * months) / 100);
  }, [principal, rate, months]);

  return (
    <div>
      {/* If no interest then ideally the due date is past */}
      {interest > 0 ? <h3>Loan Interest: {interest} </h3> : "Due date passed"}
    </div>
  );
};
