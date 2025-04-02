import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Drawer,
  FormHelperText,
  TextField,
} from "@mui/material";
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridToolbar,
} from "@mui/x-data-grid";
import { useQuery, gql } from "@apollo/client";
import { getStatusColor } from "../utilities/utility";
import { useState } from "react";
import LoanPayments from "./LoanPayments";
import axios from "axios";
import { Bounce, toast } from "react-toastify";

const GET_LOAN_DATA = gql`
  query {
    loans(isCombined: true) {
      id
      name
      interest_rate
      principal
      due_date
      payment_date
      status
    }
  }
`;

export default function LoanDataTable() {
  const { loading, error, data } = useQuery(GET_LOAN_DATA);
  const [isLoading, setIsLoading] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedLoan, setSelectedLoan] = useState(null);
  const [isPaymentModalOpen, setPaymentModalOpen] = useState(false);

  const columns: GridColDef[] = [
    { field: "name", headerName: "Name", width: 200 },
    {
      field: "interest_rate",
      headerName: "Interest Rate",
      width: 130,
      renderCell: (params: GridRenderCellParams) => `${params.value}%`,
    },
    {
      field: "principal",
      headerName: "Principal",
      width: 130,
      renderCell: (params: GridRenderCellParams) =>
        `$${Number(params.value).toLocaleString("en-US", {
          minimumFractionDigits: 2,
        })}`,
    },
    { field: "due_date", headerName: "Due Date", width: 140 },
    { field: "payment_date", headerName: "Payment Date", width: 140 },
    {
      field: "status",
      headerName: "Status",
      width: 130,
      renderCell: (params: GridRenderCellParams) => (
        <Chip label={params.value} color={getStatusColor(params.value)} />
      ),
    },
    {
      field: "actions",
      headerName: "Actions",
      width: 300,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <>
          <Button
            variant="outlined"
            size="small"
            color="primary"
            onClick={() => handleView(params.row)}
            sx={{ marginRight: "5px" }}
          >
            View Payments
          </Button>
          <Button
            variant="contained"
            size="small"
            color="primary"
            onClick={() => handlePayment(params.row)}
          >
            Make Payment
          </Button>
        </>
      ),
    },
  ];

  const handleView = (row: any) => {
    setSelectedLoan(row.id);
    setIsDrawerOpen(true);
  };

  const handlePayment = (row: any) => {
    setSelectedLoan(row.id);
    setPaymentModalOpen(true);
  };

  const toggleDrawer =
    (open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
      if (
        event.type === "keydown" &&
        ((event as React.KeyboardEvent).key === "Tab" ||
          (event as React.KeyboardEvent).key === "Shift")
      ) {
        return;
      }

      setIsDrawerOpen(open);
    };

  const handleMakePayment = (loan_id: string, amount: number) => {
    setIsLoading(true);

    let payment_data = {
      loan_id,
      amount,
    };

    axios
      .post(`${import.meta.env.VITE_APP_HOST_API}/make_payment`, payment_data)
      .then((res) => {
        if (res.status == 200) {
          toast.success("Payment Success", {
            position: "top-right",
            autoClose: 1200,
            hideProgressBar: false,
            closeOnClick: false,
            pauseOnHover: false,
            draggable: true,
            progress: undefined,
            theme: "light",
            transition: Bounce,
            onClose() {
              location.reload();
            },
          });
          setIsLoading(false);
        }
      })
      .catch((e) => {
        console.log(e);
        toast.error("Payment Failed, Kindly try again", {
          position: "top-right",
          autoClose: 1200,
          hideProgressBar: false,
          closeOnClick: false,
          pauseOnHover: false,
          draggable: true,
          progress: undefined,
          theme: "light",
          transition: Bounce,
        });
        setIsLoading(false);
      });
  };

  if (error)
    return (
      <Box sx={{ p: 4 }}>
        <DataGrid
          rows={[]}
          columns={columns}
          slotProps={{
            loadingOverlay: {
              variant: "skeleton",
              noRowsVariant: "skeleton",
            },
          }}
        />
      </Box>
    );

  return (
    <Container>
      <DataGrid
        rows={data?.loans}
        columns={columns}
        loading={loading}
        initialState={{
          pagination: {
            paginationModel: { pageSize: 5, page: 0 },
          },
        }}
        pageSizeOptions={[5, 10, 25]} 
        pagination
        slots={{ toolbar: GridToolbar }}
        slotProps={{
          toolbar: {
            showQuickFilter: true,
          },
        }}
      />
      <Drawer anchor="right" open={isDrawerOpen} onClose={toggleDrawer(false)}>
        {selectedLoan !== null ? (
          <LoanPayments ontoggleDrawer={toggleDrawer} loanId={selectedLoan} />
        ) : (
          <p>Select a loan to view details</p>
        )}
      </Drawer>
      {selectedLoan &&
        (isLoading ? (
          // handle view if the payment is submitting
          <Dialog open={true} maxWidth="sm" fullWidth>
            <DialogTitle>Payment processing.. Kindly wait!</DialogTitle>

            <DialogContent>
              <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
                <CircularProgress />
              </Box>
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 2 }}>
              <Button
                onClick={() => setPaymentModalOpen(false)}
                color="inherit"
              >
                Cancel
              </Button>
              <Button
                onClick={() => {}}
                variant="contained"
                color="primary"
                disabled={true}
              >
                Make Payment
              </Button>
            </DialogActions>
          </Dialog>
        ) : (
          // Else show payment modal 
          <PaymentModal
            open={isPaymentModalOpen}
            onClose={() => setPaymentModalOpen(false)}
            loanId={selectedLoan}
            onMakePayment={handleMakePayment}
          />
        ))}
    </Container>
  );
}

interface PaymentModalProps {
  open: boolean;
  onClose: () => void;
  loanId: string;
  onMakePayment: (loan_id: string, amount: number) => void;
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  open,
  onClose,
  loanId,
  onMakePayment,
}) => {
  const [amount, setAmount] = useState<number>(1);
  const [error, setError] = useState<string>("");

  const handleAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(event.target.value);
    setAmount(value);

    if (error) setError("");
  };

  const handleSubmit = () => {
    if (!amount) {
      setError("Please enter a valid amount");
      return;
    }

    // Call the parent payment function
    onMakePayment(loanId, amount);

    setAmount(1);
    setError("");

    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Make a Payment</DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ mb: 2 }}>
          Enter the amount you would like to pay towards your loan.
        </DialogContentText>

        <Box sx={{ mt: 2 }}>
          <TextField
            type="number"
            inputProps={{
              min: "1",
              step: "1",
            }}
            value={amount}
            onChange={handleAmountChange}
            placeholder="1"
            fullWidth
            label="Payment Amount"
            variant="outlined"
            error={!!error}
          />
          {error && <FormHelperText error>{error}</FormHelperText>}
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} color="inherit">
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={!amount}
        >
          Make Payment
        </Button>
      </DialogActions>
    </Dialog>
  );
};
