import React, { useEffect, useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import moment from 'moment'

import {DeleteButton} from './styles';

import {Check, Wait, Trash} from '../../components/Icons';
import Snackbar from '../../components/Snackbar';
import ModalMessage from '../../components/ModalMessage'

import api from '../../services/api'

const useStyles = makeStyles({
  root: { width: '100%' },
  container: { maxHeight: 312 },
});

export default ({ data, updateFiles }) => {
  const classes = useStyles();

  const [filename, setFilename] = useState('');

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [columns, setColumns] = useState([]);
  const [rows, setRows] = useState([]);

  const [openSnackbar, setOpenSnackbar] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState(false)
  const [type, setType] = useState('')

  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    const _columns = [
      { id: 'finished', label: 'Status', align: 'center' },
      { id: 'filename', label: 'Name' },
      { id: 'url', label: 'URL' },
      { id: 'time_created', label: 'Created', minWidth: 144 },
      { id: 'delete', label: '', align: 'left' },
    ]

    const _rows = data.result.map(value => {
      value.delete = value.finished;
      value.time_created = moment(value.time_created).fromNow()
      return value;
    })

    setColumns(_columns)
    setRows(_rows)
  }, [data])

  async function handleDeleteFile() {
    await api.delete('/files', {data: {filename}})
    setModalVisible(false)
    
    setSnackbarMessage(`The "${filename}" file has been deleted`)
    setType('info')
    setOpenSnackbar(true)

    await updateFiles()
  }

  function handleOpenDeleteModal({filename}) {
    setFilename(filename)
    setModalVisible(true)
  }

  const handleChangePage = (_, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(+event.target.value);
    setPage(0);
  };

  return (
    <>
      {
        modalVisible ?
          <ModalMessage 
            title={'Delete'} 
            message={`Do you want to delete the "${filename}" file?`} 
            setModalVisible={setModalVisible}
            handleOnConfirm={handleDeleteFile}
          />
        : null
      }

      <Paper className={classes.root}>
        <Snackbar 
          open={openSnackbar} 
          setOpen={setOpenSnackbar} 
          message={snackbarMessage}
          type={type}
        />

        <TableContainer className={classes.container}>
          <Table stickyHeader size='small'>

            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell
                    key={column.id}
                    align={column.align}
                    style={{ 
                      minWidth: column.minWidth,
                      maxWidth: column.maxWidth 
                    }}
                  >
                    {column.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>

            <TableBody>
              {rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                return (
                  <TableRow hover role="checkbox" tabIndex={-1} key={row.code}>
                    {columns.map((column) => {
                      const value = row[column.id];
                      return (
                        <TableCell key={column.id} align={column.align}>
                          {
                          column.id === 'finished' ? 
                            value ? 
                              <Check size={16} color={'green'} /> 
                            : <Wait size={18} color={'orange'} />
                          : column.id === 'delete' ? 
                            value ? 
                              <DeleteButton onClick={() => handleOpenDeleteModal(row)}>
                                <Trash size={14} color={'red'} />
                              </DeleteButton> 
                            : ''
                          : value
                          }
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableBody>

          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[10, 25, 100]}
          component="div"
          count={rows.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onChangePage={handleChangePage}
          onChangeRowsPerPage={handleChangeRowsPerPage}
        />
        
      </Paper>
    </>
  );
}