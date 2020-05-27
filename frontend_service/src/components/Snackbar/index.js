import React from 'react';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';

function Alert(props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

export default ({open, setOpen, message, type}) => {
  const vertical = 'bottom'
  const horizontal = 'right'

  function handleClose() {
    setOpen(false)
  };

  return (
    <div>
      <Snackbar
        anchorOrigin={{ vertical, horizontal }}
        open={open}
        autoHideDuration={5000}
        onClose={handleClose}
      >
        <Alert 
          onClose={handleClose} 
          severity={type}
        >
          {message}
        </Alert>
      </ Snackbar>
    </div>
  );
}