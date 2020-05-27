import React from 'react';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';

import {Queue} from './styles';

import QueueTable from '../../components/QueueTable';

export default ({title, handleSubmit, files, updateFiles, fileName, setFileName, url, setUrl}) => {
  return (
    <Queue>
      <p className='title'>{title}</p>

      <div className='container-add-file'>
        <TextField 
          label="File name" 
          variant="outlined" 
          size="small"
          onChange={event => setFileName(event.target.value)}
          value={fileName}
        />
        <TextField 
          label="URL" 
          variant="outlined" 
          size="small" 
          onChange={event => setUrl(event.target.value)}
          value={url}
        />
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => handleSubmit(fileName, url)}
        >
          Send
        </Button>
      </div>

      <div className='container-file-table'>
        {files ? <QueueTable data={files} updateFiles={updateFiles} /> : null}
      </div>
    </Queue>
  );
}