import React, { useEffect, useState } from 'react';

import {Main, Wrapper, Card} from '../../constants/StyledComponents';

import Queue from '../../components/Queue';
import Snackbar from '../../components/Snackbar';

import api from '../../services/api'

export default () => {
  const [files, setFiles] = useState(null)
  
  const [fileName, setFileName] = useState('');
  const [url, setUrl] = useState('');

  const [openSnackbar, setOpenSnackbar] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState(false)
  const [type, setType] = useState('')

  useEffect(() => {
    (async () => await updateFiles())()
  }, [])

  async function updateFiles() {
    const {data} = await api.get('/files');
    setFiles(data);
  }

  async function handleSubmit(filename, url) {
    const _data = {filename, url};
    let _message, _type = ''

    if (_data.filename && _data.url){
      try {
        await api.post('/files', _data)
        _message = 'The file is being created'
        _type = 'success'
        setFileName('')
        setUrl('')
      } catch (error) {
        const {status} = {...error}.response
        _message = status === 406 ? 'The URL must contain a CSV' 
        : status === 409 ? 'The file name is already registered' : status
        _type = 'error'
      }
    } else {
      _message = `Enter the ${filename ? 'URL' : 'file name'}`
      _type = 'warning'
    }

    setSnackbarMessage(_message)
    setType(_type)
    setOpenSnackbar(true)

    await updateFiles();
  }

  return (
    <Main>
      <Snackbar 
        open={openSnackbar} 
        setOpen={setOpenSnackbar} 
        message={snackbarMessage}
        type={type}
      />

      <Wrapper>
        <Card margin={'64px 0'}>
          <Queue 
            title={'Data'} 
            handleSubmit={handleSubmit} 
            files={files}
            updateFiles={updateFiles}
            fileName={fileName}
            setFileName={setFileName}
            url={url}
            setUrl={setUrl}
          />
        </Card>
      </Wrapper>
    </Main>
  );
}