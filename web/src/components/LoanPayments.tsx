import { JSX } from "react";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import { gql, useQuery } from "@apollo/client";
import { Chip, CircularProgress, Typography } from "@mui/material";
import { getStatusColor } from "../utilities/utility";
import { LoanCalculator } from "./LoanCalculator";

const GET_LOAN_PAYMENTS_DATA = gql`
  query loanPayments($filters: LoanPaymentFilter) {
    loanPayments(filters: $filters) {
      id
      payment_date
      amount
      status
      loan {
        interest_rate
        principal
        due_date
      }
    }
  }
`;

interface LoanPaymentsProps {
  ontoggleDrawer: (open: boolean) => void;
  loanId: number;
}

interface Payment {
  id: string;
  status: string;
  amount: number;
  payment_date: string;
}

export default function LoanPayments({
  ontoggleDrawer,
  loanId,
}: LoanPaymentsProps): JSX.Element {
  const { loading, error, data } = useQuery(GET_LOAN_PAYMENTS_DATA, {
    variables: {
      filters: {
        loan_id: loanId,
      },
    },
  });

  if (loading)
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );

  if (error)
    return (
      <Box sx={{ p: 4 }}>
        <Typography color="error" variant="h6">
          Error loading payments: {error.message}
        </Typography>
      </Box>
    );

  return (
    <Box
      sx={{
        width: 500,
        p: 2,
        maxHeight: "100vh",
        overflow: "auto",
      }}
      role="presentation"
      onClick={() => ontoggleDrawer(false)}
    >
      <Typography variant="h6" sx={{ mb: 2 }}>
        Payment History
      </Typography>

      <Box sx={{ width: "100%" }}>
        {data?.loanPayments && data.loanPayments.length > 0 ? (
          <>
            {/* Let's use the calculator get the interest amount needs to be paid */}
            <LoanCalculator
              principal={data.loanPayments[0].loan.principal}
              rate={data.loanPayments[0].loan.interest_rate}
              dueDate={data.loanPayments[0].loan.due_date}
            />

            {/* Show total amount paid so far */}
            <Typography variant="caption" sx={{ mb: 2 }}>
              (Total paid: $
              {data.loanPayments.reduce(
                (total: number, payment: { amount: number }) =>
                  total + payment.amount,
                0
              )}
              )
            </Typography>

            {/* Map through loan payments */}
            {data.loanPayments.map((payment: Payment) => (
              <Box key={payment.id}>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    py: 2,
                  }}
                >
                  <Box
                    sx={{ display: "flex", flexDirection: "column", gap: 1 }}
                  >
                    <Chip
                      label={payment.status}
                      color={getStatusColor(payment.status)}
                      size="small"
                      sx={{
                        fontWeight: 500,
                        width: "fit-content",
                      }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Amount: ${payment.amount}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Payment Date: {payment.payment_date}
                    </Typography>
                  </Box>
                </Box>
                <Divider />
              </Box>
            ))}
          </>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No payments available.
          </Typography>
        )}
      </Box>
    </Box>
  );
}
