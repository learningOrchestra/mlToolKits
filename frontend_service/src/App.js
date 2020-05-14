import React from 'react';
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createMuiTheme } from '@material-ui/core/styles'


import Router from './router'

import Nav from './components/Nav'

export default () => {
  const theme = createMuiTheme({
    palette: {primary: {main: '#2196F3'}}
  });


  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <Nav />
        <Router />
      </BrowserRouter>
    </ThemeProvider>
  );
}