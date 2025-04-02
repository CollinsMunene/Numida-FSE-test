// Utility to return the relevant loan color wrapper status based on payment status
export const getStatusColor = (status: string) => {
  switch (status) {
    case "On Time":
      return "success";
    case "Late":
      return "warning";
    case "Defaulted":
      return "error";
    default:
      return "default";
  }
};

// Utility to calculate the total months based on the loan due date and the current date. If date is passed let's just set it to 0 for now
export const getMonthsUntilDue = (dueDate: string): number => {
  const today = new Date();
  const due = new Date(dueDate);

  const yearsDiff = due.getFullYear() - today.getFullYear();
  const monthsDiff = due.getMonth() - today.getMonth();
  let totalMonths = yearsDiff * 12 + monthsDiff;

  return totalMonths < 0 ? 0 : totalMonths;
};
